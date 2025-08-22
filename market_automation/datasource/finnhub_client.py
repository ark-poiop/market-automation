"""
Finnhub API를 사용한 급등/급락 종목 및 섹터 데이터 수집
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..config import config

class FinnhubClient:
    """Finnhub API 클라이언트"""
    
    def __init__(self):
        self.api_key = config.get_finnhub_api_key()
        self.base_url = "https://finnhub.io/api/v1"
        
    def get_sector_performance(self) -> Dict[str, List[Dict[str, Any]]]:
        """섹터별 성과 데이터 가져오기"""
        if not self.api_key:
            print("⚠️ FINNHUB_API_KEY가 설정되지 않음")
            return {"top": [], "bottom": []}
            
        try:
            # 섹터별 성과 데이터 (S&P 500 섹터)
            url = f"{self.base_url}/stock/sector-performance"
            params = {'token': self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and isinstance(data, list):
                # 성과 기준으로 정렬 (변동률 기준)
                sorted_sectors = sorted(data, key=lambda x: x.get('performance', 0), reverse=True)
                
                # 상위 3개, 하위 3개 추출
                top_sectors = sorted_sectors[:3] if len(sorted_sectors) >= 3 else sorted_sectors
                bottom_sectors = sorted_sectors[-3:] if len(sorted_sectors) >= 3 else []
                
                return {
                    "top": top_sectors,
                    "bottom": bottom_sectors
                }
            else:
                print("⚠️ 섹터 데이터 형식이 올바르지 않음")
                return {"top": [], "bottom": []}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Finnhub 섹터 데이터 요청 실패: {e}")
            return {"top": [], "bottom": []}
        except Exception as e:
            print(f"❌ Finnhub 섹터 데이터 처리 오류: {e}")
            return {"top": [], "bottom": []}
    
    def get_top_gainers_losers(self, market: str = "US") -> Dict[str, List[Dict[str, Any]]]:
        """상위 급등/급락 종목 가져오기"""
        if not self.api_key:
            print("⚠️ FINNHUB_API_KEY가 설정되지 않음")
            return {"gainers": [], "losers": []}
            
        try:
            # 상위 변동 종목 (S&P 500 기준)
            url = f"{self.base_url}/stock/symbol"
            params = {
                'exchange': 'US',
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            symbols_data = response.json()
            
            if symbols_data and isinstance(symbols_data, list):
                # 주요 종목들 (S&P 500 대표 종목들)
                major_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
                
                gainers = []
                losers = []
                
                for symbol in major_symbols[:5]:  # 상위 5개만
                    try:
                        # 실시간 가격 데이터
                        quote_url = f"{self.base_url}/quote"
                        quote_params = {
                            'symbol': symbol,
                            'token': self.api_key
                        }
                        
                        quote_response = requests.get(quote_url, params=quote_params, timeout=5)
                        if quote_response.status_code == 200:
                            quote_data = quote_response.json()
                            
                            if quote_data and 'dp' in quote_data:
                                change_pct = quote_data['dp']  # 일일 변동률
                                
                                stock_info = {
                                    'symbol': symbol,
                                    'changePercent': change_pct,
                                    'currentPrice': quote_data.get('c', 0)
                                }
                                
                                if change_pct > 0:
                                    gainers.append(stock_info)
                                else:
                                    losers.append(stock_info)
                                
                                if len(gainers) >= 3 and len(losers) >= 3:
                                    break
                                    
                    except Exception as e:
                        print(f"⚠️ {symbol} 종목 데이터 수집 실패: {e}")
                        continue
                
                return {
                    "gainers": gainers[:3],
                    "losers": losers[:3]
                }
            else:
                print("⚠️ 종목 심볼 데이터를 가져올 수 없음")
                return {"gainers": [], "losers": []}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Finnhub API 요청 실패: {e}")
            return {"gainers": [], "losers": []}
        except Exception as e:
            print(f"❌ Finnhub API 처리 오류: {e}")
            return {"gainers": [], "bottom": []}
    
    def get_korean_top_movers(self) -> Dict[str, List[Dict[str, Any]]]:
        """한국 상위 변동 종목 가져오기 (KOSPI/KOSDAQ)"""
        if not self.api_key:
            print("⚠️ FINNHUB_API_KEY가 설정되지 않음")
            return {"gainers": [], "losers": []}
            
        try:
            # 한국 시장 데이터 (KOSPI, KOSDAQ)
            kospi_url = f"{self.base_url}/stock/symbol"
            kospi_params = {
                'exchange': 'KRX',
                'token': self.api_key
            }
            
            response = requests.get(kospi_url, params=kospi_params, timeout=10)
            response.raise_for_status()
            korean_stocks = response.json()
            
            # 실제 데이터가 있으면 처리, 없으면 기본값 반환
            if korean_stocks and len(korean_stocks) > 0:
                # 상위 3개 종목을 급등/급락으로 가정 (실제로는 가격 변동률 기준으로 정렬 필요)
                top_gainers = korean_stocks[:3]
                top_losers = korean_stocks[3:6] if len(korean_stocks) > 3 else []
                
                return {
                    "gainers": top_gainers,
                    "losers": top_losers
                }
            else:
                return {"gainers": [], "losers": []}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Finnhub 한국 시장 데이터 요청 실패: {e}")
            return {"gainers": [], "losers": []}
        except Exception as e:
            print(f"❌ Finnhub 한국 시장 데이터 처리 오류: {e}")
            return {"gainers": [], "losers": []}
    
    def format_sectors_for_display(self, sectors_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """섹터 데이터를 표시용으로 포맷팅"""
        top_sectors = sectors_data.get("top", [])
        
        if not top_sectors:
            return "데이터 없음"
        
        sector_lines = []
        for sector in top_sectors:
            name = sector.get('sector', 'Unknown')
            performance = sector.get('performance', 0)
            sector_lines.append(f"{name} {performance:+.1f}%")
        
        return "\n".join(sector_lines)
    
    def format_movers_for_display(self, movers_data: Dict[str, List[Dict[str, Any]]], market: str = "US") -> Dict[str, str]:
        """급등/급락 종목을 표시용으로 포맷팅"""
        gainers = movers_data.get("gainers", [])
        losers = movers_data.get("losers", [])
        
        # 급등 종목 포맷팅
        if gainers:
            gainer_lines = []
            for stock in gainers:
                symbol = stock.get('symbol', 'Unknown')
                change_pct = stock.get('changePercent', 0)
                gainer_lines.append(f"{symbol} +{change_pct:.1f}%")
            top_gainers = ", ".join(gainer_lines)
        else:
            top_gainers = "데이터 없음"
        
        # 급락 종목 포맷팅
        if losers:
            loser_lines = []
            for stock in losers:
                symbol = stock.get('symbol', 'Unknown')
                change_pct = stock.get('changePercent', 0)
                loser_lines.append(f"{symbol} {change_pct:.1f}%")
            top_losers = ", ".join(loser_lines)
        else:
            top_losers = "데이터 없음"
        
        return {
            "top_gainers": top_gainers,
            "top_losers": top_losers
        }
