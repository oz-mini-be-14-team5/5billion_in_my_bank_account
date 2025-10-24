import uvicorn
from tortoise import Tortoise

from fastapi import FastAPI

from config import database_url, debug_mode, host, port
from src.router.static import router as static_router
from src.router.users import router as user_router

MODELS = ["src.model.users", "src.model.posts"]
ROUTERS = [user_router, static_router]

# 앱 수명 주기 설정
async def lifespan(app: FastAPI):
    # 데이터베이스 초기화
    await Tortoise.init(db_url=database_url, modules={"models": MODELS})
    await Tortoise.generate_schemas() # DB 스키마 생성
    yield
    # 데이터베이스 연결 종료
    await Tortoise.close_connections()

# app 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# 라우터 등록
for router in ROUTERS:
    app.include_router(router)

# 헬스체크 엔드포인트
@app.route("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=port, reload=debug_mode)
