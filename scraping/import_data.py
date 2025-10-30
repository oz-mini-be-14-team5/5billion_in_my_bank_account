import asyncio
import os
import sys
from tortoise import Tortoise
import pandas as pd
from dotenv import load_dotenv

# --- 설정 시작 ---
# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (중요!) .env 파일에서 DATABASE_URL을 읽어오도록 load_dotenv() 추가
load_dotenv() 

# (수정!) config에서 database_url만 가져오기
from config import database_url

# (수정!) MODELS 리스트를 main.py에서 복사해와서 직접 정의
MODELS = ["src.model.users", "src.model.posts", "src.model.quotes", "src.model.questions", "src.model.bookmarks"]

from src.model.quotes import Quote

# 프로젝트 루트 경로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (수정!) 님이 말씀하신 엑셀 파일 경로로 변경
QUOTES_FILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'quotes.xlsx')

# 엑셀 헤더와 모델 필드 매핑 (원본 스크립트 기준)
FIELD_MAPPING = {'author': 'author', 'message': 'message'}
# --- 설정 끝 ---


async def import_from_xlsx(model, filepath: str, field_mapping: dict):
    """
    (수정!) XLSX 파일로부터 데이터를 읽어 DB에 저장하는 함수
    """
    print(f"Importing data for {model.__name__} from {filepath}...")
    created_count = 0
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # (수정!) pd.read_csv -> pd.read_excel
    df = pd.read_excel(filepath) 
    # NaN 값을 빈 문자열로 대체
    df = df.fillna('')

    for index, row in df.iterrows():
        try:
            data_to_create = {model_field: row[xlsx_header] for model_field, xlsx_header in field_mapping.items()}

            # get_or_create를 사용하여 중복 데이터 방지
            _, created = await model.get_or_create(**data_to_create)
            if created:
                created_count += 1
        except KeyError as e:
            print(f"  [Warning] 엑셀 파일에 '{e}' 컬럼이 없습니다. 건너뜁니다.")
        except Exception as e:
            print(f"  [Error] 데이터 삽입 중 오류 발생: {e}")

    print(f"Finished importing for {model.__name__}. {created_count} new records created.")

async def run():
    """데이터베이스를 초기화하고 모든 임포트 작업을 실행합니다."""
    if not database_url or not database_url.startswith("postgres"):
        print("FATAL ERROR: DATABASE_URL이 PostgreSQL로 설정되지 않았습니다! .env 파일을 확인하세요.")
        return
        
    print(f"Connecting to RDS: {database_url.split('@')[-1]}") # 비번 빼고 출력
    await Tortoise.init(db_url=database_url, modules={"models": MODELS})
    
    # 명언 데이터 임포트 실행
    await import_from_xlsx(Quote, QUOTES_FILE_PATH, FIELD_MAPPING)
    
    await Tortoise.close_connections()
    print("RDS Connection closed.")

if __name__ == "__main__":
    asyncio.run(run())
