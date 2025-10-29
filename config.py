import os

password_salt = os.environ.get("PASSWORD_SALT", "null")
jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "null")
jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
jwt_access_min = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))
jwt_refresh_day = int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", "14"))
storage_path = os.environ.get("STORAGE_PATH", "./storage")
database_url = os.environ.get("DATABASE_URL", "sqlite://db.sqlite3") # DB 주소 연결해주세요 (테스트는 기본주소 대응가능)
debug_mode = os.environ.get("DEBUG_MODE", "false").lower() == "true"
host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", "8000"))