from flask import Flask, render_template, request, make_response
import pdfkit
import html
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

app = Flask(__name__)

# Cấu hình pdfkit
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        selectors = request.form.getlist('selectors[]')
        selector_names = request.form.getlist('selector_name[]')

        if len(selectors) != len(selector_names):
            return render_template('results.html', table=None, error="Mismatch between number of selectors and names")

        # Khởi tạo trình duyệt với ChromeDriver
        service = Service("chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        sleep(random.randint(5, 10))  # Dừng để trang web tải hết

        # Khởi tạo danh sách chứa kết quả cho các selector
        all_data = []

        # Duyệt qua tất cả các selector được nhập từ form
        for selector in selectors:
            elements = [elem.text for elem in driver.find_elements(By.CSS_SELECTOR, selector)]
            all_data.append(elements)

        driver.quit()

        # Xác định độ dài tối thiểu của các danh sách
        min_length = min(len(data) for data in all_data)

        # Cắt mỗi danh sách theo min_length để đảm bảo chúng có cùng độ dài
        all_data = [data[:min_length] for data in all_data]

        # Tạo DataFrame với các cột từ dữ liệu
        data_dict = {'Index': list(range(1, min_length + 1))}
        for i, name in enumerate(selector_names):
            data_dict[name] = all_data[i]

        df = pd.DataFrame(data_dict)

        # Chuyển DataFrame thành HTML
        table_html = df.to_html(index=False)

        return render_template('results.html', table=table_html)

    return render_template('index.html')



@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    table_html = request.form.get('table_html')

    # Cấu hình tùy chọn cho pdfkit
    pdf_options = {
        'no-outline': None,
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ]
    }

    # Đảm bảo rằng đường dẫn đến wkhtmltopdf được cấu hình chính xác
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    # Tạo file PDF từ HTML với các tùy chọn cấu hình
    pdf = pdfkit.from_string(table_html, False, configuration=pdfkit_config, options=pdf_options)

    # Tạo phản hồi để tải xuống file PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=results.pdf'

    return response


if __name__ == '__main__':
    app.run(debug=True)

