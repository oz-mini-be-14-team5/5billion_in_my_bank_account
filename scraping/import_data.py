import asyncio
import os
import sys
from tortoise import Tortoise
import pandas as pd

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import database_url
from src.model.quotes import Quote

MODELS = ["src.model.users", "src.model.posts", "src.model.quotes", "src.model.questions", "src.model.bookmarks"]

async def import_from_xlsx(model, filepath: str, field_mapping: dict):
    """
    XLSX 파일로부터 데이터를 읽어 DB에 저장하는 범용 함수
    :param model: Tortoise ORM 모델 클래스
    :param filepath: XLSX 파일 경로
    :param field_mapping: XLSX 헤더와 모델 필드를 매핑하는 딕셔너리
    """
    print(f"Importing data for {model.__name__} from {filepath}...")
    created_count = 0
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    df = pd.read_excel(filepath)
    # NaN 값을 빈 문자열로 대체
    df = df.fillna('')

    for index, row in df.iterrows():
        data_to_create = {model_field: row[xlsx_header] for model_field, xlsx_header in field_mapping.items()}
        
        # get_or_create를 사용하여 중복 데이터 방지
        _, created = await model.get_or_create(**data_to_create)
        if created:
            created_count += 1
    
    print(f"Finished importing for {model.__name__}. {created_count} new records created.")

async def run():
    """데이터베이스를 초기화하고 모든 임포트 작업을 실행합니다."""
    await Tortoise.init(db_url=database_url, modules={"models": MODELS})
    await Tortoise.generate_schemas()

    # 명언 데이터 임포트
    # CSV를 사용하려면 아래 줄의 주석을 해제하세요.
    # await import_from_csv(Quote, 'data/quotes.csv', {'author': 'author', 'message': 'message'})
    await import_from_xlsx(Quote, 'data/quotes.xlsx', {'author': 'author', 'message': 'message'})
    

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
