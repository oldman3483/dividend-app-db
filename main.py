import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividend.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)
    dividend = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/data', methods=['POST'])
def insert_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "沒有提供資料"}), 400

    stock_symbol = data.get("stock_symbol")
    dividend = data.get("dividend")
    price = data.get("price")
    date_str = data.get("date")

    if not stock_symbol or not date_str:
        return jsonify({"error": "缺少必要欄位：stock_symbol 或 date"}), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "日期格式錯誤，應為 YYYY-MM-DD"}), 400

    record = StockData(stock_symbol=stock_symbol, dividend=dividend, price=price, date=date_obj)
    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "資料插入成功"}), 201

@app.route('/data', methods=['GET'])
def get_data():
    records = StockData.query.all()
    results = []
    for record in records:
        results.append({
            "id": record.id,
            "stock_symbol": record.stock_symbol,
            "dividend": record.dividend,
            "price": record.price,
            "date": record.date.strftime('%Y-%m-%d')
        })
    return jsonify(results), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
