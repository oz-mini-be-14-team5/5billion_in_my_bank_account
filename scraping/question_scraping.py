import requests
from bs4 import BeautifulSoup
import sqlite3 

TARGET_URL = "https://wealthinsight.tistory.com/entry/365%EC%9D%BC-1-%EC%9D%BC-1-%EC%A7%88%EB%AC%B8-%ED%95%98%EB%A3%A8%EB%A5%BC-%EB%A7%88%EB%AC%B4%EB%A6%AC%ED%95%98%EB%A9%B0-%EB%82%98%EC%97%90%EA%B2%8C-%EB%AC%BB%EB%8A%94-%EC%A7%88%EB%AC%B8%EC%9D%98-%ED%9E%98#google_vignette"

try:
    response = requests.get(TARGET_URL)
    response.raise_for_status() #
    html_content = response.text
except requests.exceptions.RequestException as e:
    print(f"URL 요청 중 오류 발생: {e}")
    exit()

soup = BeautifulSoup(html_content, 'html.parser')

data_to_save = []
tables = soup.find_all('table', {'border': '1'})

if tables:
    print(f"페이지에서 {len(tables)}개의 'border=1' 테이블을 찾았습니다.")
    for i, table in enumerate(tables):
        print(f"\n--- 테이블 {i+1} 처리 중 ---")
        tbody = table.find('tbody')
        
        if tbody:
            print("<tbody> 내용물을 성공적으로 찾았습니다.")
            rows = tbody.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 1:
                    question_text = cells[1].get_text(strip=True)
                    data_to_save.append(question_text)
        else:
            print("<tbody> 태그를 찾을 수 없습니다.")
else:
    print("해당 테이블을 찾을 수 없습니다.")

print("\n스크래핑된 질문 목록:")
print(data_to_save)


conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
 
for question in data_to_save:
    cursor.execute("INSERT INTO question (message) VALUES (?)", (question,))
 
conn.commit()
conn.close()
 
print(f"\n데이터베이스에 {len(data_to_save)}개의 질문을 성공적으로 저장했습니다.")