import os
from sql.sql_tool import DatabaseConnector
from mcp.server.fastmcp import FastMCP
from typing import Literal
from csv_read.csv_tool import CSVReader
from vector_db.vector_tool import WeaviateRetriver
from google_calendar.calendar_tool import Calendar
from google_drive.drive_tool import Drive

from tool_config import *
import json
from dotenv import load_dotenv
load_dotenv()
import sys
sys.stdout.reconfigure(encoding='utf-8')

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
csv_reader = CSVReader(EXCEL_PATH)
calendar = Calendar()
drive = Drive()

mcp = FastMCP(name="Assistant")

@mcp.tool(
    name="get_csv_column",
    description="Lấy các cột trong file thời khoá biểu"
)
def get_csv_column():
    """_summary_
    Lấy các cột trong file thời khoá biểu.
    """
    return csv_reader.columns

@mcp.tool(
    name="get_csv_head_rows",
    description="Lấy thông tin một số hàng đầu trong file thời khoá biểu"
)
def get_csv_head_rows():
    """_summary_
    Lấy thông tin một số hàng đầu trong file thời khoá biểu.
    """
    data_dict=csv_reader.head.to_dict()
    return json.dumps(data_dict, ensure_ascii=False)


@mcp.tool(
    name="filter_csv_data_by_items",
    description="Lấy thông tin thời khoá biểu dựa trên tên hoặc mã các học phần"
)
def filter_data_by_subject(selected_items: list, selected_column: str):
    """_summary_
    Lấy thông tin thời khoá biểu dựa trên tên hoặc mã các học phần

    Args:
        selected_items (list): Tên hoặc mã các học phần cần lọc
        selected_column (str): Tên cột chứa thông tin tương ứng
    
    Returns: Bảng gồm thông tin học phần trong thời khoá biểu
    """
    data_dict=csv_reader.filter_data_by_items(selected_items=selected_items, selected_column=selected_column).to_dict()
    return json.dumps(data_dict, ensure_ascii=False)

@mcp.tool(
    name="list_database_tables",
    description="Lấy thông tin các bảng và kết nối trong database"
)
def list_database_tables():
    """_summary_
    Lấy thông tin các bảng và kết nối trong database.
    """
    conn = DatabaseConnector(
        db_type=DATABASE_TYPE,
        host="localhost",
        user="root",
        password=os.getenv("DATABASE_PASSWORD"),
        database="chuong_trinh_dao_tao"
    )
    return conn.get_metadata()

@mcp.tool(
    name="get_database_data",
    description="Lấy dữ liệu từ database"
)
def get_database_data(query: str):
    """
    Lấy dữ liệu từ database.
    
    Args:
        query (str): Câu truy vấn SQL để lấy dữ liệu.
    """
    conn = DatabaseConnector(
        db_type=DATABASE_TYPE,
        host="localhost",
        user="root",
        password=os.getenv("DATABASE_PASSWORD"),
        database="chuong_trinh_dao_tao"
    )
    return conn.get_data(query=query)

@mcp.tool(
    name="doc_retrive",
    description="Tìm kiếm thông tin liên quan đến đại học trong vector database"
)
def doc_retrive(query: str):
    """_summary_
    Tìm kiếm thông tin liên quan đến đại học trong vector database

    Args:
        query (str): Câu hỏi của người dùng
    """
    retriver = WeaviateRetriver(WEAVIATE_URL,WEAVIATE_API_KEY)
    return {"documents":retriver.search(query, 5)}

@mcp.tool(
    name="get_calendar_recurring_events",
    description="Lấy thông tin các sự kiện lặp lại trong lịch"
)
def get_calendar_recurring_events():
    """_summary_
    Lấy thông tin các sự kiện lặp lại trong lịch
    """
    return calendar.get_recurring_event()

@mcp.tool(
    name="get_calendar_upcoming_events",
    description="Lấy thông tin các sự kiện sắp tới trong lịch"
)
def get_calendar_upcoming_events():
    """_summary_
    Lấy thông tin các sự kiện sắp tới trong lịch
    """
    return calendar.get_upcoming_events()

@mcp.tool(
    name="create_calendar_event",
    description="Tạo sự kiện trong lịch"
)   
def create_calendar_event(summary: str, location: str, description: str, start: str, end: str):
    """_summary_
    Tạo sự kiện trong lịch
    """
    event = calendar.generate_event(summary, location, description, start, end)
    return calendar.create_event(event)

@mcp.tool(
    name="create_calendar_recurring_event",
    description="Tạo sự kiện lặp lại trong lịch"
)   
def create_calendar_recurring_event(summary: str, location: str, description: str, start: str, end: str, freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], count: int):
    """_summary_
    Tạo sự kiện lặp lại trong lịch
    """
    event = calendar.generate_recurring_event(summary, location, description, start, end, freq, count)
    return calendar.create_event(event)

@mcp.tool(
    name="update_calendar_event",
    description="Cập nhật sự kiện trong lịch"
)
def update_calendar_event(event_id: str, summary: str, location: str, description: str, start: str, end: str, freq: Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"], count: int):
    """_summary_
    Cập nhật sự kiện trong lịch
    """
    event = calendar.generate_event(summary, location, description, start, end, freq, count)
    return calendar.update_event(event_id, event)

@mcp.tool(
    name="delete_calendar_event",
    description="Xóa sự kiện trong lịch"
)
def delete_calendar_event(event_id: str):
    """_summary_
    Xóa sự kiện trong lịch
    """
    return calendar.delete_event(event_id)

@mcp.tool(
    name="delete_calendar_recurring_event",
    description="Xóa sự kiện lặp lại trong lịch"
)
def delete_calendar_recurring_event(event_id: str):
    """_summary_
    Xóa sự kiện lặp lại trong lịch
    """
    return calendar.delete_recurring_event(event_id)

@mcp.tool(
    name="get_today_date",
    description="Lấy ngày hiện tại"
)
def get_today_date():
    """_summary_
    Lấy ngày hiện tại
    """
    return calendar.get_date_time()

@mcp.tool(
    name="get_all_forms_name",
    description="Lấy tên các mẫu đơn có sẵn trên google drive"
)
def get_all_forms_name():
    """_summary_
    Lấy tên các mẫu đơn có sẵn trên google drive
    """
    return drive.list_files(FORM_FOLDER_ID)

@mcp.tool(
    name="get_form_link",
    description="Lấy link mẫu đơn trên google drive"
)
def get_form_link(form_name: str):
    """_summary_
    Lấy link mẫu đơn trên google drive
    """
    return drive.get_file_link(form_name, FORM_FOLDER_ID)

if __name__ == "__main__":
    mcp.run()