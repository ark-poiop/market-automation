"""
Alpaca Markets API 클라이언트
미국 증시 데이터 수집 (주요 지수, 섹터, 특징주)
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..config import config

class AlpacaClient:
    def __init__(self):
        self.config = config
        self.api_key = self.config.get("ALPACA_API_KEY", "")
        self.api_secret = self.config.get("ALPACA_API_SECRET", "")
        self.paper_trading = self.config.get("ALPACA_PAPER", "true").lower() == "true"
        
        # API 엔드포인트 (Paper Trading vs Live Trading)
        if self.paper_trading:
            self.base_url = "https://paper-api.alpaca.markets"
            self.data_url = "https://data.sandbox.alpaca.markets"
        else:
            self.base_url = "https://api.alpaca.markets"
            self.data_url = "https://data.alpaca.markets"
        
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, url: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """API 요청 실행"""
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_account_info(self) -> Dict[str, Any]:
        """계정 정보 조회"""
        url = f"{self.base_url}/v2/account"
        return self._make_request(url)
    
    def get_us_indices(self) -> Dict[str, Any]:
        """미국 주요 지수 데이터 조회"""
        try:
            # Alpaca API에서 사용할 수 있는 실제 지수 심볼들
            # 참고: Alpaca는 일부 지수를 직접 지원하지 않으므로 대체 방법 사용
            indices = {
                "spx": "SPX",   # S&P 500 Index
                "ndx": "NDX",   # Nasdaq 100 Index
                "djia": "DJI",  # Dow Jones Industrial Average
                "rty": "RUT"    # Russell 2000 Index
            }
            
            result = {}
            
            for index_name, symbol in indices.items():
                # 지수 데이터는 다른 엔드포인트를 사용해야 할 수 있음
                # 먼저 일반적인 주식 데이터로 시도
                price_data = self.get_latest_price(symbol)
                if "error" not in price_data:
                    # 전일 종가와 비교하여 변동률 계산
                    prev_close = price_data.get("prev_close", 0)
                    current_price = price_data.get("price", 0)
                    
                    if prev_close > 0:
                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100
                    else:
                        change = 0
                        change_pct = 0
                    
                    # 코멘트 생성
                    comment = self._generate_index_comment(index_name, change_pct)
                    
                    result[index_name] = {
                        "price": current_price,
                        "diff": change,
                        "pct": change_pct,
                        "comment": comment,
                        "volume": price_data.get("volume", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # 지수 데이터 실패 시 ETF 데이터로 대체
                    print(f"⚠️ {symbol} 지수 데이터 실패, ETF로 대체 시도")
                    etf_symbol = self._get_etf_symbol(index_name)
                    if etf_symbol:
                        etf_data = self.get_latest_price(etf_symbol)
                        if "error" not in etf_data:
                            prev_close = etf_data.get("prev_close", 0)
                            current_price = etf_data.get("price", 0)
                            
                            if prev_close > 0:
                                change = current_price - prev_close
                                change_pct = (change / prev_close) * 100
                            else:
                                change = 0
                                change_pct = 0
                            
                            comment = self._generate_index_comment(index_name, change_pct)
                            
                            result[index_name] = {
                                "price": current_price,
                                "diff": change,
                                "pct": change_pct,
                                "comment": comment,
                                "volume": etf_data.get("volume", 0),
                                "timestamp": datetime.now().isoformat()
                            }
                        else:
                            result[index_name] = {"error": f"ETF {etf_symbol} 데이터 실패: {etf_data['error']}"}
                    else:
                        result[index_name] = {"error": f"지수 {symbol} 데이터 실패: {price_data['error']}"}
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """특정 심볼의 최신 가격 데이터 조회"""
        try:
            # 최신 가격 조회
            url = f"{self.data_url}/v2/stocks/{symbol}/trades/latest"
            latest_data = self._make_request(url)
            
            if "error" in latest_data:
                return latest_data
            
            # 전일 종가 조회 - 더 정확한 방법 사용
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            url = f"{self.data_url}/v2/stocks/{symbol}/bars"
            params = {
                "start": yesterday,
                "end": yesterday,
                "timeframe": "1Day",
                "limit": 1
            }
            
            prev_data = self._make_request(url, params=params)
            
            if "error" in prev_data or not prev_data.get("bars"):
                # 전일 데이터가 없으면 오늘 데이터에서 시가를 사용
                print(f"⚠️ {symbol} 전일 데이터 없음, 오늘 시가 사용")
                today = datetime.now().strftime("%Y-%m-%d")
                today_params = {
                    "start": today,
                    "end": today,
                    "timeframe": "1Day",
                    "limit": 1
                }
                today_data = self._make_request(url, params=today_params)
                if "error" not in today_data and today_data.get("bars"):
                    prev_close = today_data["bars"][0]["o"]  # 시가
                else:
                    prev_close = latest_data["trade"]["p"]  # 현재가
            else:
                prev_close = prev_data["bars"][0]["c"]  # 전일 종가
            
            return {
                "price": latest_data["trade"]["p"],  # 현재가
                "prev_close": prev_close,            # 전일 종가 또는 시가
                "volume": latest_data["trade"]["s"], # 거래량
                "timestamp": latest_data["trade"]["t"]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_sector_performance(self) -> Dict[str, List[Dict[str, Any]]]:
        """섹터별 성과 조회 (SPDR ETF 기준)"""
        try:
            # 주요 섹터 ETF 심볼들
            sector_etfs = {
                "Information Technology": "XLK",
                "Financials": "XLF", 
                "Health Care": "XLV",
                "Consumer Discretionary": "XLY",
                "Industrials": "XLI",
                "Energy": "XLE",
                "Materials": "XLB",
                "Real Estate": "XLRE",
                "Utilities": "XLU",
                "Consumer Staples": "XLP",
                "Communication Services": "XLC"
            }
            
            top_sectors = []
            bottom_sectors = []
            
            for sector_name, etf_symbol in sector_etfs.items():
                price_data = self.get_latest_price(etf_symbol)
                if "error" not in price_data:
                    prev_close = price_data.get("prev_close", 0)
                    current_price = price_data.get("price", 0)
                    
                    if prev_close > 0:
                        ret1d = ((current_price - prev_close) / prev_close) * 100
                        
                        sector_data = {
                            "name": sector_name,
                            "ret1d": round(ret1d, 2),
                            "breadth": 0.5  # 기본값, 실제로는 섹터 내 상승/하락 비율 계산 필요
                        }
                        
                        if ret1d > 0:
                            top_sectors.append(sector_data)
                        else:
                            bottom_sectors.append(sector_data)
            
            # 수익률 기준으로 정렬
            top_sectors.sort(key=lambda x: x["ret1d"], reverse=True)
            bottom_sectors.sort(key=lambda x: x["ret1d"])
            
            return {
                "top": top_sectors[:5],      # 상위 5개
                "bottom": bottom_sectors[:5]  # 하위 5개
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_movers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """상위 변동 종목 조회"""
        try:
            # S&P 500 상위 종목들 (실제로는 더 정교한 필터링 필요)
            top_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.A", "UNH", "JNJ"]
            
            movers = []
            
            for symbol in top_symbols[:limit]:
                price_data = self.get_latest_price(symbol)
                if "error" not in price_data:
                    prev_close = price_data.get("prev_close", 0)
                    current_price = price_data.get("price", 0)
                    
                    if prev_close > 0:
                        ret1d = ((current_price - prev_close) / prev_close) * 100
                        
                        # 섹터 정보 (실제로는 별도 API 호출 필요)
                        sector = self._get_stock_sector(symbol)
                        
                        movers.append({
                            "symbol": symbol,
                            "sector": sector,
                            "ret1d": round(ret1d, 2),
                            "mcap": "N/A",  # 시가총액은 별도 API 필요
                            "reason": self._generate_mover_reason(symbol, ret1d)
                        })
            
            # 변동률 기준으로 정렬
            movers.sort(key=lambda x: abs(x["ret1d"]), reverse=True)
            
            return movers[:limit]
            
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_market_status(self) -> Dict[str, Any]:
        """시장 상태 조회 (개장/폐장, 거래 시간 등)"""
        try:
            url = f"{self.base_url}/v2/clock"
            return self._make_request(url)
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_index_comment(self, index_name: str, change_pct: float) -> str:
        """지수별 코멘트 생성"""
        if abs(change_pct) < 0.5:
            return "소폭 변동"
        elif change_pct > 2:
            return "급등"
        elif change_pct > 1:
            return "상승"
        elif change_pct < -2:
            return "급락"
        elif change_pct < -1:
            return "하락"
        else:
            return "안정"
    
    def _generate_mover_reason(self, symbol: str, change_pct: float) -> str:
        """주요 변동 종목 변동 이유 생성"""
        if abs(change_pct) < 2:
            return "일반적 변동"
        elif change_pct > 5:
            return "급등 - 긍정적 뉴스"
        elif change_pct < -5:
            return "급락 - 부정적 뉴스"
        else:
            return "시장 변동"
    
    def _get_stock_sector(self, symbol: str) -> str:
        """주식의 섹터 정보 반환 (실제로는 별도 API 필요)"""
        # 간단한 매핑 (실제로는 더 정확한 데이터 필요)
        sector_map = {
            "AAPL": "Information Technology",
            "MSFT": "Information Technology", 
            "GOOGL": "Communication Services",
            "AMZN": "Consumer Discretionary",
            "NVDA": "Information Technology",
            "META": "Communication Services",
            "TSLA": "Consumer Discretionary"
        }
        return sector_map.get(symbol, "Unknown")

    def _get_etf_symbol(self, index_name: str) -> str:
        """지수명에 해당하는 ETF 심볼 반환"""
        etf_map = {
            "spx": "SPY",   # S&P 500 ETF
            "ndx": "QQQ",   # Nasdaq 100 ETF
            "djia": "DIA",  # Dow Jones ETF
            "rty": "IWM"    # Russell 2000 ETF
        }
        return etf_map.get(index_name, "")
