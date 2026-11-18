import re
from datetime import datetime

from data_layer.date_record import DateRecord
from repository_layer.date_repository import DateRepository


class DateService:
    DATE_PATTERN = re.compile(
        r"(?<!\d)(?:"
        r"(?P<dot>\d{2}\.\d{2}\.\d{4})|"
        r"(?P<slash>\d{2}/\d{2}/\d{4})|"
        r"(?P<dash>\d{2}-\d{2}-\d{4})|"
        r"(?P<iso>\d{4}-\d{2}-\d{2})"
        r")(?!\d)"
    )
    FORMAT_INFO = {
        "dot": ("%d.%m.%Y", "ДД.ММ.ГГГГ"),
        "slash": ("%d/%m/%Y", "ДД/ММ/ГГГГ"),
        "dash": ("%d-%m-%Y", "ДД-ММ-ГГГГ"),
        "iso": ("%Y-%m-%d", "ГГГГ-ММ-ДД"),
    }

    def __init__(self, repository: DateRepository):
        self._repository = repository

    def find_dates(self, text, source="Текст"):
        if not isinstance(text, str):
            raise TypeError("Для поиска необходимо передать строку.")
        records = []
        next_id = self._repository.get_next_id()
        for occurrence, match in enumerate(self.DATE_PATTERN.finditer(text), start=1):
            key = match.lastgroup
            date_text = match.group()
            date_format, display_format = self.FORMAT_INFO[key]
            try:
                datetime.strptime(date_text, date_format)
                is_valid = True
            except ValueError:
                is_valid = False
            records.append(
                DateRecord(
                    date_text=date_text,
                    date_format=display_format,
                    is_valid=is_valid,
                    source=source,
                    occurrence=occurrence,
                    id=next_id + len(records),
                )
            )
        return records

    def save_records(self, records):
        self._repository.add_many(records)

    def get_all_records(self):
        return self._repository.get_all()

    def get_record_by_id(self, record_id):
        return self._repository.get_by_id(record_id)

    def delete_record(self, record_id):
        return self._repository.delete(record_id)

    def clear_records(self):
        self._repository.clear()
