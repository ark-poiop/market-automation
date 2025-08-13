"""
한국투자증권 API 클라이언트
실전투자 API 연동
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..config import config

class KISClient:
    def __init__(self):
        self.config = config
        self.app_key = self.config.get_kis_app_key()
        self.app_secret = self.config.get_kis_app_secret()
        self.vts = self.config.get_kis_vts()
        
        # API 엔드포인트
        if self.vts == "REAL":
            self.base_url = "https://openapi.koreainvestment.com:9443"
        else:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        
        self.access_token = None
        self.token_expires = None
    
    def _get_access_token(self) -> str:
        """액세스 토큰 발급"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            headers = {
                "content-type": "application/json"
            }
            data = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                # 토큰 만료 시간 설정 (23시간 후)
                self.token_expires = datetime.now() + timedelta(hours=23)
                print("✅ KIS 액세스 토큰 발급 성공")
                return self.access_token
            else:
                print(f"❌ KIS 액세스 토큰 발급 실패: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"❌ KIS 액세스 토큰 발급 오류: {e}")
            return ""
    
    def get_kospi_data(self) -> Dict[str, Any]:
        """KOSPI 지수 데이터 조회"""
        try:
            token = self._get_access_token()
            if not token:
                return {"error": "Failed to get access token"}
            
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "000001"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                if result["rt_cd"] == "0":
                    data = result["output"]
                    return {
                        "symbol": "KOSPI",
                        "price": float(data["stck_prpr"]),
                        "change": float(data["prdy_vrss"]),
                        "change_rate": float(data["prdy_ctrt"]),
                        "volume": int(data["acml_vol"]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"API Error: {result['msg1']}"}
            else:
                return {"error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_kosdaq_data(self) -> Dict[str, Any]:
        """KOSDAQ 지수 데이터 조회"""
        try:
            token = self._get_access_token()
            if not token:
                return {"error": "Failed to get access token"}
            
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            params = {
                "FID_COND_MRKT_DIV_CODE": "K",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "100001"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                if result["rt_cd"] == "0":
                    data = result["output"]
                    return {
                        "symbol": "KOSDAQ",
                        "price": float(data["stck_prpr"]),
                        "change": float(data["prdy_vrss"]),
                        "change_rate": float(data["prdy_ctrt"]),
                        "volume": int(data["acml_vol"]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"API Error: {result['msg1']}"}
            else:
                return {"error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_exchange_rate(self) -> Dict[str, Any]:
        """환율 정보 조회 (USD/KRW)"""
        try:
            token = self._get_access_token()
            if not token:
                return {"error": "Failed to get access token"}
            
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            params = {
                "FID_COND_MRKT_DIV_CODE": "F",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "USDKRW"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                if result["rt_cd"] == "0":
                    data = result["output"]
                    return {
                        "symbol": "USDKRW",
                        "price": float(data["stck_prpr"]),
                        "change": float(data["prdy_vrss"]),
                        "change_rate": float(data["prdy_ctrt"]),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"API Error: {result['msg1']}"}
            else:
                return {"error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_sector_performance(self) -> List[Dict[str, Any]]:
        """섹터별 성과 조회"""
        # TODO: 실제 섹터 성과 API 구현
        # 현재는 샘플 데이터 반환
        return [
            {"name": "Information Technology", "ret1d": 1.6, "breadth": 0.74},
            {"name": "Financials", "ret1d": 1.2, "breadth": 0.68},
            {"name": "Industrials", "ret1d": 1.1, "breadth": 0.66},
            {"name": "Utilities", "ret1d": -0.2, "breadth": 0.42},
            {"name": "Real Estate", "ret1d": 0.1, "breadth": 0.48}
        ]
