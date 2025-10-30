import asyncio
import os
import sys
from tortoise import Tortoise
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# --- 설정 시작 ---
# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (중요!) .env 파일에서 DATABASE_URL을 읽어오도록 load_dotenv() 추가
load_dotenv() 

# config에서 database_url과 MODELS 임포트
from config import database_url
# Question 모델 임포트
from src.model.questions import Question

MODELS = ["src.model.users", "src.model.posts", "src.model.quotes", "src.model.questions", "src.model.bookmarks"]

TARGET_URL = "https://wealthinsight.tistory.com/entry/365%EC%9D%BC-1-%EC%9D%BC-1-%EC%A7%88%EB%AC%B8-%ED%95%98%EB%A3%A8%EB%A5%BC-%EB%A7%88%EB%AC%B4%EB%A6%AC%ED%95%98%EB%A9%B0-%EB%82%98%EC%97%90%EA%B2%8C-%EB%AC%BB%EB%8A%94-%EC%A7%88%EB%AC%B8%EC%9D%98-%ED%9E%98#google_vignette"
# --- 설정 끝 ---

async def scrape_and_save():
    
    if not database_url or not database_url.startswith("postgres"):
        print("FATAL ERROR: DATABASE_URL이 PostgreSQL로 설정되지 않았습니다! .env 파일을 확인하세요.")
        return
        
    print(f"Connecting to RDS: {database_url.split('@')[-1]}") # 비번 빼고 출력
    await Tortoise.init(db_url=database_url, modules={"models": MODELS})

    print(f"Scraping questions from {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"URL 요청 중 오류 발생: {e}")
        await Tortoise.close_connections()
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    data_to_save = []
    tables = soup.find_all('table', {'border': '1'})

    if tables:
        for table in tables:
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 1:
                        question_text = cells[1].get_text(strip=True)
                        if question_text:
                            data_to_save.append(question_text)
    else:
        print("해당 테이블을 찾을 수 없습니다.")
        
    print(f"Found {len(data_to_save)} questions. Saving to RDS...")
    
    created_count = 0
    for question_msg in data_to_save:
        # get_or_create로 중복 데이터 방지
        _, created = await Question.get_or_create(message=question_msg)
        if created:
            created_count += 1
            
    print(f"Finished. {created_count} new questions saved to RDS.")
    await Tortoise.close_connections()
    print("RDS Connection closed.")

if __name__ == "__main__":
    asyncio.run(scrape_and_save())
