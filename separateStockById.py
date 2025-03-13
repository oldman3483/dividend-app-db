import os
import pandas as pd

class Util:
    @staticmethod
    def split_csv_by_stock_code(file_path, output_dir="."):
        """
        Read the specified CSV file and group the data by the "股票代號" (stock code). 
        Then, save each group into a new CSV file where the file name is the stock code. 
        The files will be stored in the output_dir directory (default is the current directory).
        
        Parameters: file_path (str): The path to the original CSV file. 
        output_dir (str): The directory where the split files are saved, default is the current directory.
        """
        df = pd.read_csv(file_path, encoding="utf-8")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for stock_code, group in df.groupby("股票代號"):
            filename = os.path.join(output_dir, f"{stock_code}.csv")
            group.to_csv(filename, index=False, encoding="utf-8")
            print(f"已儲存：{filename}")

# 使用範例
if __name__ == "__main__":
    Util.split_csv_by_stock_code("data.csv", output_dir="output_csvs")
