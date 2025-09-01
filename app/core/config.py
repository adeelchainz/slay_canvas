import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path('.') / '.env')
except Exception:
    pass


class Settings:
    DATABASE_URL: str
    SECRET_KEY: str
    GOOGLE_CLIENT_ID: Optional[str]
    GOOGLE_CLIENT_SECRET: Optional[str]
    FRONTEND_ORIGIN: str

    def __init__(self):
        self.DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://user:pass@localhost:5432/mediaboard')
        self.SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-me-with-secure-random')
        self.GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
        self.GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        self.FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', 'http://localhost:3000')


settings = Settings()
