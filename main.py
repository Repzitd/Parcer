import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

# Список доступных валют
currencies = [
    ("USD", "доллар"),
    ("EUR", "евро"),
    ("JPY", "йена"),
    ("CNY", "юань"),
    ("GBP", "фунт"),
    ("CHF", "франк"),
    ("INR", "рупия"),
    ("KZT", "тенге"),
    ("TRY", "лира"),
    ("RUB", "рубль")
]

def get_rates_by_date(date_obj: date):
    """Получаем курсы ЦБ РФ на конкретную дату"""
    date_str = date_obj.strftime("%d.%m.%Y")
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')

    val_date = datetime.strptime(soup.ValCurs['Date'], "%d.%m.%Y").date()
    rates = {"RUB": 1.0}
    for valute in soup.find_all('Valute'):
        code = valute.CharCode.text
        nominal = int(valute.Nominal.text)
        value = float(valute.Value.text.replace(',', '.'))
        rates[code] = value / nominal

    return val_date, rates

def display_currency_list():
    print("Доступные валюты:")
    for i, (code, name) in enumerate(currencies, 1):
        print(f"{i}. {name.title()} ({code})")

def select_currency(prompt: str) -> str:
    """Позволяет выбрать валюту по номеру из списка"""
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(currencies):
                return currencies[choice - 1][0]
            else:
                print(f"Введите число от 1 до {len(currencies)}\n")
        except ValueError:
            print("Введите корректное число")

def convert(amount: float, from_code: str, to_code: str, rates: dict) -> float:
    return amount * rates[from_code] / rates[to_code]

def input_date() -> date:
    """Позволяет выбрать дату: сегодня или ввести вручную"""
    while True:
        choice = input("Использовать сегодняшнюю дату? (да/нет): \n").strip().lower()
        if choice == "да":
            return date.today()
        elif choice == "нет":
            while True:
                date_input = input("Введите дату в формате dd.mm.yyyy (например, 2.9.2025): \n").strip()
                try:
                    day, month, year = map(int, date_input.split('.'))
                    date_obj = date(year, month, day)
                    if date_obj > date.today():
                        print("Дата не может быть больше текущей. Введите актуальную дату.")
                    else:
                        return date_obj
                except ValueError:
                    print("Неверный формат даты. Попробуйте снова.")
        else:
            print("Введите 'да' или 'нет'.")

def show_rate_difference(code: str, old_rate: float):
    """Вывод разницы курса выбранной валюты с текущим курсом"""
    _, current_rates = get_rates_by_date(date.today())
    current_rate = current_rates.get(code)
    if current_rate is None:
        print("Не удалось получить текущий курс валюты.")
        return
    diff = current_rate - old_rate
    diff_percent = (diff / old_rate) * 100
    sign = "+" if diff >= 0 else ""
    print(f"Разница курса {code} между выбранной датой и текущей равна {sign}{diff:.4f} руб ({sign}{diff_percent:.2f}%)")

# === основной код ===
if __name__ == "__main__":
    while True:
        print("\n--- Конвертер валют ЦБ РФ ---")
        display_currency_list()

        # Выбор даты
        val_date_obj = input_date()
        val_date, rates = get_rates_by_date(val_date_obj)

        # Выбор валют и суммы
        from_code = select_currency("\nВыберите валюту, которую хотите конвертировать (номер): \n")
        to_code = select_currency("Выберите валюту, в которую конвертировать (номер): \n")

        while True:
            try:
                amount = float(input("Введите сумму: \n"))
                break
            except ValueError:
                print("Введите корректное число")

        result = convert(amount, from_code, to_code, rates)
        print(f"\nНа {val_date} {amount} {from_code} = {result:.2f} {to_code}")

        # Показать разницу курса выбранной валюты с текущим курсом
        show_rate_difference(from_code, rates[from_code])

        repeat = input("\nВведите 'нет' для выхода или нажмите Enter для продолжения работы программы: ").strip().lower()
        if repeat == "нет":
            print("Программа завершена.")
            break