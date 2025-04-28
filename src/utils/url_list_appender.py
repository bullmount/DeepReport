import json
import threading
from typing import List

#todo: remove
class UrlListAppender:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()

    def append_url(self, url: str):
        with self._lock:
            urls = self._read_urls()
            if url not in urls:
                urls.append(url)
                with open(self.path, "w", encoding="utf-8") as file:
                    json.dump(urls, file, ensure_ascii=False, indent=2)

    def get_urls(self) -> List[str]:
        with self._lock:
            return self._read_urls()

    def _read_urls(self) -> List[str]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []