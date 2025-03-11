import requests
import pandas as pd
import time
from datetime import datetime

# GCP API端點
BASE_URL = "https://mysql-local-conn-148949302162.asia-east1.run.app"

def import_stock_data():
    # 讀取CSV
    try:
        df = pd.read_csv('TaiwanStockInfo.csv', encoding='utf-8')
        print(f"成功讀取CSV，共{len(df)}筆資料")
    except Exception as e:
        print(f"讀取CSV失敗: {e}")
        return
    
    success = 0
    fail = 0
    
    # 設定API請求頭
    headers = {"Content-Type": "application/json"}
    
    # 處理每一筆資料
    for index, row in df.iterrows():
        # 只使用原始main.py支持的欄位
        data = {
            "stock_symbol": str(row['stock_id']),
            "dividend": None,  # 假設無股息數據
            "price": None,     # 假設無價格數據
            "date": datetime.now().strftime('%Y-%m-%d')
        }
        
        # 發送API請求
        try:
            response = requests.post(f"{BASE_URL}/data", json=data, headers=headers)
            response.raise_for_status()
            success += 1
            print(f"成功導入 {row['stock_id']} - {row['stock_name']}")
        except Exception as e:
            fail += 1
            print(f"導入失敗 {row['stock_id']}: {e}")
        
        # 每10筆暫停一下
        if index % 10 == 0 and index > 0:
            print(f"已處理 {index} 筆數據，暫停一下...")
            time.sleep(0.5)
    
    print(f"\n導入完成！成功: {success}, 失敗: {fail}")
    
    # 檢查已導入數據
    try:
        response = requests.get(f"{BASE_URL}/data")
        if response.status_code == 200:
            data = response.json()
            print(f"資料庫中共有 {len(data)} 筆記錄")
    except Exception as e:
        print(f"查詢資料庫失敗: {e}")

if __name__ == "__main__":
    print("開始導入台灣股票資料...")
    import_stock_data()