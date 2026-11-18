import unittest

from repository_layer.date_repository import MemoryDateRepository
from service_layer.date_service import DateService


class DateServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = DateService(MemoryDateRepository())

    def test_all_supported_formats(self):
        text = "01.02.2024 02/03/2024 03-04-2024 2024-05-06"
        records = self.service.find_dates(text)
        self.assertEqual(len(records), 4)
        self.assertTrue(all(record.is_valid for record in records))

    def test_invalid_calendar_date_is_found(self):
        records = self.service.find_dates("31.02.2026")
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0].is_valid)

    def test_repeated_occurrences_are_separate(self):
        records = self.service.find_dates("01.01.2020 и снова 01.01.2020")
        self.assertEqual(len(records), 2)
        self.assertEqual([r.occurrence for r in records], [1, 2])
        self.assertNotEqual(records[0].id, records[1].id)

    def test_mixed_separator_and_embedded_digits_are_not_matched(self):
        records = self.service.find_dates("1.1.2020 01.02/2020 x101.02.2020")
        self.assertEqual(records, [])

    def test_repository_operations_through_service(self):
        records = self.service.find_dates("10.10.2020")
        self.service.save_records(records)
        self.assertEqual(len(self.service.get_all_records()), 1)
        record_id = records[0].id
        self.assertIsNotNone(self.service.get_record_by_id(record_id))
        self.assertTrue(self.service.delete_record(record_id))
        self.assertIsNone(self.service.get_record_by_id(record_id))
        self.service.save_records(records)
        self.service.clear_records()
        self.assertEqual(self.service.get_all_records(), [])


if __name__ == "__main__":
    unittest.main()
