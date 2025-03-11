import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividend.db'

CLOUD_SQL_CONNECTION_NAME = 'dividend-app-db:us-central1:postgres-1'
DB_USER = 'postgres'  # 需要填入您的資料庫使用者名稱
DB_PASS = '000000'  # 需要填入您的資料庫密碼
DB_NAME = 'postgres'  # 需要填入您的資料庫名稱


# DB_HOST = '127.0.0.1'
DB_HOST = '34.56.5.186'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}'




app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)  # 股票代碼
    stock_name = db.Column(db.String(50), nullable=True)     # 股票名稱
    industry_category = db.Column(db.String(50), nullable=True)  # 產業類別
    type = db.Column(db.String(20), nullable=True)           # 類型
    dividend = db.Column(db.Float, nullable=True)            # 股息
    price = db.Column(db.Float, nullable=True)               # 價格
    date = db.Column(db.Date, nullable=False)                # 日期

with app.app_context():
    db.create_all()

@app.route('/data', methods=['POST'])
def insert_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "沒有提供資料"}), 400

    stock_symbol = data.get("stock_symbol")
    stock_name = data.get("stock_name")
    industry_category = data.get("industry_category")
    type_value = data.get("type")
    dividend = data.get("dividend")
    price = data.get("price")
    date_str = data.get("date")

    if not stock_symbol or not date_str:
        return jsonify({"error": "缺少必要欄位：stock_symbol 或 date"}), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "日期格式錯誤，應為 YYYY-MM-DD"}), 400

    record = StockData(
        stock_symbol=stock_symbol, 
        stock_name=stock_name,
        industry_category=industry_category,
        type=type_value,
        dividend=dividend, 
        price=price, 
        date=date_obj
    )
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
            "stock_name": record.stock_name,
            "industry_category": record.industry_category,
            "type": record.type,
            "dividend": record.dividend,
            "price": record.price,
            "date": record.date.strftime('%Y-%m-%d')
        })
    return jsonify(results), 200

# 批量導入路由 - 用於直接從應用程序導入CSV
@app.route('/import-csv', methods=['POST'])
def import_csv():
    # 這個功能需要文件上傳，這裡僅做示範
    # 實際使用時可能需要另外設計
    return jsonify({"message": "此功能尚未實現"}), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)