from dataclasses import dataclass


@dataclass
class DateRecord:
    date_text: str
    date_format: str
    is_valid: bool
    source: str
    occurrence: int
    id: int = None

    def to_dict(self):
        return {
            "id": self.id,
            "date_text": self.date_text,
            "date_format": self.date_format,
            "is_valid": self.is_valid,
            "source": self.source,
            "occurrence": self.occurrence,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            date_text=data["date_text"],
            date_format=data["date_format"],
            is_valid=data["is_valid"],
            source=data["source"],
            occurrence=data["occurrence"],
        )
