from flask import Flask, render_template, request, jsonify
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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
    date_str = date_obj.strftime("%d.%m.%Y")
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    rates = {"RUB": 1.0}
    for valute in soup.find_all('Valute'):
        code = valute.CharCode.text
        nominal = int(valute.Nominal.text)
        value = float(valute.Value.text.replace(',', '.'))
        rates[code] = value / nominal
    return rates

def convert(amount: float, from_code: str, to_code: str, rates: dict) -> float:
    return amount * rates[from_code] / rates[to_code]

@app.route('/')
def index():
    return render_template('index.html', currencies=currencies)

@app.route('/convert', methods=['GET'])
def convert_api():
    from_currency = request.args.get('from')
    to_currency = request.args.get('to')
    amount = float(request.args.get('amount', 0))
    date_str = request.args.get('date')

    if date_str:
        day, month, year = map(int, date_str.split('.'))
        val_date = date(year, month, day)
    else:
        val_date = date.today()

    rates = get_rates_by_date(val_date)
    result = convert(amount, from_currency, to_currency, rates)

    current_rates = get_rates_by_date(date.today())
    current_result = convert(amount, from_currency, to_currency, current_rates)
    diff = current_result - result
    diff_percent = (diff / result) * 100 if result != 0 else 0

    return jsonify({
        "date": val_date.strftime("%d.%m.%Y"),
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "result": round(result, 2),
        "rate_difference": diff,
        "rate_difference_percent": diff_percent
    })

@app.route('/history', methods=['GET'])
def history_api():
    from_currency = request.args.get('from')
    to_currency = request.args.get('to')

    today = date.today()
    history = []

    for i in range(30):
        d = today - timedelta(days=29 - i)
        try:
            rates = get_rates_by_date(d)
            rate = convert(1, from_currency, to_currency, rates)
            history.append({"date": d.strftime("%d.%m"), "rate": round(rate, 4)})
        except Exception:
            continue

    return jsonify(history)

if __name__ == "__main__":
    app.run(debug=True)