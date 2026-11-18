import json
from abc import ABC, abstractmethod
from pathlib import Path

from data_layer.date_record import DateRecord


class DateRepository(ABC):
    """Контракт хранилища записей о датах."""

    @abstractmethod
    def add_many(self, records):
        """Добавить несколько записей."""

    @abstractmethod
    def get_all(self):
        """Вернуть все записи."""

    @abstractmethod
    def get_by_id(self, record_id):
        """Найти запись по идентификатору."""

    @abstractmethod
    def delete(self, record_id):
        """Удалить запись по идентификатору."""

    @abstractmethod
    def clear(self):
        """Удалить все записи."""


class MemoryDateRepository(DateRepository):
    """Простое хранилище в оперативной памяти (для тестов и примеров)."""

    def __init__(self):
        self._records = []

    def add_many(self, records):
        self._records.extend(records)

    def get_all(self):
        return list(self._records)

    def get_by_id(self, record_id):
        return next((r for r in self._records if r.id == record_id), None)

    def delete(self, record_id):
        for index, record in enumerate(self._records):
            if record.id == record_id:
                del self._records[index]
                return True
        return False

    def clear(self):
        self._records.clear()


class JsonDateRepository(DateRepository):
    """Хранилище в JSON-файле; записи сохраняются между запусками."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def _load(self):
        if not self.file_path.exists():
            return []
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Корневой элемент JSON должен быть списком.")
            return [DateRecord.from_dict(item) for item in data]
        except json.JSONDecodeError as error:
            raise ValueError(f"Файл хранилища содержит некорректный JSON: {error}") from error
        except (KeyError, TypeError) as error:
            raise ValueError(f"Неверная структура записи в JSON: {error}") from error

    def _write(self, records):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(
                [record.to_dict() for record in records],
                file,
                ensure_ascii=False,
                indent=4,
            )

    def add_many(self, records):
        current = self._load()
        current.extend(records)
        self._write(current)

    def get_all(self):
        return self._load()

    def get_by_id(self, record_id):
        return next((r for r in self._load() if r.id == record_id), None)

    def delete(self, record_id):
        records = self._load()
        for index, record in enumerate(records):
            if record.id == record_id:
                del records[index]
                self._write(records)
                return True
        return False

    def clear(self):
        self._write([])
