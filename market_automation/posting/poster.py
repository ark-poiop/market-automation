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
from ..datasource.kis import KISClient

class MarketPoster:
    def __init__(self):
        self.config = config
        self.composer = ContentComposer()
        self.client = ThreadsClient()
        self.alpaca = AlpacaClient()
        self.kis = KISClient()
    
    def post_us_close(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """미국 증시 마감 포스팅"""
        try:
            print("🔄 미국 증시 데이터 수집 중...")
            
            # Alpaca API에서 실제 데이터 수집
            try:
                us_indices = self.alpaca.get_us_indices()
                if "error" in us_indices:
                    print(f"⚠️ Alpaca API 오류, 샘플 데이터 사용: {us_indices['error']}")
                    # API 오류 시 샘플 데이터 사용
                    if not self._validate_us_close_data(data):
                        return {"success": False, "error": "Invalid sample data"}
                    indices = data["indices"]
                    sectors = data.get("sectors", {})
                    movers = data.get("movers", [])
                else:
                    print("✅ Alpaca API에서 미국 지수 데이터 수집 완료")
                    print(f"🔍 수집된 데이터 구조: {list(us_indices.keys())}")
                    
                    # 첫 번째 지수의 상세 구조 확인
                    first_index = list(us_indices.keys())[0] if us_indices else None
                    if first_index:
                        print(f"📊 {first_index} 데이터 구조: {us_indices[first_index]}")
                    
                    indices = us_indices
                    
                    # 섹터 및 특징주 데이터도 수집
                    sectors = self.alpaca.get_sector_performance()
                    if "error" in sectors:
                        print(f"⚠️ 섹터 데이터 수집 실패, 기본값 사용: {sectors['error']}")
                        sectors = {"top": [], "bottom": []}
                    
                    movers = self.alpaca.get_top_movers(5)
                    if movers and "error" in movers[0]:
                        print(f"⚠️ 특징주 데이터 수집 실패, 기본값 사용: {movers[0]['error']}")
                        movers = []
            except Exception as e:
                print(f"⚠️ Alpaca API 연결 실패, 샘플 데이터 사용: {e}")
                # API 연결 실패 시 샘플 데이터 사용
                if not self._validate_us_close_data(data):
                    return {"success": False, "error": "Invalid sample data"}
                indices = data["indices"]
                sectors = data.get("sectors", {})
                movers = data.get("movers", [])
            
            # 데이터 구조 검증 및 정규화
            if not self._validate_indices_data(indices):
                print("⚠️ 지수 데이터 구조 오류, 샘플 데이터 사용")
                indices = data["indices"]
                sectors = data.get("sectors", {})
                movers = data.get("movers", [])
            
            print("🔍 데이터 검증 완료")
            print("🔄 콘텐츠 합성 중...")
            
            # 섹터 요약 생성
            sector_line = self.composer.compose_sector_summary(
                sectors.get("top", []),
                sectors.get("bottom", [])
            )
            print(f"🏭 섹터 요약: {sector_line}")
            
            # 특징주 요약 생성
            movers_block = self.composer.compose_movers_summary(movers)
            movers_line_count = len(movers_block.split('\n')) if movers_block else 0
            print(f"🚀 특징주 요약: {movers_line_count}줄")
            
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
        required_fields = ["date", "us_wrap", "futures"]
        if not all(field in data for field in required_fields):
            return False
        
        return True
    
    def post_kr_midday(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 장중 포스팅"""
        try:
            print("🔄 한국 장중 데이터 수집 중...")
            
            # 한국투자증권 API에서 실시간 데이터 수집
            try:
                # 한국 시장 데이터 일괄 조회
                market_data = self.kis.get_kr_market_data()
                if "error" in market_data:
                    print(f"⚠️ 한국 시장 데이터 수집 실패, 샘플 데이터 사용: {market_data['error']}")
                    kospi_data = data["kospi"]
                    kosdaq_data = data["kosdaq"]
                else:
                    print("✅ 한국 시장 실시간 데이터 수집 완료")
                    kospi_data = market_data["kospi"]
                    kosdaq_data = market_data["kosdaq"]
                    exchange_data = market_data["exchange"]
                    
                    if "error" not in kospi_data:
                        print("✅ KOSPI 실시간 데이터 수집 완료")
                    else:
                        print(f"⚠️ KOSPI 데이터 수집 실패, 샘플 데이터 사용: {kospi_data['error']}")
                        kospi_data = data["kospi"]
                    
                    if "error" not in kosdaq_data:
                        print("✅ KOSDAQ 실시간 데이터 수집 완료")
                    else:
                        print(f"⚠️ KOSDAQ 데이터 수집 실패, 샘플 데이터 사용: {kosdaq_data['error']}")
                        kosdaq_data = data["kosdaq"]
                    

                
                # 실시간 데이터로 구성
                realtime_data = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "kospi": {
                        "price": kospi_data.get("price", data["kospi"]["price"]),
                        "diff": kospi_data.get("change", data["kospi"]["diff"]),
                        "pct": kospi_data.get("change_rate", data["kospi"]["pct"])
                    },
                    "kosdaq": {
                        "price": kosdaq_data.get("price", data["kosdaq"]["price"]),
                        "diff": kosdaq_data.get("change", data["kosdaq"]["diff"]),
                        "pct": kosdaq_data.get("change_rate", data["kosdaq"]["pct"])
                    },
                    "top_sectors": data["top_sectors"],     # 섹터는 별도 API 필요
                    "bottom_sectors": data["bottom_sectors"],
                    "movers": data["movers"]
                }
                
                print("✅ 한국 장중 실시간 데이터 구성 완료")
                print(f"📊 KOSPI: {realtime_data['kospi']['price']} ({realtime_data['kospi']['diff']:+.2f}, {realtime_data['kospi']['pct']:+.2f}%)")
                print(f"📊 KOSDAQ: {realtime_data['kosdaq']['price']} ({realtime_data['kosdaq']['diff']:+.2f}, {realtime_data['kosdaq']['pct']:+.2f}%)")
                
            except Exception as e:
                print(f"⚠️ 한국투자증권 API 연결 실패, 샘플 데이터 사용: {e}")
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
                kospi=self.composer.format_price(realtime_data["kospi"]["price"]),
                kospi_diff=self.composer.format_percentage(realtime_data["kospi"]["diff"], False),
                kospi_pct=self.composer.format_percentage(realtime_data["kospi"]["pct"]),
                kosdaq=self.composer.format_price(realtime_data["kosdaq"]["price"]),
                kosdaq_diff=self.composer.format_percentage(realtime_data["kosdaq"]["diff"], False),
                kosdaq_pct=self.composer.format_percentage(realtime_data["kosdaq"]["pct"]),
                top_sectors=", ".join(realtime_data["top_sectors"]),
                bottom_sectors=", ".join(realtime_data["bottom_sectors"]),
                movers=realtime_data["movers"]
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
            # 데이터 검증
            if not self._validate_kr_close_data(data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 한국 장 마감 데이터 검증 완료")
            print("🔄 한국 장 마감 콘텐츠 합성 중...")
            
            # 섹터 요약 생성
            sectors = data.get("sectors", {})
            sector_line = self.composer.compose_sector_summary(
                sectors.get("top", []),
                sectors.get("bottom", [])
            )
            print(f"🏭 한국 섹터 요약: {sector_line}")
            
            # 특징주 요약 생성
            movers_block = self.composer.compose_movers_summary(data.get("movers", []))
            movers_line_count = len(movers_block.split('\n')) if movers_block else 0
            print(f"🚀 한국 특징주 요약: {movers_line_count}줄")
            
            # 템플릿 렌더링
            from ..rendering.templates import KR_CLOSE
            
            content = KR_CLOSE.format(
                date=data["date"],
                kospi=self.composer.format_price(data["kospi"]["price"]),
                kospi_diff=self.composer.format_percentage(data["kospi"]["diff"], False),
                kospi_pct=self.composer.format_percentage(data["kospi"]["pct"]),
                kosdaq=self.composer.format_price(data["kosdaq"]["price"]),
                kosdaq_diff=self.composer.format_percentage(data["kosdaq"]["diff"], False),
                kosdaq_pct=self.composer.format_percentage(data["kosdaq"]["pct"]),
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
            # 데이터 검증
            if not self._validate_us_preview_data(data):
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 미국 개장 전 데이터 검증 완료")
            print("🔄 미국 개장 전 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import US_PREVIEW
            
            content = US_PREVIEW.format(
                date=data["date"],
                spx_pct=self.composer.format_percentage(data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(data["us_wrap"]["djia_pct"]),
                es=self.composer.format_price(data["futures"]["es"]),
                nq=self.composer.format_price(data["futures"]["nq"]),
                ym=self.composer.format_price(data["futures"]["ym"]),
                wti=self.composer.format_price(data["macro"]["wti"]),
                gold=self.composer.format_price(data["macro"]["gold"]),
                ust10y=self.composer.format_price(data["macro"]["ust10y"]),
                today_events=" / ".join(data["today_events"]),
                focus_sectors="·".join(data["focus_sectors"]),
                risks=", ".join(data["risks"])
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
            # 데이터 검증
            if not self._validate_us_preview_data(data):  # 동일한 데이터 구조 사용
                return {"success": False, "error": "Invalid data"}
            
            print("🔍 미국 장전 데이터 검증 완료")
            print("🔄 미국 장전 콘텐츠 합성 중...")
            
            # 템플릿 렌더링
            from ..rendering.templates import US_PREMKT
            
            content = US_PREMKT.format(
                date=data["date"],
                spx_pct=self.composer.format_percentage(data["us_wrap"]["spx_pct"]),
                ndx_pct=self.composer.format_percentage(data["us_wrap"]["ndx_pct"]),
                djia_pct=self.composer.format_percentage(data["us_wrap"]["djia_pct"]),
                es=self.composer.format_price(data["futures"]["es"]),
                nq=self.composer.format_price(data["futures"]["nq"]),
                ym=self.composer.format_price(data["futures"]["ym"]),
                wti=self.composer.format_price(data["macro"]["wti"]),
                gold=self.composer.format_price(data["macro"]["gold"]),
                ust10y=self.composer.format_price(data["macro"]["ust10y"]),
                today_events=" / ".join(data["today_events"]),
                focus_sectors="·".join(data["focus_sectors"]),
                risks=", ".join(data["risks"])
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
        required_fields = ["date", "kospi", "kosdaq", "top_sectors", "bottom_sectors", "movers"]
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
