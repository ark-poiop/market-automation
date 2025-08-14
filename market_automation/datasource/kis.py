"""
한국투자증권 API 클라이언트
실전투자 API 연동
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from ..config import config

class KISClient:
    def __init__(self):
        self.config = config
        self.app_key = self.config.get_kis_app_key()
        self.app_secret = self.config.get_kis_app_secret()
        self.vts = self.config.get_kis_vts()
        
        # VTS에 따른 도메인 설정
        if self.vts == "REAL":
            self.base_url = "https://openapi.koreainvestment.com:9443"
        else:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        
        # 토큰 관리
        self.access_token = None
        self.token_expires = None
        
        # idxcode.mst 파일에서 지수 코드 매핑 생성
        self.index_code_map = self._load_index_codes()
        
        print(f"🔧 KIS 클라이언트 초기화 완료")
        print(f"🏢 VTS: {self.vts}")
        print(f"🔗 도메인: {self.base_url}")
        print(f"📊 지수 코드 매핑: {len(self.index_code_map)}개 로드됨")
    
    def _load_index_codes(self) -> Dict[str, str]:
        """idxcode.mst 파일을 로드하여 지수 이름 ↔ fid_input_iscd 매핑 생성"""
        index_code_map = {}
        
        try:
            # idxcode.mst 파일 경로 (프로젝트 루트 기준)
            idxcode_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "idxcode.mst")
            
            if os.path.exists(idxcode_path):
                # 다양한 인코딩 시도
                encodings = ['cp949', 'euc-kr', 'utf-8', 'latin-1']
                
                for encoding in encodings:
                    try:
                        with open(idxcode_path, 'r', encoding=encoding) as f:
                            for line in f:
                                line = line.strip()
                                if line and len(line) >= 5:
                                    # 앞 5자리가 지수 코드, 나머지가 지수 이름
                                    code = line[:5].strip()
                                    name = line[5:].strip()
                                    
                                    if code and name and code != "00000":
                                        index_code_map[name] = code
                                        index_code_map[code] = name  # 양방향 매핑
                        
                        print(f"✅ idxcode.mst 파일 로드 성공: {idxcode_path} (인코딩: {encoding})")
                        break
                        
                    except UnicodeDecodeError:
                        continue
                else:
                    print(f"⚠️ 모든 인코딩 시도 실패, 기본 지수 코드 사용")
                    # 기본 지수 코드 설정
                    index_code_map = {
                        "KOSPI": "00001",
                        "00001": "KOSPI",
                        "KOSDAQ": "11001", 
                        "11001": "KOSDAQ"
                    }
            else:
                print(f"⚠️ idxcode.mst 파일을 찾을 수 없음: {idxcode_path}")
                # 기본 지수 코드 설정
                index_code_map = {
                    "KOSPI": "00001",
                    "00001": "KOSPI",
                    "KOSDAQ": "11001", 
                    "11001": "KOSDAQ"
                }
                
        except Exception as e:
            print(f"❌ idxcode.mst 파일 로드 실패: {e}")
            # 기본 지수 코드 설정
            index_code_map = {
                "KOSPI": "00001",
                "00001": "KOSPI",
                "KOSDAQ": "11001",
                "11001": "KOSDAQ"
            }
        
        return index_code_map
    
    def _get_access_token(self) -> str:
        """액세스 토큰 발급 - 개선된 버전"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        try:
            # 토큰 발급 URL
            url = f"{self.base_url}/oauth2/tokenP"
            
            # 요청 헤더
            headers = {
                "Content-Type": "application/json"
            }
            
            # 요청 데이터
            payload = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            print(f"🔄 KIS 토큰 발급 시도 중...")
            print(f"🔗 URL: {url}")
            print(f"🔑 App Key: {self.app_key[:10]}...")
            print(f"🔒 VTS: {self.vts}")
            
            # POST 요청
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"📡 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📋 응답 내용: {result}")
                
                if "access_token" in result:
                    self.access_token = result["access_token"]
                    # 토큰 만료 시간 설정 (23시간 후)
                    self.token_expires = datetime.now() + timedelta(hours=23)
                    print(f"✅ KIS 액세스 토큰 발급 성공: {self.access_token[:20]}...")
                    return self.access_token
                else:
                    print(f"❌ 응답에 access_token이 없음: {result}")
                    return ""
            else:
                print(f"❌ KIS 액세스 토큰 발급 실패: HTTP {response.status_code}")
                print(f"📋 오류 응답: {response.text}")
                return ""
                
        except Exception as e:
            print(f"❌ KIS 액세스 토큰 발급 오류: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _make_authenticated_request(self, method: str, endpoint: str, token: str, **kwargs) -> Dict[str, Any]:
        """Bearer token 기반 인증 요청 - 다른 지수 조회 TR ID 시도"""
        try:
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {token}"
            headers["Content-Type"] = "application/json"
            headers["appkey"] = self.app_key
            headers["appsecret"] = self.app_secret
            
            # VTS에 따른 TR ID 설정 - 다른 지수 조회 TR ID 시도
            if self.vts == "REAL":
                # 실전투자: 다른 지수 조회 TR ID 시도
                headers["tr_id"] = "FHKST01010100"  # 일반적인 지수 조회 TR ID
            else:
                # 모의투자: 다른 지수 조회 TR ID 시도
                headers["tr_id"] = "VTTC2102U"  # 일반적인 지수 조회 TR ID
            
            url = f"{self.base_url}{endpoint}"
            
            print(f"🔄 인증 요청: {method} {url}")
            print(f"🔑 토큰: {token[:20]}...")
            print(f"🏷️ TR ID: {headers['tr_id']}")
            print(f"🏢 VTS: {self.vts}")
            
            response = requests.request(method, url, headers=headers, **kwargs)
            
            print(f"📡 응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"❌ API 요청 실패: HTTP {response.status_code}")
                print(f"📋 오류 응답: {response.text}")
                return {"error": f"HTTP Error: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ 인증 요청 오류: {e}")
            return {"error": str(e)}
    
    def get_kr_market_data(self) -> Dict[str, Any]:
        """한국 시장 데이터 통합 조회 - KOSPI와 KOSDAQ 모두 조회"""
        try:
            # 액세스 토큰 발급
            token = self._get_access_token()
            if not token:
                return {"error": "Failed to get access token"}
            
            print("✅ KIS 액세스 토큰 발급 성공")
            
            # KOSPI 데이터 조회
            kospi_data = self._get_kospi_data(token)
            print(f"📊 KOSPI 데이터: {kospi_data}")
            
            # KOSDAQ 데이터 조회
            kosdaq_data = self._get_kosdaq_data(token)
            print(f"📊 KOSDAQ 데이터: {kosdaq_data}")
            
            return {
                "kospi": kospi_data,
                "kosdaq": kosdaq_data,
                "exchange": None  # 환율은 별도 조회
            }
                
        except Exception as e:
            print(f"❌ 한국 시장 데이터 조회 실패: {e}")
            return {"error": str(e)}
    
    def _get_kospi_data(self, token: str) -> Dict[str, Any]:
        """KOSPI 데이터 조회"""
        try:
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-index-daily-price"
            kospi_code = self.index_code_map.get("KOSPI", "00001")
            
            params = {
                "FID_COND_MRKT_DIV_CODE": "1",
                "FID_INPUT_ISCD": kospi_code,
                "FID_INPUT_DATE": datetime.now().strftime("%Y%m%d"),
                "FID_INPUT_PRICE": "1",
                "FID_VOL_CNT": "1"
            }
            
            print(f"📊 KOSPI 조회 매개변수: {params}")
            
            result = self._make_authenticated_request("GET", endpoint, token, params=params)
            
            if "error" not in result and result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "symbol": "KOSPI",
                    "price": float(output.get("stck_prpr", 0)),
                    "change": float(output.get("prdy_vrss", 0)),
                    "change_rate": float(output.get("prdy_ctrt", 0)),
                    "volume": int(output.get("acml_vol", 0)),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"KOSPI 조회 실패: {result.get('msg1', 'Unknown error')}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _get_kosdaq_data(self, token: str) -> Dict[str, Any]:
        """KOSDAQ 데이터 조회"""
        try:
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-index-daily-price"
            kosdaq_code = self.index_code_map.get("KOSDAQ", "11001")
            
            params = {
                "FID_COND_MRKT_DIV_CODE": "1",
                "FID_INPUT_ISCD": kosdaq_code,
                "FID_INPUT_DATE": datetime.now().strftime("%Y%m%d"),
                "FID_INPUT_PRICE": "1",
                "FID_VOL_CNT": "1"
            }
            
            print(f"📊 KOSDAQ 조회 매개변수: {params}")
            
            result = self._make_authenticated_request("GET", endpoint, token, params=params)
            
            if "error" not in result and result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "symbol": "KOSDAQ",
                    "price": float(output.get("stck_prpr", 0)),
                    "change": float(output.get("prdy_vrss", 0)),
                    "change_rate": float(output.get("prdy_ctrt", 0)),
                    "volume": int(output.get("acml_vol", 0)),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"KOSDAQ 조회 실패: {result.get('msg1', 'Unknown error')}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _get_exchange_with_token(self, token: str) -> Dict[str, Any]:
        """토큰을 사용하여 환율 데이터 조회"""
        try:
            # 환율은 기존 API 엔드포인트 사용 (지수가 아니므로)
            endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
            
            # USD/KRW 환율 조회
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",      # J: 주식
                "FID_COND_SCR_DIV_CODE": "20171",   # 20171: 지수
                "FID_INPUT_ISCD": "USDKRW"          # USDKRW: 달러/원 환율
            }
            
            result = self._make_authenticated_request("GET", endpoint, token, params=params)
            
            if "error" not in result:
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
                return result
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_kr_market_data_alternative(self) -> Dict[str, Any]:
        """한국 시장 데이터 대안 조회 방법 (지수 전용 API)"""
        try:
            token = self._get_access_token()
            if not token:
                return {"error": "Failed to get access token"}
            
            print(f"✅ KIS 액세스 토큰 발급 성공: {token[:20]}...")
            
            # 대안 1: 다른 지수 조회 방법 시도
            kospi_data = self._get_kospi_alternative(token)
            print(f"🔍 KOSPI 대안 데이터: {kospi_data}")
            
            kosdaq_data = self._get_kosdaq_alternative(token)
            print(f"🔍 KOSDAQ 대안 데이터: {kosdaq_data}")
            
            exchange_data = self._get_exchange_alternative(token)
            print(f"🔍 환율 대안 데이터: {exchange_data}")
            
            return {
                "kospi": kospi_data,
                "kosdaq": kosdaq_data,
                "exchange": exchange_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_kospi_alternative(self, token: str) -> Dict[str, Any]:
        """KOSPI 데이터 대안 조회 방법"""
        try:
            # 대안 1: 다른 매개변수 조합 시도
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            # 대안 매개변수 시도
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "KS11"  # KS11: KOSPI 지수 심볼
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
    
    def _get_kosdaq_alternative(self, token: str) -> Dict[str, Any]:
        """KOSDAQ 데이터 대안 조회 방법"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            # 대안 매개변수 시도
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_COND_SCR_DIV_CODE": "20171",
                "FID_INPUT_ISCD": "KQ11"  # KQ11: KOSDAQ 지수 심볼
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
    
    def _get_exchange_alternative(self, token: str) -> Dict[str, Any]:
        """환율 데이터 대안 조회 방법"""
        try:
            url = f"{self.base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "Content-Type": "application/json",
                "authorization": f"Bearer {token}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": "FHKST01010100"
            }
            
            # 대안 매개변수 시도
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
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
