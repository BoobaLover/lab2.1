import json
from abc import ABC, abstractmethod
from pathlib import Path

from data_layer.date_record import DateRecord


class DateRepository(ABC):
    @abstractmethod
    def add_many(self, records):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, record_id):
        pass

    @abstractmethod
    def get_next_id(self):
        pass

    @abstractmethod
    def delete(self, record_id):
        pass

    @abstractmethod
    def clear(self):
        pass


class MemoryDateRepository(DateRepository):
    def __init__(self):
        self.records = []

    def get_next_id(self):
        ids = [r.id for r in self.records if isinstance(r.id, int)]
        return max(ids, default=0) + 1

    def add_many(self, records):
        next_id = self.get_next_id()

        for record in records:
            if record.id is None:
                record.id = next_id
                next_id += 1

        self.records.extend(records)

    def get_all(self):
        return list(self.records)

    def get_by_id(self, record_id):
        return next(
            (r for r in self.records if r.id == record_id),
            None
        )

    def delete(self, record_id):
        for record in self.records:
            if record.id == record_id:
                self.records.remove(record)
                return True
        return False

    def clear(self):
        self.records.clear()


class JsonDateRepository(DateRepository):
    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def _load(self):
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Некорректная структура JSON.")

            records = [
                DateRecord.from_dict(item)
                for item in data
            ]


            used_ids = {
                r.id for r in records
                if isinstance(r.id, int)
            }

            next_id = max(used_ids, default=0) + 1
            changed = False

            for record in records:
                if not isinstance(record.id, int):
                    while next_id in used_ids:
                        next_id += 1

                    record.id = next_id
                    used_ids.add(next_id)
                    next_id += 1
                    changed = True

            if changed:
                self._write(records)

            return records

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Ошибка чтения JSON: {error}"
            ) from error

    def _write(self, records):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(
                [r.to_dict() for r in records],
                file,
                ensure_ascii=False,
                indent=4
            )

    def get_next_id(self):
        records = self._load()
        ids = [r.id for r in records if isinstance(r.id, int)]
        return max(ids, default=0) + 1

    def add_many(self, records):
        current = self._load()
        next_id = max(
            (r.id for r in current if isinstance(r.id, int)),
            default=0
        ) + 1

        for record in records:
            if record.id is None:
                record.id = next_id
                next_id += 1

        current.extend(records)
        self._write(current)

    def get_all(self):
        return self._load()

    def get_by_id(self, record_id):
        return next(
            (r for r in self._load() if r.id == record_id),
            None
        )

    def delete(self, record_id):
        records = self._load()

        for record in records:
            if record.id == record_id:
                records.remove(record)
                self._write(records)
                return True

        return False

    def clear(self):
        self._write([])
