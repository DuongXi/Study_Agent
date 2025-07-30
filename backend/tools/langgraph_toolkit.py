import os
from langchain_core.tools import tool
from typing import Literal
from tools.sql.sql_tool import DatabaseConnector
from tools.csv_read.csv_tool import CSVReader
from tools.vector_db.vector_tool import WeaviateRetriver
from tools.tool_config import *
from tools.google_calendar.calendar_tool import Calendar
from tools.google_drive.drive_tool import Drive
import sys
import json
from dotenv import load_dotenv
load_dotenv()
import sys
sys.stdout.reconfigure(encoding='utf-8')

csv_reader = CSVReader(EXCEL_PATH)
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
connection = DatabaseConnector(
        db_type=DATABASE_TYPE,
        host="localhost",
        user="root",
        password=os.getenv("DATABASE_PASSWORD"),
        database="chuong_trinh_dao_tao"
    )
calendar = Calendar()
drive = Drive()

@tool("get_csv_column")
def get_csv_column():
    """_summary_
    Lấy các cột trong file thời khoá biểu.
    """
    return csv_reader.columns

@tool("get_csv_head_rows")
def get_csv_head_rows():
    """_summary_
    Lấy thông tin một số hàng đầu trong file thời khoá biểu.
    """
    data_dict=csv_reader.head.to_dict()
    return json.dumps(data_dict, ensure_ascii=False)

@tool("filter_csv_data_by_items")
def filter_data_by_subject(selected_items: list[str], selected_column: str):
    """_summary_
    Lấy thông tin thời khoá biểu dựa trên tên hoặc mã các học phần

    Args:
        selected_items (list): Tên hoặc mã các học phần cần lọc
        selected_column (str): Tên cột chứa thông tin tương ứng
    
    Returns: Bảng gồm thông tin học phần trong thời khoá biểu
    """
    data_dict=csv_reader.filter_data_by_items(selected_items=selected_items, selected_column=selected_column).to_dict()
    return json.dumps(data_dict, ensure_ascii=False)

@tool("list_database_tables")
def list_database_tables():
    """_summary_
    Lấy thông tin các bảng và kết nối trong database.
    """
    return connection.get_metadata()

@tool("get_database_data")
def get_database_data(query: str):
    """
    Lấy dữ liệu từ database.
    
    Args:
        query (str): Câu truy vấn SQL để lấy dữ liệu.
    """
    return connection.get_data(query=query)

@tool("doc_retrieve")
def doc_retrieve(query: str):
    """_summary_
    Tìm kiếm thông tin liên quan đến đại học trong vector database

    Args:
        query (str): Câu hỏi của người dùng
    """
    retriver = WeaviateRetriver(WEAVIATE_URL,WEAVIATE_API_KEY)
    return {"documents":retriver.search(query, 7)}

@tool("get_calendar_recurring_events")
def get_calendar_recurring_events():
    """_summary_
    Lấy thông tin các sự kiện lặp lại trong lịch
    """
    return calendar.get_recurring_event()

@tool("get_calendar_upcoming_events")
def get_calendar_upcoming_events():
    """_summary_
    Lấy thông tin các sự kiện sắp tới trong lịch
    """
    return calendar.get_upcoming_events()

@tool("create_calendar_event")
def create_calendar_event(summary: str, location: str, description: str, start: str, end: str):
    """_summary_
    Tạo sự kiện trong lịch
    """
    event = calendar.generate_event(summary, location, description, start, end)
    return calendar.create_event(event)

@tool("create_calendar_recurring_event")
def create_calendar_recurring_event(summary: str, location: str, description: str, start: str, end: str, freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], count: int):
    """_summary_
    Tạo sự kiện lặp lại trong lịch
    """
    event = calendar.generate_recurring_event(summary, location, description, start, end, freq, count)
    return calendar.create_event(event)

@tool("update_calendar_event")
def update_calendar_event(event_id: str, summary: str, location: str, description: str, start: str, end: str, freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], count: int):
    """_summary_
    Cập nhật sự kiện trong lịch
    """
    return calendar.update_event(event_id, summary, location, description, start, end, freq, count)

@tool("delete_calendar_event")
def delete_calendar_event(event_id: str):
    """_summary_
    Xóa sự kiện trong lịch
    """
    return calendar.delete_event(event_id)

@tool("delete_calendar_recurring_event")
def delete_calendar_recurring_event(event_id: str):
    """_summary_
    Xóa sự kiện lặp lại trong lịch
    """
    return calendar.delete_recurring_event(event_id)

@tool("get_today_date")
def get_today_date():
    """_summary_
    Lấy ngày hiện tại
    """
    return calendar.get_date_time()

@tool("get_all_forms_name")
def get_all_forms_name():
    """_summary_
    Lấy tên các mẫu đơn có sẵn trên google drive
    """
    return drive.list_files(FORM_FOLDER_ID)

@tool("get_form_link")
def get_form_link(form_name: str):
    """_summary_
    Lấy link mẫu đơn trên google drive
    """
    return drive.get_file_link(form_name, FORM_FOLDER_ID)