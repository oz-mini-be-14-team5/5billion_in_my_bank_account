import requests
from bs4 import BeautifulSoup as bs
import time
import random
import csv


START_NO = 1 
END_NO = 6118

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}
BASE_URL = 'https://gall.dcinside.com/mgallery/board/view/?id=quotes&no='

csv_file = open('dc_quotes_data.csv', 'a', newline='', encoding='utf-8-sig')
writer = csv.writer(csv_file)


writer.writerow(['No.', 'quote', 'author']) 
print("CSV 파일 'dc_quotes_data.csv' 준비 완료.\n")


for post_no in range(START_NO, END_NO + 1):
    url = f"{BASE_URL}{post_no}"
    time.sleep(random.uniform(2, 4)) 

    try:
        response = requests.get(url, headers=HEADERS)
        html = bs(response.text, 'html.parser')

        content_tag = html.find(class_='write_div')
        nickname_tag = html.find(class_='nickname') 

        dc_nickname = nickname_tag.get_text(strip=True) if nickname_tag else None
        
        if content_tag and dc_nickname == "Talnos":
            content = content_tag.get_text(strip=True, separator='\n')
            
            if '-' in content:
                last_hyphen_index = content.rfind('-')
                quote_text = content[:last_hyphen_index].strip()
                author_name = content[last_hyphen_index + 1:].strip()
            else:
                quote_text = content
                author_name = "정보 없음"

            writer.writerow([post_no, quote_text, author_name])
            
            print(f"[SUCCESS] {post_no}번 글 '{quote_text[:15]}...' 저장 완료.")
        
        elif content_tag is None:
            print(f"[SKIP] {post_no}번 글: 삭제되었거나 접근 불가능.")
        
        else:
             print(f"[SKIP] {post_no}번 글: 작성자 '{dc_nickname}' 필터링 제외.")


    except Exception as e:
        print(f"[Error] {post_no}번 글 처리 중 오류 발생: {type(e).__name__}") 

csv_file.close()
print("\n---완료 ---")