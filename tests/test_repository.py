import tempfile
import unittest
from pathlib import Path

from data_layer.date_record import DateRecord
from repository_layer.date_repository import (
    JsonDateRepository,
    MemoryDateRepository,
)


def sample_record():
    return DateRecord("29.02.2024", "ДД.ММ.ГГГГ", True, "test", 1)


class MemoryRepositoryTests(unittest.TestCase):
    def test_crud(self):
        repository = MemoryDateRepository()
        record = sample_record()
        repository.add_many([record])
        self.assertEqual(repository.get_by_id(record.id), record)
        self.assertEqual(repository.get_all(), [record])
        self.assertTrue(repository.delete(record.id))
        self.assertFalse(repository.delete(record.id))
        repository.add_many([record])
        repository.clear()
        self.assertEqual(repository.get_all(), [])


class JsonRepositoryTests(unittest.TestCase):
    def test_persistence_and_crud(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "dates.json"
            repository = JsonDateRepository(path)
            record = sample_record()
            repository.add_many([record])

            # Новый экземпляр читает те же данные с диска.
            second_repository = JsonDateRepository(path)
            loaded = second_repository.get_by_id(record.id)
            self.assertEqual(loaded.date_text, record.date_text)
            self.assertTrue(second_repository.delete(record.id))
            self.assertEqual(second_repository.get_all(), [])
            second_repository.add_many([record])
            second_repository.clear()
            self.assertEqual(second_repository.get_all(), [])

    def test_missing_file_is_empty_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonDateRepository(Path(directory) / "missing.json")
            self.assertEqual(repository.get_all(), [])


if __name__ == "__main__":
    unittest.main()
