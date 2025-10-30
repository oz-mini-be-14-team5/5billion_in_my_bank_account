import os

password_salt = os.environ.get("PASSWORD_SALT", "null")
jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "null")
jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
jwt_access_min = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))
jwt_refresh_day = int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", "14"))
storage_path = os.environ.get("STORAGE_PATH", "./storage")
database_url = os.environ.get("DATABASE_URL", "postgres://postgres:qwer1234!@database-1.chc88eiu64kp.ap-northeast-2.rds.amazonaws.com:5432/postgres")
debug_mode = os.environ.get("DEBUG_MODE", "false").lower() == "true"
host = os.environ.get("HOST", "0.0.0.0")
port = int(os.environ.get("PORT", "8000"))
