import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, Float, Date, MetaData
from sqlalchemy import inspect

app = Flask(__name__)

CLOUD_SQL_CONNECTION_NAME = 'dividend-app-db:us-central1:postgres-1'
DB_USER = 'postgres'      # 請填入您的資料庫使用者名稱
DB_PASS = '000000'        # 請填入您的資料庫密碼
DB_NAME = 'postgres'      # 請填入您的資料庫名稱
DB_HOST = '34.56.5.186'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 預設的資料模型，當 table_type 為 0 且未提供 table_name 時使用
class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)  # 股票代碼
    stock_name = db.Column(db.String(50), nullable=True)       # 股票名稱
    industry_category = db.Column(db.String(50), nullable=True)  # 產業類別
    type = db.Column(db.String(20), nullable=True)             # 類型
    dividend = db.Column(db.Float, nullable=True)              # 股息
    price = db.Column(db.Float, nullable=True)                 # 價格
    date = db.Column(db.Date, nullable=False)                  # 日期

with app.app_context():
    db.create_all()

@app.route('/data', methods=['POST'])
def insert_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "沒有提供資料"}), 400

    # 取得共用欄位
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

    # 取得 table_type 參數，預設為 0
    table_type = data.get("table_type", 0)

    if table_type == 2:
        # table_type == 2：使用預設模型 StockData，將資料插入預設表
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
        return jsonify({"message": "資料已插入至預設表 'StockData'"}), 201

    elif table_type == 1:
        # table_type == 1：要求提供 table_name，並以動態建立/插入表格方式處理
        table_name = data.get("table_name")
        if not table_name:
            return jsonify({"error": "table_type 為 1 時必須提供 table_name 參數"}), 400

        # 如果 table_name 以數字開頭，加上前綴 "t_"
        if table_name[0].isdigit():
            table_name = "t_" + table_name

        metadata = MetaData(bind=db.engine)
        inspector = inspect(db.engine)
        # 檢查 table 是否存在，若不存在則建立新表
        if not inspector.has_table(table_name):
            new_table = Table(
                table_name,
                metadata,
                Column('id', Integer, primary_key=True),
                Column('stock_symbol', String(10), nullable=False),
                Column('dividend_year', String(4), nullable=True),
                Column('dividend_period', String(50), nullable=True),
                Column('shareholders_meeting_date', String(20), nullable=True),
                Column('ex_dividend_date', String(20), nullable=True),
                Column('ex_dividend_reference_price', Float, nullable=True),
                Column('fill_dividend_completion_date', String(20), nullable=True),
                Column('fill_dividend_days', Integer, nullable=True),
                Column('cash_dividend_distribution_date', String(50), nullable=True),
                Column('ex_rights_date', String(20), nullable=True),
                Column('ex_rights_reference_price', Float, nullable=True),
                Column('fill_rights_completion_date', String(20), nullable=True),
                Column('fill_rights_days', Integer, nullable=True),
                Column('cash_dividend_earnings', Float, nullable=True),
                Column('cash_dividend_capital_surplus', Float, nullable=True),
                Column('total_cash_dividend', Float, nullable=True),
                Column('stock_dividend_earnings', Float, nullable=True),
                Column('stock_dividend_capital_surplus', Float, nullable=True),
                Column('total_stock_dividend', Float, nullable=True),
                Column('total_dividend', Float, nullable=True),
                Column('date', Date, nullable=False)  # 新增 date 欄位
            )
            new_table.create(db.engine)
            print(f"Table '{table_name}' created.")

        # 反射載入該動態表格並插入資料
        table = Table(table_name, metadata, autoload_with=db.engine)
        ins = table.insert().values(
            stock_symbol=stock_symbol,
            dividend_year=data.get("dividend_year"),
            dividend_period=data.get("dividend_period"),
            shareholders_meeting_date=data.get("shareholders_meeting_date"),
            ex_dividend_date=data.get("ex_dividend_date"),
            ex_dividend_reference_price=data.get("ex_dividend_reference_price"),
            fill_dividend_completion_date=data.get("fill_dividend_completion_date"),
            fill_dividend_days=data.get("fill_dividend_days"),
            cash_dividend_distribution_date=data.get("cash_dividend_distribution_date"),
            ex_rights_date=data.get("ex_rights_date"),
            ex_rights_reference_price=data.get("ex_rights_reference_price"),
            fill_rights_completion_date=data.get("fill_rights_completion_date"),
            fill_rights_days=data.get("fill_rights_days"),
            cash_dividend_earnings=data.get("cash_dividend_earnings"),
            cash_dividend_capital_surplus=data.get("cash_dividend_capital_surplus"),
            total_cash_dividend=data.get("total_cash_dividend"),
            stock_dividend_earnings=data.get("stock_dividend_earnings"),
            stock_dividend_capital_surplus=data.get("stock_dividend_capital_surplus"),
            total_stock_dividend=data.get("total_stock_dividend"),
            total_dividend=data.get("total_dividend"),
            date=date_obj
        )
        conn = db.engine.connect()
        conn.execute(ins)
        conn.close()

        return jsonify({"message": f"資料已插入至 '{table_name}'"}), 201

    else:
        # table_type == 0：如果提供 table_name 則使用動態表處理，否則使用預設表 StockData
        table_name = data.get("table_name")
        if table_name:
            if table_name[0].isdigit():
                table_name = "t_" + table_name

            metadata = MetaData(bind=db.engine)
            inspector = inspect(db.engine)
            if not inspector.has_table(table_name):
                new_table = Table(
                    table_name,
                    metadata,
                    Column('id', Integer, primary_key=True),
                    Column('stock_symbol', String(10), nullable=False),
                    Column('stock_name', String(50), nullable=True),
                    Column('industry_category', String(50), nullable=True),
                    Column('type', String(20), nullable=True),
                    Column('dividend', Float, nullable=True),
                    Column('price', Float, nullable=True),
                    Column('date', Date, nullable=False)
                )
                new_table.create(db.engine)
                print(f"Table '{table_name}' created.")

            table = Table(table_name, metadata, autoload_with=db.engine)
            ins = table.insert().values(
                stock_symbol=stock_symbol,
                stock_name=stock_name,
                industry_category=industry_category,
                type=type_value,
                dividend=dividend,
                price=price,
                date=date_obj
            )
            conn = db.engine.connect()
            conn.execute(ins)
            conn.close()
            return jsonify({"message": f"資料已插入至動態表 '{table_name}'"}), 201
        else:
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
            return jsonify({"message": "資料已插入至預設表 'StockData'"}), 201

@app.route('/data', methods=['GET'])
def get_data():
    table_name = request.args.get("table_name")
    if table_name:
        metadata = MetaData(bind=db.engine)
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):
            return jsonify({"error": f"Table '{table_name}' 不存在"}), 404

        table = Table(table_name, metadata, autoload_with=db.engine)
        conn = db.engine.connect()
        result = conn.execute(table.select()).fetchall()
        conn.close()

        records = []
        for row in result:
            records.append({
                "id": row.id,
                "stock_symbol": row.stock_symbol,
                "stock_name": row.stock_name,
                "industry_category": row.industry_category,
                "type": row.type,
                "dividend": row.dividend,
                "price": row.price,
                "date": row.date.strftime('%Y-%m-%d')
            })
        return jsonify(records), 200
    else:
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
