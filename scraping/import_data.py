import asyncio
import os
import sys
from tortoise import Tortoise
import pandas as pd

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import database_url
from src.model.quotes import Quote

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'db.sqlite3')

# 2. database_url을 절대 경로를 사용하도록 재정의합니다.
# Tortoise ORM의 SQLite URL 형식에 맞춥니다.
database_url = f"sqlite://{DB_PATH}"
print(f"Database URL set to: {database_url}")

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
    QUOTES_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'quotes.xlsx')
    
    # 🌟 [수정된 부분]: 'data/quotes.xlsx' 대신 QUOTES_FILE_PATH 변수를 사용합니다.
    await import_from_xlsx(Quote, QUOTES_FILE_PATH, {'author': 'author', 'message': 'message'})
    

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
