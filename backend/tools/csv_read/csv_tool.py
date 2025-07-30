import pandas as pd
import os
from typing import List, Literal

class CSVReader():
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"The file {path} does not exist.")
        if path.endswith(".csv"):
            self.df = pd.read_csv(path, header=0)
        elif path.endswith(".xlsx"):
            self.df = pd.read_excel(path, header=0)
        self.columns = self.df.columns.tolist()
        self.head = self.df.head()
        self.describe = self.df.describe()
    
    # Lấy thông tin mô tả của cột
    def get_column_desribe(self, selected_column: str):
        try:
            return self.describe[selected_column]
        except Exception as e:
            return f"Error: {e}"

    # Lọc dữ liệu theo các giá trị
    def filter_data_by_items(self, selected_items: list, selected_column: str):
        filtered_df = self.df[self.df[selected_column].isin(selected_items)]
        return filtered_df[["Trường_Viện_Khoa", "Mã_lớp", "Mã_HP", "Tên_HP","Buổi_số", "Thứ", "Loại_lớp", "Thời_gian"]]

    # Lọc dữ liệu theo số lượng
    def fiter_data_by_number(self,selected_column: str, comparision: float,constraint: List[Literal["larger", "smaller", "equal", "larger and equal", "smaller and equal"]] ):
        try:
            match constraint:
                case "larger":
                    return self.df[self.df[selected_column] > comparision]
                case "smaller":
                    return self.df[self.df[selected_column] < comparision]
                case "equal":
                    return self.df[self.df[selected_column] == comparision]
                case "larger and equal":
                    return self.df[self.df[selected_column] >= comparision]
                case "smaller and equal":
                    return self.df[self.df[selected_column] <= comparision]
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    csv_reader = CSVReader(r"\main\backend\data\excel_data\THỜI KHÓA BIỂU KỲ 20242.xlsx")
    print(csv_reader.filter_data_by_items(["Hệ hỗ trợ quyết định"],"Tên_HP"))