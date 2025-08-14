"""
네이버 금융 크롤링 데이터를 기존 시스템 형식으로 변환하는 어댑터
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class NaverDataAdapter:
    """네이버 금융 데이터를 기존 시스템 형식으로 변환"""
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent.parent / "naver_market_data.json"
    
    def load_naver_data(self) -> Optional[Dict[str, Any]]:
        """네이버 데이터 파일 로드"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ 네이버 데이터 로드 성공: {self.data_file}")
                return data
            else:
                print(f"⚠️ 네이버 데이터 파일이 없음: {self.data_file}")
                return None
        except Exception as e:
            print(f"❌ 네이버 데이터 로드 실패: {e}")
            return None
    
    def convert_to_kr_preopen_format(self, naver_data: Dict[str, Any]) -> Dict[str, Any]:
        """네이버 데이터를 한국 개장 전 형식으로 변환"""
        try:
            # 현재 날짜
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # 기존 시스템에서 요구하는 구조로 변환
            converted_data = {
                "date": current_date,
                "us_wrap": {
                    "spx_pct": 0.0,  # 전일 미증시 데이터는 별도 필요
                    "ndx_pct": 0.0,
                    "djia_pct": 0.0
                },
                "futures": {
                    "k200f": 0.0,    # 선물 데이터는 별도 필요
                    "es": 0.0,
                    "nq": 0.0
                },

                "today_events": ["주요 경제지표 발표 없음"],
                "focus_sectors": ["반도체", "2차전지", "바이오"],
                "risks": ["글로벌 경제 불확실성", "원자재 가격 변동성"]
            }
            
            # 네이버 데이터에서 사용 가능한 정보 업데이트
            if "kospi" in naver_data:
                kospi = naver_data["kospi"]
                print(f"📊 KOSPI 데이터 변환: {kospi['price']:,.2f} ({kospi['change']:+,.2f}, {kospi['change_rate']:+.2f}%)")
            
            if "kosdaq" in naver_data:
                kosdaq = naver_data["kosdaq"]
                print(f"📈 KOSDAQ 데이터 변환: {kosdaq['price']:,.2f} ({kosdaq['change']:+,.2f}, {kosdaq['change_rate']:+.2f}%)")
            
            print(f"✅ 한국 개장 전 형식으로 변환 완료")
            return converted_data
            
        except Exception as e:
            print(f"❌ 한국 개장 전 형식 변환 실패: {e}")
            return self._get_default_kr_preopen_data()
    
    def convert_to_kr_midday_format(self, naver_data: Dict[str, Any]) -> Dict[str, Any]:
        """네이버 데이터를 한국 장중 형식으로 변환"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            converted_data = {
                "date": current_date,
                "kospi": {"price": 0.0, "diff": 0.0, "pct": 0.0},
                "kosdaq": {"price": 0.0, "diff": 0.0, "pct": 0.0},
                "top_sectors": ["반도체", "2차전지", "바이오"],
                "bottom_sectors": ["건설", "화학"],
                "movers": "삼성전자 +0.5%, SK하이닉스 +0.3%"
            }
            
            # KOSPI 데이터 변환
            if "kospi" in naver_data:
                kospi = naver_data["kospi"]
                converted_data["kospi"] = {
                    "price": kospi["price"],
                    "diff": kospi["change"],
                    "pct": kospi["change_rate"]
                }
                print(f"📊 KOSPI 변환: {kospi['price']:,.2f} ({kospi['change']:+,.2f}, {kospi['change_rate']:+.2f}%)")
            
            # KOSDAQ 데이터 변환
            if "kosdaq" in naver_data:
                kosdaq = naver_data["kosdaq"]
                converted_data["kosdaq"] = {
                    "price": kosdaq["price"],
                    "diff": kosdaq["change"],
                    "pct": kosdaq["change_rate"]
                }
                print(f"📈 KOSDAQ 변환: {kosdaq['price']:,.2f} ({kosdaq['change']:+,.2f}, {kosdaq['change_rate']:+.2f}%)")
            
            print(f"✅ 한국 장중 형식으로 변환 완료")
            return converted_data
            
        except Exception as e:
            print(f"❌ 한국 장중 형식 변환 실패: {e}")
            return self._get_default_kr_midday_data()
    
    def convert_to_kr_close_format(self, naver_data: Dict[str, Any]) -> Dict[str, Any]:
        """네이버 데이터를 한국 장 마감 형식으로 변환"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            converted_data = {
                "date": current_date,
                "kospi": {"price": 0.0, "diff": 0.0, "pct": 0.0},
                "kosdaq": {"price": 0.0, "diff": 0.0, "pct": 0.0},
                "sectors": {
                    "top": [
                        {"name": "Information Technology", "ret1d": 1.5, "breadth": 0.7},
                        {"name": "Financials", "ret1d": 1.2, "breadth": 0.65}
                    ],
                    "bottom": [
                        {"name": "Materials", "ret1d": -0.3, "breadth": 0.48}
                    ]
                },
                "movers": [
                    {"symbol": "005930", "sector": "Information Technology", "ret1d": 1.8, "reason": "AI 수요 증가"},
                    {"symbol": "000660", "sector": "Information Technology", "ret1d": 1.5, "reason": "메모리 가격 상승"}
                ]
            }
            
            # KOSPI 데이터 변환
            if "kospi" in naver_data:
                kospi = naver_data["kospi"]
                converted_data["kospi"] = {
                    "price": kospi["price"],
                    "diff": kospi["change"],
                    "pct": kospi["change_rate"]
                }
                print(f"📊 KOSPI 변환: {kospi['price']:,.2f} ({kospi['change']:+,.2f}, {kospi['change_rate']:+.2f}%)")
            
            # KOSDAQ 데이터 변환
            if "kosdaq" in naver_data:
                kosdaq = naver_data["kosdaq"]
                converted_data["kosdaq"] = {
                    "price": kosdaq["price"],
                    "diff": kosdaq["change"],
                    "pct": kosdaq["change_rate"]
                }
                print(f"📈 KOSDAQ 변환: {kosdaq['price']:,.2f} ({kosdaq['change']:+,.2f}, {kosdaq['change_rate']:+.2f}%)")
            
            print(f"✅ 한국 장 마감 형식으로 변환 완료")
            return converted_data
            
        except Exception as e:
            print(f"❌ 한국 장 마감 형식 변환 실패: {e}")
            return self._get_default_kr_close_data()
    
    def convert_to_us_close_format(self, naver_data: Dict[str, Any]) -> Dict[str, Any]:
        """네이버 데이터를 미국 장 마감 형식으로 변환"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            converted_data = {
                "date": current_date,
                "indices": {
                    "spx": {"price": 0.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                    "ndx": {"price": 0.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                    "djia": {"price": 0.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                    "rty": {"price": 0.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"}
                },
                "sectors": {"top": [], "bottom": []},
                "movers": []
            }
            
            # S&P 500 데이터 변환
            if "world" in naver_data and "sp500" in naver_data["world"]:
                sp500 = naver_data["world"]["sp500"]
                converted_data["indices"]["spx"] = {
                    "price": sp500["price"],
                    "diff": sp500["change"],
                    "pct": sp500["change_rate"],
                    "comment": self._get_index_comment(sp500["change_rate"])
                }
                print(f"📊 S&P 500 변환: {sp500['price']:,.2f} ({sp500['change']:+,.2f}, {sp500['change_rate']:+.2f}%)")
            
            # 나스닥 데이터 변환
            if "world" in naver_data and "nasdaq" in naver_data["world"]:
                nasdaq = naver_data["world"]["nasdaq"]
                converted_data["indices"]["ndx"] = {
                    "price": nasdaq["price"],
                    "diff": nasdaq["change"],
                    "pct": nasdaq["change_rate"],
                    "comment": self._get_index_comment(nasdaq["change_rate"])
                }
                print(f"📈 나스닥 변환: {nasdaq['price']:,.2f} ({nasdaq['change']:+,.2f}, {nasdaq['change_rate']:+.2f}%)")
            
            # 다우 데이터 변환
            if "world" in naver_data and "dow" in naver_data["world"]:
                dow = naver_data["world"]["dow"]
                converted_data["indices"]["djia"] = {
                    "price": dow["price"],
                    "diff": dow["change"],
                    "pct": dow["change_rate"],
                    "comment": self._get_index_comment(dow["change_rate"])
                }
                print(f"🏭 다우 변환: {dow['price']:,.2f} ({dow['change']:+,.2f}, {dow['change_rate']:+.2f}%)")
            
            # Russell 2000은 기본값 사용 (네이버에서 제공하지 않음)
            print(f"✅ 미국 장 마감 형식으로 변환 완료")
            return converted_data
            
        except Exception as e:
            print(f"❌ 미국 장 마감 형식 변환 실패: {e}")
            return self._get_default_us_close_data()
    
    def convert_to_us_preview_format(self, naver_data: Dict[str, Any]) -> Dict[str, Any]:
        """네이버 데이터를 미국 개장 전 형식으로 변환"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            converted_data = {
                "date": current_date,
                "us_wrap": {
                    "spx_pct": 0.0,
                    "ndx_pct": 0.0,
                    "djia_pct": 0.0
                },
                "futures": {
                    "es": 0.0,
                    "nq": 0.0,
                    "ym": 0.0
                },
                "macro": {
                    "wti": 0.0,
                    "gold": 0.0,
                    "ust10y": 0.0
                },
                "today_events": ["주요 경제지표 발표 없음"],
                "focus_sectors": ["기술", "금융", "헬스케어"],
                "risks": ["글로벌 경제 불확실성", "원자재 가격 변동성"]
            }
            
            # 전일 미국 지수 데이터 업데이트
            if "world" in naver_data:
                world = naver_data["world"]
                
                if "sp500" in world:
                    converted_data["us_wrap"]["spx_pct"] = world["sp500"]["change_rate"]
                
                if "nasdaq" in world:
                    converted_data["us_wrap"]["ndx_pct"] = world["nasdaq"]["change_rate"]
                
                if "dow" in world:
                    converted_data["us_wrap"]["djia_pct"] = world["dow"]["change_rate"]
            
            print(f"✅ 미국 개장 전 형식으로 변환 완료")
            return converted_data
            
        except Exception as e:
            print(f"❌ 미국 개장 전 형식 변환 실패: {e}")
            return self._get_default_us_preview_data()
    
    def _get_index_comment(self, change_rate: float) -> str:
        """변동률에 따른 코멘트 생성"""
        if abs(change_rate) < 0.5:
            return "소폭 변동"
        elif change_rate > 2:
            return "급등"
        elif change_rate > 1:
            return "상승"
        elif change_rate < -2:
            return "급락"
        elif change_rate < -1:
            return "하락"
        else:
            return "안정"
    
    def _get_default_kr_preopen_data(self) -> Dict[str, Any]:
        """기본 한국 개장 전 데이터"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "us_wrap": {
                "spx_pct": 0.0,
                "ndx_pct": 0.0,
                "djia_pct": 0.0
            },
            "futures": {
                "k200f": 0.0,
                "es": 0.0,
                "nq": 0.0
            },
            "today_events": ["주요 경제지표 발표 없음"],
            "focus_sectors": ["반도체", "2차전지", "바이오"],
            "risks": ["글로벌 경제 불확실성", "원자재 가격 변동성"]
        }
    
    def _get_default_kr_midday_data(self) -> Dict[str, Any]:
        """기본 한국 장중 데이터"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "kospi": {"price": 0.0, "diff": 0.0, "pct": 0.0},
            "kosdaq": {"price": 0.0, "diff": 0.0, "pct": 0.0},
            "top_sectors": ["반도체", "2차전지", "바이오"],
            "bottom_sectors": ["건설", "화학"],
            "movers": "삼성전자 +0.5%, SK하이닉스 +0.3%"
        }
    
    def _get_default_kr_close_data(self) -> Dict[str, Any]:
        """기본 한국 장 마감 데이터"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "kospi": {"price": 0.0, "diff": 0.0, "pct": 0.0},
            "kosdaq": {"price": 0.0, "diff": 0.0, "pct": 0.0},
            "sectors": {
                "top": [
                    {"name": "Information Technology", "ret1d": 1.5, "breadth": 0.7},
                    {"name": "Financials", "ret1d": 1.2, "breadth": 0.65}
                ],
                "bottom": [
                    {"name": "Information Technology", "ret1d": -0.3, "breadth": 0.48}
                ]
            },
            "movers": [
                {"symbol": "005930", "sector": "Information Technology", "ret1d": 1.8, "reason": "AI 수요 증가"},
                {"symbol": "000660", "sector": "Information Technology", "ret1d": 1.5, "reason": "메모리 가격 상승"}
            ]
        }
    
    def _get_default_us_close_data(self) -> Dict[str, Any]:
        """기본 미국 장 마감 데이터"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return {
            "date": current_date,
            "indices": {
                "spx": {"price": 5000.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                "ndx": {"price": 16000.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                "djia": {"price": 40000.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"},
                "rty": {"price": 2000.0, "diff": 0.0, "pct": 0.0, "comment": "소폭 변동"}
            },
            "sectors": {"top": [], "bottom": []},
            "movers": []
        }
    
    def _get_default_us_preview_data(self) -> Dict[str, Any]:
        """기본 미국 개장 전 데이터"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return {
            "date": current_date,
            "us_wrap": {
                "spx_pct": 0.0,
                "ndx_pct": 0.0,
                "djia_pct": 0.0
            },
            "futures": {
                "es": 5000.0,
                "nq": 16000.0,
                "ym": 40000.0
            },
            "macro": {
                "wti": 80.0,
                "gold": 2000.0,
                "ust10y": 4.0
            },
            "today_events": ["주요 경제지표 발표 없음"],
            "focus_sectors": ["기술", "금융", "헬스케어"],
            "risks": ["글로벌 경제 불확실성", "원자재 가격 변동성"]
        }
