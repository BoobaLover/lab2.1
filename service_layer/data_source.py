from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class DataSourceError(Exception):
    """Ошибка чтения внешнего источника данных."""


class TextDataSource:
    """Читает текст из файла и загружает HTML по URL."""

    def read_txt(self, file_path):
        """Прочитать TXT в UTF-8; при ошибке кодировки попробовать Windows-1251."""
        path = Path(file_path)
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise DataSourceError(f"Не удалось прочитать файл: {error}") from error
        for encoding in ("utf-8-sig", "cp1251"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise DataSourceError("Не удалось определить кодировку TXT-файла.")

    def read_url(self, url):
        """Загрузить страницу и вернуть её текстовое содержимое."""
        if not url.startswith(("http://", "https://")):
            raise DataSourceError("URL должен начинаться с http:// или https://.")
        request = Request(url, headers={"User-Agent": "DateRegexLab/1.0"})
        try:
            with urlopen(request, timeout=15) as response:
                content = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
            return content.decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError) as error:
            raise DataSourceError(f"Не удалось загрузить веб-страницу: {error}") from error
