import os
from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Optional


@dataclass
class QueryInfoStorage:
    auth_secret: str
    base_end_point: str

    def __init__(self, auth_secret: Optional[str] = None, base_end_point: Optional[str] = None):
        load_dotenv()
        self.auth_secret = self._get_env_value(auth_secret, 'JBA_API_AUTH_SECRET')
        self.base_end_point = self._get_env_value(base_end_point, 'BASE_END_POINT')

    def get_auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.auth_secret}"}

    @classmethod
    def _get_env_value(cls, value: Optional[str], env_name: str) -> str:
        load_dotenv()
        if value is None:
            return os.getenv(env_name)
        return value
