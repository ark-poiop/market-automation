"""
설정 관리 모듈
환경 변수, YAML 설정 파일 로드
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        self.env = self._load_env()
        self.sectors = self._load_sectors()
    
    def _load_env(self) -> Dict[str, str]:
        """환경 변수 로드"""
        env_file = Path(__file__).parent.parent / ".env"
        env_vars = {}
        
        if env_file.exists():
            print(f"🔧 .env 파일 로드: {env_file}")
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key] = value
                        print(f"  {key}={value}")
        else:
            print(f"⚠️ .env 파일을 찾을 수 없음: {env_file}")
        
        # 환경 변수로 오버라이드
        for key in env_vars:
            if os.getenv(key):
                env_vars[key] = os.getenv(key)
                print(f"  {key} (환경변수로 오버라이드): {os.getenv(key)}")
        
        return env_vars
    
    def _load_sectors(self) -> Dict[str, Any]:
        """섹터 설정 YAML 로드"""
        sectors_file = Path(__file__).parent.parent / "assets" / "sectors.yml"
        
        if sectors_file.exists():
            with open(sectors_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """환경 변수 값 조회"""
        return self.env.get(key, default)
    
    def is_dry_run(self) -> bool:
        """드라이 런 모드 여부"""
        return self.get("DRY_RUN", "1") == "1"
    
    def get_sector_alias(self, english_name: str) -> str:
        """영문 섹터명을 한글명으로 변환"""
        return self.sectors.get("aliases", {}).get(english_name, english_name)
    
    def get_sector_emoji(self, korean_name: str) -> str:
        """한글 섹터명에 해당하는 이모지 반환"""
        return self.sectors.get("emoji", {}).get(korean_name, "")
    
    def get_kis_app_key(self) -> str:
        """한국투자증권 앱키 반환"""
        return self.get("KIS_APP_KEY", "")
    
    def get_kis_app_secret(self) -> str:
        """한국투자증권 앱시크릿 반환"""
        return self.get("KIS_APP_SECRET", "")
    
    def get_kis_vts(self) -> str:
        """한국투자증권 가상/실전 구분"""
        return self.get("KIS_VTS", "REAL")
    
    def get_threads_access_token(self) -> str:
        """Threads 액세스 토큰 반환"""
        return self.get("THREADS_ACCESS_TOKEN", "")
    
    def get_threads_user_id(self) -> str:
        """Threads 사용자 ID 반환"""
        return self.get("THREADS_USER_ID", "")
    
    def get_openai_api_key(self) -> str:
        """OpenAI API 키 반환"""
        return self.get("OPENAI_API_KEY", "")

# 전역 설정 인스턴스
config = Config()
