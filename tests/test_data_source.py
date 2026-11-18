import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from service_layer.data_source import DataSourceError, TextDataSource


class DataSourceTests(unittest.TestCase):
    def setUp(self):
        self.source = TextDataSource()

    def test_read_txt_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "text.txt"
            path.write_text("Дата 01.01.2024", encoding="utf-8")
            self.assertIn("01.01.2024", self.source.read_txt(path))

    def test_missing_txt_raises_clear_error(self):
        with self.assertRaises(DataSourceError):
            self.source.read_txt("missing-file.txt")

    def test_rejects_unsupported_url_scheme(self):
        with self.assertRaises(DataSourceError):
            self.source.read_url("ftp://example.com")

    @patch("service_layer.data_source.urlopen")
    def test_read_url(self, mocked_urlopen):
        class Headers:
            def get_content_charset(self):
                return "utf-8"

        class Response:
            headers = Headers()

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<p>01.01.2024</p>"

        mocked_urlopen.return_value = Response()
        self.assertIn("01.01.2024", self.source.read_url("https://example.com"))


if __name__ == "__main__":
    unittest.main()
