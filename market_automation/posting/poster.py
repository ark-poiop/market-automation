"""
포스팅 실행 모듈
각 슬롯별 포스팅 로직
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..config import config
from ..rendering.compose import ContentComposer
from .threads_client import ThreadsClient

class MarketPoster:
    def __init__(self):
        self.config = config
        self.composer = ContentComposer()
        self.client = ThreadsClient()
    
    def post_us_close(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """미국 증시 마감 포스팅"""
        try:
            # 데이터 검증
            if not self._validate_us_close_data(data):
                return {"success": False, "error": "Invalid data"}
            
            # 콘텐츠 합성
            indices = data["indices"]
            sectors = data.get("sectors", {})
            movers = data.get("movers", [])
            
            # 섹터 요약 생성
            sector_line = self.composer.compose_sector_summary(
                sectors.get("top", []),
                sectors.get("bottom", [])
            )
            
            # 특징주 요약 생성
            movers_block = self.composer.compose_movers_summary(movers)
            
            # 템플릿 렌더링
            from ..rendering.templates import US_CLOSE
            
            content = US_CLOSE.format(
                date=data["date"],
                spx=self.composer.format_price(indices["spx"]["price"]),
                spx_diff=self.composer.format_percentage(indices["spx"]["diff"], False),
                spx_pct=self.composer.format_percentage(indices["spx"]["pct"]),
                spx_comment=indices["spx"]["comment"],
                ndx=self.composer.format_price(indices["ndx"]["price"]),
                ndx_diff=self.composer.format_percentage(indices["ndx"]["diff"], False),
                ndx_pct=self.composer.format_percentage(indices["ndx"]["pct"]),
                ndx_comment=indices["ndx"]["comment"],
                djia=self.composer.format_price(indices["djia"]["price"]),
                djia_diff=self.composer.format_percentage(indices["djia"]["diff"], False),
                djia_pct=self.composer.format_percentage(indices["djia"]["pct"]),
                djia_comment=indices["djia"]["comment"],
                rty=self.composer.format_price(indices["rty"]["price"]),
                rty_diff=self.composer.format_percentage(indices["rty"]["diff"], False),
                rty_pct=self.composer.format_percentage(indices["rty"]["pct"]),
                rty_comment=indices["rty"]["comment"],
                sector_line=sector_line,
                movers_block=movers_block
            )
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "us_close"
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "us_close"}
    
    def post_kr_preopen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 개장 전 포스팅"""
        try:
            # 데이터 검증
            if not self._validate_kr_preopen_data(data):
                return {"success": False, "error": "Invalid data"}
            
            # 템플릿 렌더링
            from ..rendering.templates import KR_PREOPEN
            
            content = KR_PREOPEN.format(
                date=data["date"],
                spx_pct=self.composer.format_percentage(data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(data["us_wrap"]["djia_pct"]),
                k200f=self.composer.format_price(data["futures"]["k200f"]),
                es=self.composer.format_price(data["futures"]["es"]),
                nq=self.composer.format_price(data["futures"]["nq"]),
                usdkrs=self.composer.format_price(data["macro"]["usdkrs"]),
                wti=self.composer.format_price(data["macro"]["wti"]),
                ust10y=self.composer.format_price(data["macro"]["ust10y"]),
                today_events=" / ".join(data["today_events"]),
                focus_sectors="·".join(data["focus_sectors"]),
                risks=", ".join(data["risks"])
            )
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "kr_preopen"
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "kr_preopen"}
    
    def _validate_us_close_data(self, data: Dict[str, Any]) -> bool:
        """미국 증시 데이터 검증"""
        required_fields = ["date", "indices"]
        if not all(field in data for field in required_fields):
            return False
        
        required_indices = ["spx", "ndx", "djia", "rty"]
        if not all(idx in data["indices"] for idx in required_indices):
            return False
        
        return True
    
    def _validate_kr_preopen_data(self, data: Dict[str, Any]) -> bool:
        """한국 개장 전 데이터 검증"""
        required_fields = ["date", "us_wrap", "futures", "macro"]
        if not all(field in data for field in required_fields):
            return False
        
        return True
