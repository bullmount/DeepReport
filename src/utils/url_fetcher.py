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
import os
import tempfile
from io import BytesIO
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (AcceleratorDevice, AcceleratorOptions, PdfPipelineOptions)
import logging
import traceback
import fitz
from readability import Document
from markdownify import markdownify

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

import io
from PyPDF2 import PdfReader, PdfWriter


# def estrai_prime_n_pagine(pdf_bytes: bytes, num_pagine:int) -> bytes:
#     reader = PdfReader(io.BytesIO(pdf_bytes))
#     if num_pagine > len(reader.pages):
#         return pdf_bytes
#
#     writer = PdfWriter()
#
#     num_pagine = min(num_pagine, len(reader.pages))
#
#     for i in range(num_pagine):
#         writer.add_page(reader.pages[i])
#
#     output_stream = io.BytesIO()
#     writer.write(output_stream)
#     return output_stream.getvalue()  # restituisce i bytes

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
    max_pdf_size: int = 500 * 1024

    @staticmethod
    def _fetch_pdf(url: str) -> bytes:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    temp_file_path = tmp_file.name

                with page.expect_download() as download_info:
                    page.goto(url)
                    download = download_info.value
                    download.save_as(temp_file_path)
                    with open(temp_file_path, 'rb') as f:
                        pdf_bytes = f.read()
                        return pdf_bytes
            finally:
                browser.close()
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    def fetch_contents(self, urls: List[str]) -> Dict[str, str]:
        contents = {}

        def fetch(url):
            with UrlFetcher._cache_lock:
                if url in UrlFetcher._shared_cache:
                    return url, UrlFetcher._shared_cache[url]

            session = requests.Session()
            session.verify = False
            session.mount("https://", SSLIgnoreAdapter())
            try:
                head_resp = session.head(url, allow_redirects=True)
                content_type = head_resp.headers.get("Content-Type", "")
            except:
                content_type = ""

            if url.lower().endswith(".pdf") or "application/pdf" in content_type:
                try:
                    scraper = cloudscraper.create_scraper()  # crea un sessione che esegue JS-challenge
                    scraper.mount("https://", SSLIgnoreAdapter())
                    response = scraper.get(url, verify=False)
                    pdf_bytes = response.content
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # verifica che è n pdf
                except Exception as e:
                    pdf_bytes = self._fetch_pdf(url)

                if len(pdf_bytes) >= self.max_pdf_size:
                    return url, ""

                # pdf_bytes = estrai_prime_n_pagine(pdf_bytes,20)
                try:
                    buf = BytesIO(pdf_bytes)
                    pipeline_options = PdfPipelineOptions()
                    pipeline_options.do_ocr = False
                    pipeline_options.generate_picture_images = False
                    pipeline_options.do_table_structure = True
                    # accelerator_options = AcceleratorOptions(num_threads=4, device=AcceleratorDevice.CUDA)
                    # pipeline_options.accelerator_options = accelerator_options
                    pipeline_options.table_structure_options.do_cell_matching = False
                    source = DocumentStream(name="pdf_to_convert.pdf", stream=buf)
                    doc_converter = DocumentConverter(
                        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options,
                                                                         backend=PyPdfiumDocumentBackend)})
                    result = doc_converter.convert(source,
                                                   # max_num_pages=20,  # todo:remove
                                                   max_file_size=self.max_pdf_size)
                    testo = result.document.export_to_markdown()
                    testo = testo.replace("<!-- image -->\n\n", "")
                    return url, testo.strip() if testo else "[Nessun testo estraibile dal PDF]"
                except Exception as e:
                    logger.error(f"Si è verificato un errore: {str(e)}")
                    # logger.error(f"Traceback completo:\n{traceback.format_exc()}")

                    # print(f"errore conversione pdf: {url}")
                    return url, ""  # "Documento PDF non convertibile"
            else:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                        viewport=ViewportSize(width=1280, height=800),  # {"width": 1280, "height": 800},
                        java_script_enabled=True,
                    )
                    page = context.new_page()
                    try:
                        page.goto(url, wait_until="networkidle", timeout=30 * 1000)  # 60 sec.
                        page.wait_for_load_state('networkidle')

                        # Sequenza di azioni che simula comportamento umano nella navigazione:
                        # pause casuali + movimento mouse + scroll naturale rendono più difficile il rilevamento come bot
                        # da parte dei sistemi anti-automazione
                        time.sleep(random.uniform(0.5, 1.5))
                        page.mouse.move(300, 400)
                        time.sleep(random.uniform(0.5, 1.5))
                        page.mouse.wheel(0, 500)

                        # html_content = page.content()
                        html_content = page.inner_html("body")

                        doc = Document(html_content)
                        contenuto_html = doc.summary()

                        in_doc = InputDocument(
                            path_or_stream=BytesIO(bytes(contenuto_html, encoding="utf-8")),
                            format=InputFormat.HTML,
                            backend=HTMLDocumentBackend,
                            filename="duck.html",
                        )
                        backend = HTMLDocumentBackend(in_doc=in_doc,
                                                      path_or_stream=BytesIO(bytes(contenuto_html, encoding="utf-8"))
                                                      )
                        dl_doc = backend.convert()
                        contenuto_markdown = dl_doc.export_to_markdown()
                        if len(contenuto_markdown) == 0:
                            contenuto_markdown = markdownify(contenuto_html)

                        with UrlFetcher._cache_lock:
                            UrlFetcher._shared_cache[url] = contenuto_markdown
                        return url, contenuto_markdown
                    except Exception as e:
                        # todo: log error
                        return url, ""
                    finally:
                        browser.close()

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url = {executor.submit(fetch, url): url for url in urls}
            for future in as_completed(future_to_url):
                url, content = future.result()
                contents[url] = content

        return contents
