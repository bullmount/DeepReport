import cloudscraper
import threading
from typing import List, Dict, ClassVar
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import requests
from docling.backend.html_backend import HTMLDocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.document import InputDocument
from playwright.sync_api import sync_playwright, ViewportSize
import time
from threading import Lock
from requests.adapters import HTTPAdapter
import ssl
import pymupdf4llm
import os
import tempfile
from io import BytesIO
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (AcceleratorDevice, AcceleratorOptions, PdfPipelineOptions)
import logging
import fitz
from readability import Document
from markdownify import markdownify

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

MAX_WORKERS = 4
FETCH_TIMEOUT = 20

class SSLIgnoreAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


class UrlFetcher:
    _shared_cache: ClassVar[Dict[str, str]] = {}
    _cache_lock: ClassVar[Lock] = threading.Lock()
    _playwright_lock: ClassVar[Lock] = Lock()
    max_pdf_size: int = 500 * 1024

    @staticmethod
    def _fetch_pdf_fallback(url: str) -> bytes:
        temp_file_path = None
        with UrlFetcher._playwright_lock:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        temp_file_path = tmp_file.name

                    with page.expect_download(timeout=15_000) as download_info:
                        page.goto(url)
                        download = download_info.value
                        download.save_as(temp_file_path)
                    with open(temp_file_path, 'rb') as f:
                       return f.read()
                finally:
                    browser.close()
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)

    def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        try:
            buf = BytesIO(pdf_bytes)
            accelerator_options = AcceleratorOptions(num_threads=2, device=AcceleratorDevice.CUDA)
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.generate_picture_images = False
            pipeline_options.do_table_structure = True
            pipeline_options.table_structure_options.do_cell_matching = False
            pipeline_options.accelerator_options = accelerator_options
            source = DocumentStream(name="pdf_to_convert.pdf", stream=buf)
            doc_converter = DocumentConverter(
                format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options,
                                                                 backend=PyPdfiumDocumentBackend)}
            )
            result = doc_converter.convert(source, max_file_size=self.max_pdf_size)
            testo = result.document.export_to_markdown().replace("<!-- image -->\n\n", "")
            return testo.strip() if testo else "[Nessun testo estraibile dal PDF]"
        except Exception:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                return pymupdf4llm.to_markdown(doc).strip()
            except Exception as e:
                logger.error(f"Errore nel fallback PDF parsing: {str(e)}")
                return ""

    def _extract_html_text(self, url: str) -> str:
        with UrlFetcher._playwright_lock:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                               "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    viewport=ViewportSize(width=1280, height=800),
                    java_script_enabled=True,
                )
                page = context.new_page()
                try:
                    page.goto(url, wait_until="load", timeout=8000)
                    page.wait_for_load_state('networkidle', timeout=8000)
                    time.sleep(random.uniform(0.5, 1.5))
                    page.mouse.move(300, 400)
                    time.sleep(random.uniform(0.5, 1.5))
                    page.mouse.wheel(0, 500)

                    try:
                        html_content = page.inner_html("body", timeout=5000)
                    except:
                        html_content = page.content()

                    doc = Document(html_content)
                    contenuto_html = doc.summary()

                    in_doc = InputDocument(
                        path_or_stream=BytesIO(contenuto_html.encode("utf-8")),
                        format=InputFormat.HTML,
                        backend=HTMLDocumentBackend,
                        filename="page.html",
                    )
                    backend = HTMLDocumentBackend(in_doc=in_doc,
                                                  path_or_stream=BytesIO(contenuto_html.encode("utf-8")))
                    dl_doc = backend.convert()
                    markdown = dl_doc.export_to_markdown()
                    if len(markdown) == 0:
                        markdown = markdownify(contenuto_html)
                    return markdown if markdown else markdownify(contenuto_html)
                except Exception as e:
                    logger.error(f"Errore Playwright su {url}: {str(e)}")
                    return ""
                finally:
                    browser.close()

    def _fetch(self,url):
        with UrlFetcher._cache_lock:
            if url in UrlFetcher._shared_cache:
                return url, UrlFetcher._shared_cache[url]

        session = requests.Session()
        session.verify = False
        session.mount("https://", SSLIgnoreAdapter())

        try:
            head_resp = session.head(url, allow_redirects=True, timeout=10)
            content_type = head_resp.headers.get("Content-Type", "")
        except:
            content_type = ""

        try:
            if url.lower().endswith(".pdf") or "application/pdf" in content_type:
                try:
                    scraper = cloudscraper.create_scraper()  # crea un sessione che esegue JS-challenge
                    scraper.mount("https://", SSLIgnoreAdapter())
                    response = scraper.get(url, verify=False)
                    pdf_bytes = response.content
                    fitz.open(stream=pdf_bytes, filetype="pdf")  # verifica che è un pdf
                except Exception as e:
                    pdf_bytes = self._fetch_pdf_fallback(url)

                if len(pdf_bytes) >= self.max_pdf_size:
                    return url, ""

                testo = self._extract_pdf_text(pdf_bytes)
                with UrlFetcher._cache_lock:
                    UrlFetcher._shared_cache[url] = testo
                return url, testo
            else:
                markdown = self._extract_html_text(url)

                with UrlFetcher._cache_lock:
                    UrlFetcher._shared_cache[url] = markdown
                return url, markdown

        except Exception as e:
            logger.error(f"Errore generico fetch {url}: {str(e)}")
            return url, ""

    def fetch_contents(self, urls: List[str]) -> Dict[str, str]:
        contents = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {executor.submit(self._fetch, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    url, content = future.result(timeout=FETCH_TIMEOUT)
                    contents[url] = content
                except Exception as e:
                    logger.error(f"Errore fetch su {url}: {str(e)}")
                    contents[url] = ""
        return contents
