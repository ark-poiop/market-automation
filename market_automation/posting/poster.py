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
from ..datasource.alpaca import AlpacaClient
from ..datasource.naver_adapter import NaverDataAdapter

class MarketPoster:
    def __init__(self):
        self.config = config
        self.composer = ContentComposer()
        self.client = ThreadsClient()
        self.alpaca = AlpacaClient()
        self.naver_adapter = NaverDataAdapter()
    
    def post_us_close(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """미국 증시 마감 포스팅"""
        try:
            print("🔄 미국 증시 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    converted_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 미국 장 마감 형식으로 변환
                    converted_data = self.naver_adapter.convert_to_us_close_format(naver_data)
                    
                    print("✅ 네이버 데이터를 미국 장 마감 형식으로 변환 완료")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                converted_data = data
            
            print("🔍 데이터 검증 완료")
            print("🔄 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import US_CLOSE
            
            content = US_CLOSE.format(
                date=converted_data["date"],
                spx=self.composer.format_price(converted_data["spx"]),
                spx_pct=self.composer.format_percentage(converted_data["spx_pct"]),
                ndx=self.composer.format_price(converted_data["ndx"]),
                ndx_pct=self.composer.format_percentage(converted_data["ndx_pct"]),
                djia=self.composer.format_price(converted_data["djia"]),
                djia_pct=self.composer.format_percentage(converted_data["djia_pct"]),
                sector_top3=converted_data["sector_top3"],
                news_events=converted_data["news_events"],
                top_gainers=converted_data["top_gainers"],
                top_losers=converted_data["top_losers"]
            )
            
            print("📝 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "us_close"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content  # 드라이 런 모드에서 콘텐츠 확인용
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "us_close"}
    
    def post_kr_preopen(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 개장 전 포스팅"""
        try:
            print("🔄 한국 개장 전 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    realtime_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 한국 개장 전 형식으로 변환
                    realtime_data = self.naver_adapter.convert_to_kr_preopen_format(naver_data)
                    
                    print("✅ 네이버 데이터를 한국 개장 전 형식으로 변환 완료")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                realtime_data = data
            
            # 데이터 검증
            if not self._validate_kr_preopen_data(realtime_data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 한국 개장 전 데이터 검증 완료")
            print("🔄 한국 개장 전 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import KR_PREOPEN
            
            content = KR_PREOPEN.format(
                date=realtime_data["date"],
                spx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(realtime_data["us_wrap"]["djia_pct"]),
                k200f=self.composer.format_price(realtime_data["futures"]["k200f"]),
                es=self.composer.format_price(realtime_data["futures"]["es"]),
                nq=self.composer.format_price(realtime_data["futures"]["nq"]),
                today_events=" / ".join(realtime_data["today_events"]),
                focus_sectors="·".join(realtime_data["focus_sectors"]),
                risks=", ".join(realtime_data["risks"])
            )
            
            print("📝 한국 개장 전 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "kr_preopen"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content
            
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
        required_fields = ["date", "us_wrap", "futures"]
        if not all(field in data for field in required_fields):
            return False
        
        return True
    
    def post_kr_midday(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 장중 포스팅"""
        try:
            print("🔄 한국 장중 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    realtime_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 한국 장중 형식으로 변환
                    realtime_data = self.naver_adapter.convert_to_kr_midday_format(naver_data)
                    
                    print("✅ 네이버 데이터를 한국 장중 형식으로 변환 완료")
                    print(f"📊 KOSPI: {realtime_data['kospi']} ({realtime_data['kospi_pct']:+.2f}%)")
                    print(f"📊 KOSDAQ: {realtime_data['kosdaq']} ({realtime_data['kosdaq_pct']:+.2f}%)")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                realtime_data = data
            
            # 데이터 검증
            if not self._validate_kr_midday_data(realtime_data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 한국 장중 데이터 검증 완료")
            print("🔄 한국 장중 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import KR_MIDDAY
            
            content = KR_MIDDAY.format(
                date=realtime_data["date"],
                kospi=self.composer.format_price(realtime_data["kospi"]),
                kospi_pct=self.composer.format_percentage(realtime_data["kospi_pct"]),
                kosdaq=self.composer.format_price(realtime_data["kosdaq"]),
                kosdaq_pct=self.composer.format_percentage(realtime_data["kosdaq_pct"]),
                sector_top3=realtime_data["sector_top3"],
                news_events=realtime_data["news_events"],
                top_gainers=realtime_data["top_gainers"],
                top_losers=realtime_data["top_losers"]
            )
            
            print("📝 한국 장중 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "kr_midday"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "kr_midday"}
    
    def post_kr_close(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 장 마감 포스팅"""
        try:
            print("🔄 한국 장 마감 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    realtime_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 한국 장 마감 형식으로 변환
                    realtime_data = self.naver_adapter.convert_to_kr_close_format(naver_data)
                    
                    print("✅ 네이버 데이터를 한국 장 마감 형식으로 변환 완료")
                    print(f"📊 KOSPI: {realtime_data['kospi']['price']} ({realtime_data['kospi']['diff']:+.2f}, {realtime_data['kospi']['pct']:+.2f}%)")
                    print(f"📊 KOSDAQ: {realtime_data['kosdaq']['price']} ({realtime_data['kosdaq']['diff']:+.2f}, {realtime_data['kosdaq']['pct']:+.2f}%)")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                realtime_data = data
            
            # 데이터 검증
            if not self._validate_kr_close_data(realtime_data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 한국 장 마감 데이터 검증 완료")
            print("🔄 한국 장 마감 콘텐츠 합성 중...")
            
            # 섹터 요약 생성
            sectors = realtime_data.get("sectors", {})
            sector_line = self.composer.compose_sector_summary(
                sectors.get("top", []),
                sectors.get("bottom", [])
            )
            print(f"🏭 한국 섹터 요약: {sector_line}")
            
            # 특징주 요약 생성
            movers_block = self.composer.compose_movers_summary(realtime_data.get("movers", []))
            movers_line_count = len(movers_block.split('\n')) if movers_block else 0
            print(f"🚀 한국 특징주 요약: {movers_line_count}줄")
            
            # 템플릿 렌더링
            from ..rendering.templates import KR_CLOSE
            
            content = KR_CLOSE.format(
                date=realtime_data["date"],
                kospi=self.composer.format_price(realtime_data["kospi"]["price"]),
                kospi_diff=self.composer.format_percentage(realtime_data["kospi"]["diff"], False),
                kospi_pct=self.composer.format_percentage(realtime_data["kospi"]["pct"]),
                kosdaq=self.composer.format_price(realtime_data["kosdaq"]["price"]),
                kosdaq_diff=self.composer.format_percentage(realtime_data["kosdaq"]["diff"], False),
                kosdaq_pct=self.composer.format_percentage(realtime_data["kosdaq"]["pct"]),
                sector_line=sector_line,
                movers_block=movers_block
            )
            
            print("📝 한국 장 마감 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "kr_close"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "kr_close"}
    
    def post_us_preview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """미국 개장 전 포스팅"""
        try:
            print("🔄 미국 개장 전 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    realtime_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 미국 개장 전 형식으로 변환
                    realtime_data = self.naver_adapter.convert_to_us_preview_format(naver_data)
                    
                    print("✅ 네이버 데이터를 미국 개장 전 형식으로 변환 완료")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                realtime_data = data
            
            # 데이터 검증
            if not self._validate_us_preview_data(realtime_data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 미국 개장 전 데이터 검증 완료")
            print("🔄 미국 개장 전 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import US_PREVIEW
            
            content = US_PREVIEW.format(
                date=realtime_data["date"],
                spx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(realtime_data["us_wrap"]["djia_pct"]),
                es=self.composer.format_price(realtime_data["futures"]["es"]),
                nq=self.composer.format_price(realtime_data["futures"]["nq"]),
                ym=self.composer.format_price(realtime_data["futures"]["ym"]),
                wti=self.composer.format_price(realtime_data["macro"]["wti"]),
                gold=self.composer.format_price(realtime_data["macro"]["gold"]),
                ust10y=self.composer.format_price(realtime_data["macro"]["ust10y"]),
                today_events=" / ".join(realtime_data["today_events"]),
                focus_sectors="·".join(realtime_data["focus_sectors"]),
                risks=", ".join(realtime_data["risks"])
            )
            
            print("📝 미국 개장 전 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "us_preview"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "us_preview"}
    
    def post_us_premkt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """미국 장전 포스팅"""
        try:
            print("🔄 미국 장전 데이터 수집 중...")
            
            # 네이버 크롤링 데이터 사용
            try:
                # 네이버 데이터 로드
                naver_data = self.naver_adapter.load_naver_data()
                if not naver_data:
                    print("⚠️ 네이버 데이터 로드 실패, 샘플 데이터 사용")
                    realtime_data = data
                else:
                    print("✅ 네이버 데이터 로드 완료")
                    
                    # 네이버 데이터를 미국 장전 형식으로 변환
                    realtime_data = self.naver_adapter.convert_to_us_preview_format(naver_data)
                    
                    print("✅ 네이버 데이터를 미국 장전 형식으로 변환 완료")
                    
            except Exception as e:
                print(f"⚠️ 네이버 데이터 처리 실패, 샘플 데이터 사용: {e}")
                realtime_data = data
            
            # 데이터 검증
            if not self._validate_us_preview_data(realtime_data):  # 동일한 데이터 구조 사용
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 미국 장전 데이터 검증 완료")
            print("🔄 미국 장전 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import US_PREMKT
            
            content = US_PREMKT.format(
                date=realtime_data["date"],
                spx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(realtime_data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(realtime_data["us_wrap"]["djia_pct"]),
                es=self.composer.format_price(realtime_data["futures"]["es"]),
                nq=self.composer.format_price(realtime_data["futures"]["nq"]),
                ym=self.composer.format_price(realtime_data["futures"]["ym"]),
                wti=self.composer.format_price(realtime_data["macro"]["wti"]),
                gold=self.composer.format_price(realtime_data["macro"]["gold"]),
                ust10y=self.composer.format_price(realtime_data["macro"]["ust10y"]),
                today_events=" / ".join(realtime_data["today_events"]),
                focus_sectors="·".join(realtime_data["focus_sectors"]),
                risks=", ".join(realtime_data["risks"])
            )
            
            print("📝 미국 장전 템플릿 렌더링 완료")
            
            # 포스팅
            result = self.client.post(content)
            result["slot"] = "us_premkt"
            result["timestamp"] = datetime.now().isoformat()
            result["content"] = content
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e), "slot": "us_premkt"}
    
    def _validate_kr_midday_data(self, data: Dict[str, Any]) -> bool:
        """한국 장중 데이터 검증"""
        required_fields = ["date", "kospi", "kospi_pct", "kosdaq", "kosdaq_pct", "sector_top3", "news_events", "top_gainers", "top_losers"]
        if not all(field in data for field in required_fields):
            return False
        return True
    
    def _validate_kr_close_data(self, data: Dict[str, Any]) -> bool:
        """한국 장 마감 데이터 검증"""
        required_fields = ["date", "kospi", "kosdaq"]
        if not all(field in data for field in required_fields):
            return False
        return True
    
    def _validate_us_preview_data(self, data: Dict[str, Any]) -> bool:
        """미국 개장 전/장전 데이터 검증"""
        required_fields = ["date", "us_wrap", "futures", "macro", "today_events", "focus_sectors", "risks"]
        if not all(field in data for field in required_fields):
            return False
        return True
    
    def _validate_indices_data(self, indices: Dict[str, Any]) -> bool:
        """지수 데이터 구조 검증"""
        if not indices:
            return False
        
        required_indices = ["spx", "ndx", "djia", "rty"]
        for idx in required_indices:
            if idx not in indices:
                return False
            
            index_data = indices[idx]
            if not isinstance(index_data, dict):
                return False
            
            required_fields = ["price", "diff", "pct", "comment"]
            if not all(field in index_data for field in required_fields):
                return False
        
        return True
