from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy import text
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()
import os
class DatabaseConnector:
    def __init__(self,
                 db_type,
                 host=None,
                 database=None,
                 user=None,
                 password=None,
                 port=None,
                 driver=None):
        self.db_type = db_type.lower()
        self.database = database
        connection_url = ""
        
        # Tạo chuỗi kết nối phù hợp với từng CSDL
        if self.db_type == "mysql":
            
            connection_url = URL.create(
                "mysql+pymysql",
                username=user,
                password=password,
                host=host,
                port=port or 3306,
                database=database,
                query={"charset": "utf8mb4"}
            )

        elif self.db_type == "postgresql":
            
            connection_url = URL.create(
                "postgresql+psycopg2 ",
                username=user,
                password=password,
                host=host,
                port= port or 5432,
                database=database,
            )

        elif self.db_type == "sqlite":

            connection_url = URL.create(
                "sqlite ",
                database=database,
            )

        elif self.db_type == "sqlserver":
            
            connection_url = URL.create(
                "mssql+pyodbc",
                username=user,
                password=password,
                host=host,
                port= port or 1433,
                database=database,
                query={"driver": driver or "SQL Server"},
            )

        else:
            raise ValueError("Database type not supported!")

        if connection_url:
            self.engine = create_engine(connection_url)
  
        # Tạo session
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        print(f"Kết nối {self.db_type} thành công!")
    
    def get_data(self, query):
    # Thực hiện truy vấn và trả về dữ liệu        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                table = [tuple(result.keys()),result.fetchall()]
                return str(table)
        except Exception as e:
            return f"Error: {e}"

    def get_metadata(self):
        try:
            metadata = MetaData()

            # Lấy metadata của tất cả các bảng trong database
            metadata.reflect(bind=self.engine)

            # Truy xuất thông tin
            schema_text = ""
            for table in metadata.tables.values():
                metadata_text = f"Table: {table.name}\n"
                for column in table.columns:
                    if str(column.type) == "ENUM":
                        
                        metadata_text += f"Column: {column.name}, Type: {column.type}({', '.join(column.type.enums)})\n"
                    else:
                        metadata_text += f"Column: {column.name}, Type: {column.type}\n"
                
                # Lấy các khóa ngoại
                for fk in table.foreign_keys:
                    metadata_text += f"Foreign Key: {fk.name}, References: {fk.column.table.name}({fk.column.name})\n"
                schema_text += metadata_text
            return schema_text
        except Exception as e:
            return f"Error: {e}"
    
    def get_json_data(self, query):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                rows_json = [dict(row._mapping) for row in rows]
                return json.dumps(rows_json)
        except Exception as e:
            return f"Error: {e}"

    def close(self):
        # Đóng kết nối
        self.session.close()

if __name__ == "__main__":
    database = DatabaseConnector(
        db_type="mysql",
        host="localhost",
        user="root",
        password=os.getenv("DATABASE_PASSWORD"),
        database="chuong_trinh_dao_tao"
    )
    print(database.get_metadata())