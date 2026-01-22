import os
from dotenv import load_dotenv

load_dotenv(".env")

# 資料庫設定
# 優先使用環境變數，否則使用預設值（SQLite 用於開發）
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
DB_NAME = os.getenv("DB_NAME", "db.sqlite3")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

if DB_ENGINE == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }
else:
    # 預設使用 SQLite（開發環境）
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), DB_NAME),
        }
    }
