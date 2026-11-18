

from pathlib import Path

from repository_layer.date_repository import JsonDateRepository
from service_layer.data_source import DataSourceError, TextDataSource
from service_layer.date_service import DateService


def print_records(records):
    if not records:
        print("Записей нет.")
        return
    for record in records:
        status = "корректная" if record.is_valid else "некорректная"
        print(
            f"ID: {record.id} | Дата: {record.date_text} | "
            f"Формат: {record.date_format} | Статус: {status} | "
            f"Источник: {record.source} | Вхождение: {record.occurrence}"
        )


def main():
    repository = JsonDateRepository(Path(__file__).parent / "dates.json")
    service = DateService(repository)
    data_source = TextDataSource()

    while True:
        print("\n=== Поиск и проверка дат ===")
        print("1. Найти даты в тексте")
        print("2. Найти даты в TXT-файле")
        print("3. Найти даты на веб-странице")
        print("4. Показать все записи")
        print("5. Найти запись по ID")
        print("6. Удалить запись")
        print("7. Очистить хранилище")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                text = input("Введите текст: ")
                records = service.find_dates(text, source="Введённый текст")
                print(f"Найдено вхождений: {len(records)}")
                print_records(records)
                if records and input("Сохранить найденные записи? (д/н): ").lower() == "д":
                    service.save_records(records)
                    print("Записи сохранены.")
            elif choice == "2":
                path = input("Путь к TXT-файлу: ").strip()
                text = data_source.read_txt(path)
                records = service.find_dates(text, source=str(path))
                print_records(records)
                if records and input("Сохранить найденные записи? (д/н): ").lower() == "д":
                    service.save_records(records)
                    print("Записи сохранены.")
            elif choice == "3":
                url = input("URL страницы: ").strip()
                text = data_source.read_url(url)
                records = service.find_dates(text, source=url)
                print_records(records)
                if records and input("Сохранить найденные записи? (д/н): ").lower() == "д":
                    service.save_records(records)
                    print("Записи сохранены.")
            elif choice == "4":
                print_records(service.get_all_records())
            elif choice == "5":
                record_id = int(input("Введите ID: ").strip())
                record = service.get_record_by_id(record_id)
                print_records([record] if record else [])

            elif choice == "6":
                record_id = int(input("Введите ID для удаления: ").strip())
                if service.delete_record(record_id):
                    print("Запись удалена.")
                else:
                    print("Запись не найдена.")
            elif choice == "7":
                confirmation = input("Удалить все записи? (д/н): ").strip().lower()
                if confirmation == "д":
                    service.clear_records()
                    print("Хранилище очищено.")
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неизвестный пункт меню.")
        except (DataSourceError, OSError, ValueError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
