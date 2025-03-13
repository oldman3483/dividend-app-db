import os
import requests
import pandas as pd
import time
from datetime import datetime

# GCP API 端點
BASE_URL = "https://postgres-1-148949302162.asia-east1.run.app"

class Utils:
    @staticmethod
    def import_stock_data(file_path="0050.csv", base_url=BASE_URL):
        """
        讀取指定的 CSV 檔案，並將每一筆資料以 POST 請求送入 API 中。
        每筆資料皆加入參數 "table_type": 1 與 "table_name"（取自檔案名稱去除副檔名）。
        若檔案名稱以數字開頭，則在前面加上 "t_" 前綴，確保為合法的 PostgreSQL table 名稱。
        
        CSV 欄位對應 (轉成英文)：
            股票代號 -> stock_symbol
            股利發放年度 -> dividend_year
            股利盈餘所屬期間 -> dividend_period
            股東會日期 -> shareholders_meeting_date
            除息交易日 -> ex_dividend_date
            除息參考價 -> ex_dividend_reference_price
            填息完成日 -> fill_dividend_completion_date
            填息花費天數 -> fill_dividend_days
            現金股利發放日 -> cash_dividend_distribution_date
            除權交易日 -> ex_rights_date
            除權參考價 -> ex_rights_reference_price
            填權完成日 -> fill_rights_completion_date
            填權花費天數 -> fill_rights_days
            現金股利(盈餘) -> cash_dividend_earnings
            現金股利(公積) -> cash_dividend_capital_surplus
            總現金股利 -> total_cash_dividend
            股票股利(盈餘) -> stock_dividend_earnings
            股票股利(公積) -> stock_dividend_capital_surplus
            總股票股利 -> total_stock_dividend
            總股利合計 -> total_dividend
            ※另外加入 "date" 欄位記錄匯入日期
        
        參數:
            file_path (str): CSV 檔案路徑，預設為 "0050.csv"
            base_url (str): API 的基本 URL，預設為 BASE_URL
        """
        # 取出檔案名稱 (去除副檔名) 作為 table_name
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        # 若 table_name 以數字開頭，加上前綴 "t_"
        if table_name and table_name[0].isdigit():
            table_name = "t_" + table_name

        # 讀取 CSV 檔案
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"成功讀取 CSV，共 {len(df)} 筆資料")
        except Exception as e:
            print(f"讀取 CSV 失敗: {e}")
            return

        success = 0
        fail = 0

        # 定義動態表格中存在的欄位
        allowed_keys = [
            "table_type", "table_name", "stock_symbol", "dividend_year", "dividend_period", "shareholders_meeting_date",
            "ex_dividend_date", "ex_dividend_reference_price", "fill_dividend_completion_date",
            "fill_dividend_days", "cash_dividend_distribution_date", "ex_rights_date",
            "ex_rights_reference_price", "fill_rights_completion_date", "fill_rights_days",
            "cash_dividend_earnings", "cash_dividend_capital_surplus", "total_cash_dividend",
            "stock_dividend_earnings", "stock_dividend_capital_surplus", "total_stock_dividend",
            "total_dividend", "date"
        ]

        # 設定 API 請求標頭
        headers = {"Content-Type": "application/json"}

        # 逐筆處理資料
        for index, row in df.iterrows():
            # 建立原始 payload（包含其他不屬於資料表欄位的鍵，如 table_type 與 table_name）
            payload = {
                "table_type": 1,                # 固定 table_type = 1
                "table_name": table_name,       # 從檔案名稱取得的 table_name
                "stock_symbol": str(row["股票代號"]) if "股票代號" in row else None,
                "dividend_year": str(row["股利發放年度"]) if "股利發放年度" in row else None,
                "dividend_period": str(row["股利盈餘所屬期間"]) if "股利盈餘所屬期間" in row else None,
                "shareholders_meeting_date": str(row["股東會日期"]) if "股東會日期" in row else None,
                "ex_dividend_date": str(row["除息交易日"]) if "除息交易日" in row else None,
                "ex_dividend_reference_price": float(row["除息參考價"]) if "除息參考價" in row and pd.notna(row["除息參考價"]) else None,
                "fill_dividend_completion_date": str(row["填息完成日"]) if "填息完成日" in row else None,
                "fill_dividend_days": int(row["填息花費天數"]) if "填息花費天數" in row and pd.notna(row["填息花費天數"]) else None,
                "cash_dividend_distribution_date": str(row["現金股利發放日"]) if "現金股利發放日" in row else None,
                "ex_rights_date": str(row["除權交易日"]) if "除權交易日" in row else None,
                "ex_rights_reference_price": float(row["除權參考價"]) if "除權參考價" in row and pd.notna(row["除權參考價"]) else None,
                "fill_rights_completion_date": str(row["填權完成日"]) if "填權完成日" in row else None,
                "fill_rights_days": int(row["填權花費天數"]) if "填權花費天數" in row and pd.notna(row["填權花費天數"]) else None,
                "cash_dividend_earnings": float(row["現金股利(盈餘)"]) if "現金股利(盈餘)" in row and pd.notna(row["現金股利(盈餘)"]) else None,
                "cash_dividend_capital_surplus": float(row["現金股利(公積)"]) if "現金股利(公積)" in row and pd.notna(row["現金股利(公積)"]) else None,
                "total_cash_dividend": float(row["總現金股利"]) if "總現金股利" in row and pd.notna(row["總現金股利"]) else None,
                "stock_dividend_earnings": float(row["股票股利(盈餘)"]) if "股票股利(盈餘)" in row and pd.notna(row["股票股利(盈餘)"]) else None,
                "stock_dividend_capital_surplus": float(row["股票股利(公積)"]) if "股票股利(公積)" in row and pd.notna(row["股票股利(公積)"]) else None,
                "total_stock_dividend": float(row["總股票股利"]) if "總股票股利" in row and pd.notna(row["總股票股利"]) else None,
                "total_dividend": float(row["總股利合計"]) if "總股利合計" in row and pd.notna(row["總股利合計"]) else None,
                "dividend": None,  # 此欄位不屬於動態表 schema，會過濾掉
                "date": datetime.now().strftime('%Y-%m-%d')
            }
            
            # 過濾掉不屬於資料表的欄位
            insert_payload = { 
                key: value 
                for key, value in payload.items() 
                if key in allowed_keys
            }
            
            # 印出 debug 訊息
            print(f"Payload: {insert_payload}")
            
            # 發送 POST 請求到 API
            try:
                response = requests.post(f"{base_url}/data", json=insert_payload, headers=headers)
                response.raise_for_status()
                success += 1
                print(f"成功導入 {insert_payload.get('stock_symbol')} - {insert_payload.get('dividend_year')}")
            except Exception as e:
                fail += 1
                print(f"導入失敗 {insert_payload.get('stock_symbol')}: {e}")
            
            # 測試用：每處理 10 筆暫停一下，正式使用時可移除 break 以處理全部資料
            if index % 10 == 0 and index > 0:
                print(f"已處理 {index} 筆資料，暫停一下...")
                time.sleep(0.5)
            # break  # 測試只處理一筆
            
        print(f"\n導入完成！成功: {success}, 失敗: {fail}")
        
        # 查詢指定 table 的資料筆數（假設 API 支援以 table_name 查詢）
        try:
            response = requests.get(f"{base_url}/data?table_name={table_name}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"資料庫中 table '{table_name}' 共有 {len(data)} 筆記錄")
        except Exception as e:
            print(f"查詢資料庫失敗: {e}")

if __name__ == "__main__":
    print("開始導入 0050.csv 的資料...")
    Utils.import_stock_data("./stockDividend/00713.csv")
    Utils.import_stock_data("./stockDividend/00919.csv")

