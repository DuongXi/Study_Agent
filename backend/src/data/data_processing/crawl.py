import requests
from bs4 import BeautifulSoup
import time
import json
import re
BASE_URL = "http://sis.hust.edu.vn/ModuleProgram/CourseLists.aspx"
GRID_ID = "MainContent_gvCoursesGrid_DXMainTable"

# Lấy các trường ẩn
def get_hidden_fields(soup):
    fields = {}
    for tag in soup.find_all("input", type="hidden"):
        if "name" in tag.attrs:
            fields[tag["name"]] = tag.get("value", "")
    return fields

# Lấy dữ liệu từ bảng
def parse_table_data(soup):
    global course_list
    courses = soup.find_all("tr", class_="dxgvDataRow_SisTheme")
    for course in courses:
        soup1 = BeautifulSoup(str(course), 'html.parser')
        attr = soup1.find_all("td", class_="dxgv")
        if len(attr) == 7:
            course_list.append({'Mã học phần':attr[1].get_text(strip=True),
                                'Tên học phần':attr[2].get_text(strip=True),
                                'Số tín chỉ': attr[4].get_text(strip=True),
                                'TC học phí': attr[5].get_text(strip=True),
                                'Trọng số': attr[6].get_text(strip=True)})
            
course_list = []
session = requests.Session()
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")
up = 3 # số phân trang
grid = 20 # kích thước grid

# Thực hiện lần đầu
hidden_fields = get_hidden_fields(soup)
parse_table_data(soup)

# Bắt đầu crawl từ trang 2
for i in range(405):
    if i == 10: 
        up += 1
        grid += 1
    if i == 100:
        up += 1
        grid += 1
    print(f"Đang tải trang: {i+2}")
    
    # Tạo dữ liệu form
    form_data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": hidden_fields["__VIEWSTATE"],
        "__VIEWSTATEGENERATOR": hidden_fields["__VIEWSTATEGENERATOR"],
        "ctl00$MainContent$gvCoursesGrid$DXKVInput": hidden_fields["ctl00$MainContent$gvCoursesGrid$DXKVInput"],
        "MainContent_cbAcademic_DDDWS": hidden_fields["MainContent_cbAcademic_DDDWS"],
        "ctl00$MainContent$gvCoursesGrid$CallbackState": hidden_fields["ctl00$MainContent$gvCoursesGrid$CallbackState"],
        "__CALLBACKID": "ctl00$MainContent$gvCoursesGrid",
        "__CALLBACKPARAM": f"c0:KV|187;{hidden_fields['ctl00$MainContent$gvCoursesGrid$DXKVInput']};GB|{grid};12|PAGERONCLICK{up}|PN{i+1};",
        "__EVENTVALIDATION": hidden_fields["__EVENTVALIDATION"],
    }
    
    # Tạo header
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0",
    }
    resp = session.post(BASE_URL, data=form_data, headers=headers)
    if resp.text.startswith("0|/*DX*/"):
        import ast
        match = re.search(r"/\*DX\*/\((.*)\)", resp.text)
        if match:
            json_str = match.group(1)
            data = ast.literal_eval(json_str)
            html_text =  data['result']
        else:
            print("Không tìm thấy dữ liệu DX")
    page_soup = BeautifulSoup(html_text, "html5lib")
    parse_table_data(page_soup)

    with open("hocphan.json", "w", encoding="utf-8") as f:
        json.dump(course_list, f, ensure_ascii=False, indent=4)

    time.sleep(3)  # tránh spam server