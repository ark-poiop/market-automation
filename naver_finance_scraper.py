#!/usr/bin/env python3
"""
네이버 금융 지수 데이터 수집기
KOSPI, KOSDAQ, 미국 주요 지수 실시간 정보를 웹 스크래핑으로 수집
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import json

class NaverFinanceScraper:
    def __init__(self):
        self.base_url = "https://finance.naver.com/sise/"
        self.world_url = "https://finance.naver.com/world/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_market_data(self):
        """네이버 금융에서 시장 데이터 수집"""
        try:
            print("🔍 네이버 금융에서 시장 데이터 수집 중...")
            print("=" * 60)
            
            # 메인 페이지 요청
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            # 한글 인코딩 처리
            response.encoding = 'euc-kr'
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 지수 정보 추출
            market_data = self._extract_market_data(soup)
            
            # 세계지수 데이터 수집
            print("\n🌍 세계지수 데이터 수집 중...")
            world_data = self.get_world_market_data()
            if world_data and 'error' not in world_data:
                market_data['world'] = world_data
                print("✅ 세계지수 데이터 수집 완료")
            else:
                print("⚠️ 세계지수 데이터 수집 실패")
            
            # 섹터 데이터 수집
            print("\n🏭 섹터 데이터 수집 중...")
            sector_data = self.get_sector_data()
            if sector_data:
                market_data['sectors'] = sector_data
                print("✅ 섹터 데이터 수집 완료")
            else:
                print("⚠️ 섹터 데이터 수집 실패")
            
            # 특징주 데이터 수집
            print("\n🚀 특징주 데이터 수집 중...")
            movers_data = self.get_movers_data()
            if movers_data:
                market_data['movers'] = movers_data
                print("✅ 특징주 데이터 수집 완료")
            else:
                print("⚠️ 특징주 데이터 수집 실패")
            
            return market_data
            
        except Exception as e:
            print(f"❌ 데이터 수집 실패: {e}")
            return {"error": str(e)}
    
    def get_sector_data(self):
        """업종별 시세 데이터 수집"""
        try:
            print("🏭 업종별 시세 데이터 수집 중...")
            
            # 업종별 시세 페이지
            sector_url = "https://finance.naver.com/sise/sise_group.naver"
            response = requests.get(sector_url, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            sector_data = self._extract_sector_data(soup)
            
            if sector_data:
                print("✅ 업종별 시세 데이터 수집 완료")
                return sector_data
            else:
                print("⚠️ 업종별 시세 데이터 수집 실패")
                return None
                
        except Exception as e:
            print(f"❌ 업종별 시세 데이터 수집 실패: {e}")
            return None
    
    def get_movers_data(self):
        """특징주 데이터 수집"""
        try:
            print("🚀 특징주 데이터 수집 중...")
            
            # 여러 특징주 페이지에서 시도
            movers_data = None
            
            # 1. 거래량 급증 페이지 시도
            volume_url = "https://finance.naver.com/sise/sise_quant.naver"
            movers_data = self._try_get_movers_from_url(volume_url, "거래량 급증")
            
            # 2. 급등주 페이지 시도
            if not movers_data:
                rise_url = "https://finance.naver.com/sise/sise_rise.naver"
                movers_data = self._try_get_movers_from_url(rise_url, "급등주")
            
            # 3. 시가총액 상위 페이지 시도
            if not movers_data:
                market_url = "https://finance.naver.com/sise/sise_market_sum.naver"
                movers_data = self._try_get_movers_from_url(market_url, "시가총액 상위")
            
            if movers_data:
                print("✅ 특징주 데이터 수집 완료")
                return movers_data
            else:
                print("⚠️ 모든 특징주 페이지에서 데이터 수집 실패")
                return None
                
        except Exception as e:
            print(f"❌ 특징주 데이터 수집 실패: {e}")
            return None
    
    def _try_get_movers_from_url(self, url, page_name):
        """특정 URL에서 특징주 데이터 수집 시도"""
        try:
            print(f"   🔍 {page_name} 페이지 시도 중...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = 'euc-kr'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            movers_data = self._extract_movers_data(soup)
            
            if movers_data:
                print(f"   ✅ {page_name} 페이지에서 데이터 수집 성공")
                return movers_data
            else:
                print(f"   ⚠️ {page_name} 페이지에서 데이터 수집 실패")
                return None
                
        except Exception as e:
            print(f"   ❌ {page_name} 페이지 접근 실패: {e}")
            return None
    
    def _extract_market_data(self, soup):
        """HTML에서 시장 데이터 추출"""
        try:
            market_data = {}
            
            # KOSPI 정보 추출
            kospi_data = self._extract_kospi_data(soup)
            if kospi_data:
                market_data['kospi'] = kospi_data
                print(f"📊 KOSPI: {kospi_data['price']:,.2f} ({kospi_data['change']:+,.2f}, {kospi_data['change_rate']:+.2f}%)")
            
            # KOSDAQ 정보 추출
            kosdaq_data = self._extract_kosdaq_data(soup)
            if kosdaq_data:
                market_data['kosdaq'] = kosdaq_data
                print(f"📈 KOSDAQ: {kosdaq_data['price']:,.2f} ({kosdaq_data['change']:+,.2f}, {kosdaq_data['change_rate']:+.2f}%)")
            

            
            # 수집 시간 추가
            market_data['timestamp'] = datetime.now().isoformat()
            market_data['source'] = 'naver_finance'
            
            return market_data
            
        except Exception as e:
            print(f"❌ 데이터 추출 실패: {e}")
            return {"error": str(e)}
    
    def get_world_market_data(self):
        """네이버 금융 세계지수 페이지에서 미국 주요 지수 데이터 수집"""
        try:
            # 세계지수 페이지 요청
            response = requests.get(self.world_url, headers=self.headers)
            response.raise_for_status()
            
            # 한글 인코딩 처리
            response.encoding = 'euc-kr'
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 미국 주요 지수 데이터 추출
            world_data = self._extract_world_market_data(soup)
            
            return world_data
            
        except Exception as e:
            print(f"❌ 세계지수 데이터 수집 실패: {e}")
            return {"error": str(e)}
    
    def _extract_world_market_data(self, soup):
        """HTML에서 세계지수 데이터 추출"""
        try:
            world_data = {}
            
            # JavaScript 변수에서 데이터 파싱
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                script_text = script.get_text()
                
                # americaData 변수 찾기
                if 'americaData' in script_text:
                    print("🔍 americaData 변수 발견, 데이터 파싱 중...")
                    
                    # S&P 500 데이터 파싱
                    sp500_match = re.search(r'"SPI@SPX":\{"diff":([+-]?[\d.]+)[^}]*"last":([\d.]+)[^}]*"rate":([+-]?[\d.]+)', script_text)
                    if sp500_match:
                        change = float(sp500_match.group(1))
                        price = float(sp500_match.group(2))
                        change_rate = float(sp500_match.group(3))
                        
                        world_data['sp500'] = {
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"📊 S&P 500: {price:,.2f} ({change:+,.2f}, {change_rate:+.2f}%)")
                    else:
                        print("⚠️ S&P 500 데이터 파싱 실패")
                    
                    # 나스닥 종합 데이터 파싱
                    nasdaq_match = re.search(r'"NAS@IXIC":\{"diff":([+-]?[\d.]+)[^}]*"last":([\d.]+)[^}]*"rate":([+-]?[\d.]+)', script_text)
                    if nasdaq_match:
                        change = float(nasdaq_match.group(1))
                        price = float(nasdaq_match.group(2))
                        change_rate = float(nasdaq_match.group(3))
                        
                        world_data['nasdaq'] = {
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"📈 나스닥: {price:,.2f} ({change:+,.2f}, {change_rate:+.2f}%)")
                    else:
                        print("⚠️ 나스닥 데이터 파싱 실패")
                    
                    # 다우 산업 데이터 파싱
                    dow_match = re.search(r'"DJI@DJI":\{"diff":([+-]?[\d.]+)[^}]*"last":([\d.]+)[^}]*"rate":([+-]?[\d.]+)', script_text)
                    if dow_match:
                        change = float(dow_match.group(1))
                        price = float(dow_match.group(2))
                        change_rate = float(dow_match.group(3))
                        
                        world_data['dow'] = {
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"🏭 다우: {price:,.2f} ({change:+,.2f}, {change_rate:+.2f}%)")
                    else:
                        print("⚠️ 다우 데이터 파싱 실패")
                    
                    break  # americaData를 찾았으면 중단
            
            return world_data
            
        except Exception as e:
            print(f"❌ 세계지수 데이터 추출 실패: {e}")
            return {"error": str(e)}
    
    def _extract_kospi_data(self, soup):
        """KOSPI 데이터 추출 - HTML 요소 ID/클래스 기반"""
        try:
            # KOSPI 가격을 ID로 직접 찾기
            kospi_price_elem = soup.find('span', id='KOSPI_now')
            
            if kospi_price_elem:
                price_str = kospi_price_elem.get_text().replace(',', '')
                price = float(price_str)
                print(f"🔍 KOSPI 가격 발견 (ID): {price:,.2f}")
                
                # 등락 정보를 더 정확하게 찾기
                # 방법 1: KOSPI 관련 테이블이나 섹션에서 찾기
                kospi_section = soup.find('div', class_='type_1')
                if kospi_section:
                    # 등락 정보가 있는 텍스트 찾기
                    section_text = kospi_section.get_text()
                    print(f"🔍 KOSPI 섹션 텍스트: {section_text[:200]}...")
                    
                    # 등락 정보 패턴: 숫자.숫자 +숫자.숫자% 또는 -숫자.숫자 -숫자.숫자%
                    change_pattern = r'([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                    change_match = re.search(change_pattern, section_text)
                    
                    if change_match:
                        change = float(change_match.group(1))
                        change_rate = float(change_match.group(2))
                        print(f"🎯 KOSPI 등락 정보 발견 (섹션): {change:+,.2f}, {change_rate:+.2f}%")
                        
                        return {
                            'symbol': 'KOSPI',
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                
                # 방법 2: 전체 HTML에서 KOSPI 가격 근처의 등락 정보 찾기
                html_text = soup.get_text()
                
                # KOSPI 가격 다음에 오는 등락 정보를 더 유연하게 찾기
                # 패턴: 가격 + 공백 + 등락 + 공백 + 등락률%
                flexible_pattern = r'3,2\d{2}\.\d+\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                change_match = re.search(flexible_pattern, html_text)
                
                if change_match:
                    change = float(change_match.group(1))
                    change_rate = float(change_match.group(2))
                    print(f"🎯 KOSPI 등락 정보 발견 (유연한 패턴): {change:+,.2f}, {change_rate:+.2f}%")
                    
                    return {
                        'symbol': 'KOSPI',
                        'price': price,
                        'change': change,
                        'change_rate': change_rate,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # 방법 3: KOSPI 전용 등락 정보 찾기 (KOSPI 200과 구분)
                # KOSPI 가격 근처에서 정확한 등락 정보 찾기
                print("🔍 KOSPI 전용 등락 정보 찾기 시작...")
                
                # 방법 3-1: KOSPI 전용 컨테이너 찾기
                kospi_container = soup.find('div', {'id': 'KOSPI'}) or soup.find('div', {'class': 'KOSPI'})
                if kospi_container:
                    kospi_text = kospi_container.get_text()
                    print(f"🔍 KOSPI 컨테이너 발견: {kospi_text[:200]}...")
                    
                    # KOSPI 가격과 등락 정보를 함께 찾기
                    kospi_pattern = r'3,2\d{2}\.\d+\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                    kospi_match = re.search(kospi_pattern, kospi_text)
                    
                    if kospi_match:
                        change = float(kospi_match.group(1))
                        change_rate = float(kospi_match.group(2))
                        print(f"🎯 KOSPI 등락 정보 발견 (컨테이너): {change:+,.2f}, {change_rate:+.2f}%")
                        
                        return {
                            'symbol': 'KOSPI',
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                
                # 방법 3-2: KOSPI 가격 요소의 부모에서 등락 정보 찾기
                kospi_price_parent = kospi_price_elem.parent
                if kospi_price_parent:
                    parent_text = kospi_price_parent.get_text()
                    print(f"🔍 KOSPI 가격 부모 텍스트: {parent_text[:200]}...")
                    
                    # KOSPI 가격 근처의 등락 정보 패턴 (더 유연하게)
                    # 패턴 1: 가격 + 공백 + 등락 + 공백 + 등락률%
                    nearby_pattern1 = r'3,2\d{2}\.\d+\s+([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%'
                    nearby_match1 = re.search(nearby_pattern1, parent_text)
                    
                    if nearby_match1:
                        change = float(nearby_match1.group(1))
                        change_rate = float(nearby_match1.group(2))
                        print(f"🎯 KOSPI 등락 정보 발견 (패턴1): {change:+,.2f}, {change_rate:+.2f}%")
                        
                        return {
                            'symbol': 'KOSPI',
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    # 패턴 2: 등락 + 공백 + 등락률% (부호가 없는 경우)
                    nearby_pattern2 = r'(\d+\.\d+)\s+([+-]\d+\.\d+)%'
                    nearby_match2 = re.search(nearby_pattern2, parent_text)
                    
                    if nearby_match2:
                        change_str = nearby_match2.group(1)
                        change_rate = float(nearby_match2.group(2))
                        
                        # 등락 값의 부호를 등락률과 일치시키기
                        if change_rate > 0:
                            change = float(change_str)  # 양수
                        else:
                            change = -float(change_str)  # 음수
                        
                        print(f"🎯 KOSPI 등락 정보 발견 (패턴2): {change:+,.2f}, {change_rate:+.2f}%")
                        
                        return {
                            'symbol': 'KOSPI',
                            'price': price,
                            'change': change,
                            'change_rate': change_rate,
                            'timestamp': datetime.now().isoformat()
                        }
                
                # 방법 3-3: KOSPI 관련 모든 요소에서 정확한 데이터 찾기
                print("🔍 KOSPI 관련 요소에서 정확한 데이터 찾기...")
                kospi_elements = soup.find_all(text=re.compile(r'코스피'))
                
                for element in kospi_elements:
                    parent = element.parent
                    if parent:
                        parent_text = parent.get_text()
                        
                        # KOSPI 200이 아닌 KOSPI만 찾기
                        if '코스피' in parent_text and '코스피200' not in parent_text and any(char.isdigit() for char in parent_text):
                            print(f"🔍 KOSPI 관련 텍스트 (코스피200 제외): {parent_text[:100]}...")
                            
                            # KOSPI 가격과 등락 정보 패턴 찾기
                            kospi_exact_pattern = r'3,2\d{2}\.\d+\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                            kospi_exact_match = re.search(kospi_exact_pattern, parent_text)
                            
                            if kospi_exact_match:
                                change = float(kospi_exact_match.group(1))
                                change_rate = float(kospi_exact_match.group(2))
                                print(f"🎯 KOSPI 정확한 등락 정보 발견: {change:+,.2f}, {change_rate:+.2f}%")
                                
                                return {
                                    'symbol': 'KOSPI',
                                    'price': price,
                                    'change': change,
                                    'change_rate': change_rate,
                                    'timestamp': datetime.now().isoformat()
                                }
                
                # 방법 3-4: 전체 HTML에서 KOSPI 가격 근처의 등락 정보 찾기
                print("🔍 전체 HTML에서 KOSPI 가격 근처 등락 정보 찾기...")
                html_text = soup.get_text()
                
                # KOSPI 가격 다음에 오는 등락 정보를 더 유연하게 찾기
                # 패턴: 가격 + 공백 + 등락 + 공백 + 등락률%
                flexible_pattern = r'3,2\d{2}\.\d+\s+([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                flexible_match = re.search(flexible_pattern, html_text)
                
                if flexible_match:
                    change = float(flexible_match.group(1))
                    change_rate = float(flexible_match.group(2))
                    print(f"🎯 KOSPI 등락 정보 발견 (유연한 패턴): {change:+,.2f}, {change_rate:+.2f}%")
                    
                    return {
                        'symbol': 'KOSPI',
                        'price': price,
                        'change': change,
                        'change_rate': change_rate,
                        'timestamp': datetime.now().isoformat()
                    }
                
                print("⚠️ KOSPI 등락 정보를 찾을 수 없음")
                return {
                    'symbol': 'KOSPI',
                    'price': price,
                    'change': 0.0,
                    'change_rate': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            
            # ID로 찾지 못한 경우 기존 방식 시도
            return self._extract_kospi_data_fallback(soup)
            
        except Exception as e:
            print(f"❌ KOSPI 데이터 추출 실패: {e}")
            return None
    
    def _extract_kospi_data_fallback(self, soup):
        """KOSPI 데이터 추출 - 폴백 방식"""
        try:
            html_text = soup.get_text()
            
            # KOSPI 가격 추출
            price_pattern = r'코스피\s+(\d{1,3}(?:,\d{3})*\.\d{2})'
            price_match = re.search(price_pattern, html_text)
            
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                price = float(price_str)
                print(f"🔍 KOSPI 가격 발견 (폴백): {price:,.2f}")
                
                return {
                    'symbol': 'KOSPI',
                    'price': price,
                    'change': 0.0,
                    'change_rate': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ KOSPI 폴백 추출 실패: {e}")
            return None
    
    def _extract_kosdaq_data(self, soup):
        """KOSDAQ 데이터 추출 - HTML 요소 ID/클래스 기반"""
        try:
            # KOSDAQ 가격을 ID로 직접 찾기
            kosdaq_price_elem = soup.find('span', id='KOSDAQ_now')
            
            if kosdaq_price_elem:
                price_str = kosdaq_price_elem.get_text().replace(',', '')
                price = float(price_str)
                print(f"🔍 KOSDAQ 가격 발견 (ID): {price:,.2f}")
                
                # 방법 1: KOSDAQ 등락 정보를 KOSPI와 동일한 방식으로 찾기
                # KOSDAQ 관련 섹션에서 형제 요소 찾기
                kosdaq_section = soup.find('div', class_='type_2')
                if kosdaq_section:
                    # KOSDAQ 가격과 등락 정보가 있는 요소 찾기
                    kosdaq_elements = kosdaq_section.find_all('span')
                    for i, elem in enumerate(kosdaq_elements):
                        elem_text = elem.get_text().strip()
                        if '코스닥' in elem_text:
                            print(f"🔍 KOSDAQ 요소 {i+1}: {elem_text}")
                            
                            # 이 요소의 부모에서 형제 요소들 확인
                            parent = elem.parent
                            if parent:
                                siblings = parent.find_all('span')
                                for j, sibling in enumerate(siblings):
                                    sibling_text = sibling.get_text().strip()
                                    sibling_class = sibling.get('class', [])
                                    print(f"🔍 KOSDAQ 형제 요소 {j+1}: {sibling_text} (클래스: {sibling_class})")
                                
                                # 형제 요소 3번에서 등락 정보 추출 (KOSPI와 동일한 패턴)
                                if len(siblings) >= 3:
                                    change_sibling = siblings[2]  # 3번째 형제 요소
                                    change_sibling_text = change_sibling.get_text().strip()
                                    print(f"🎯 KOSDAQ 등락 형제 요소: {change_sibling_text}")
                                    
                                    # 등락 정보 파싱: "0.68 +0.08%상승" 형식
                                    change_pattern = r'([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%'
                                    change_match = re.search(change_pattern, change_sibling_text)
                                    
                                    if change_match:
                                        change_str = change_match.group(1)
                                        change_rate = float(change_match.group(2))
                                        
                                        # 등락 값의 부호를 등락률과 일치시키기
                                        if change_rate < 0:
                                            if not change_str.startswith('-'):
                                                change_str = '-' + change_str
                                        else:
                                            if not change_str.startswith('+'):
                                                change_str = '+' + change_str
                                        
                                        change = float(change_str)
                                        
                                        print(f"🎯 KOSDAQ 등락 정보 파싱 성공: {change:+,.2f}, {change_rate:+.2f}%")
                                        print(f"🔍 부호 일치 확인: 등락 {change:+,.2f}, 등락률 {change_rate:+.2f}%")
                                        
                                        return {
                                            'symbol': 'KOSDAQ',
                                            'price': price,
                                            'change': change,
                                            'change_rate': change_rate,
                                            'timestamp': datetime.now().isoformat()
                                        }
                
                # 방법 2: 전체 HTML에서 KOSDAQ 등락 정보 찾기 (더 유연한 방식)
                html_text = soup.get_text()
                
                # KOSDAQ 관련 텍스트에서 등락 정보 찾기
                kosdaq_pattern = r'코스닥\s+\d{1,3}(?:,\d{3})*\.\d{2}\s+([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%'
                kosdaq_match = re.search(kosdaq_pattern, html_text)
                
                if kosdaq_match:
                    change_str = kosdaq_match.group(1)
                    change_rate = float(kosdaq_match.group(2))
                    
                    # 등락 값의 부호를 등락률과 일치시키기
                    if change_rate < 0:
                        if not change_str.startswith('-'):
                            change_str = '-' + change_str
                    else:
                        if not change_str.startswith('+'):
                            change_str = '+' + change_str
                    
                    change = float(change_str)
                    
                    print(f"🎯 KOSDAQ 등락 정보 발견 (전체 텍스트): {change:+,.2f}, {change_rate:+.2f}%")
                    print(f"🔍 부호 일치 확인: 등락 {change:+,.2f}, 등락률 {change_rate:+.2f}%")
                    
                    return {
                        'symbol': 'KOSDAQ',
                        'price': price,
                        'change': change,
                        'change_rate': change_rate,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # 등락 정보를 찾지 못한 경우 가격만 반환
                print(f"⚠️ KOSDAQ 등락 정보 없음, 가격만 반환")
                return {
                    'symbol': 'KOSDAQ',
                    'price': price,
                    'change': 0.0,
                    'change_rate': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            
            # ID로 찾지 못한 경우 기존 방식 시도
            return self._extract_kosdaq_data_fallback(soup)
            
        except Exception as e:
            print(f"❌ KOSDAQ 데이터 추출 실패: {e}")
            return None
    
    def _extract_kosdaq_data_fallback(self, soup):
        """KOSDAQ 데이터 추출 - 폴백 방식"""
        try:
            html_text = soup.get_text()
            
            # KOSDAQ 가격 추출
            price_pattern = r'코스닥\s+(\d{1,3}(?:,\d{3})*\.\d{2})'
            price_match = re.search(price_pattern, html_text)
            
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                price = float(price_str)
                print(f"🔍 KOSDAQ 가격 발견 (폴백): {price:,.2f}")
                
                return {
                    'symbol': 'KOSDAQ',
                    'price': price,
                    'change': 0.0,
                    'change_rate': 0.0,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ KOSDAQ 폴백 추출 실패: {e}")
            return None
    
    def _extract_sector_data(self, soup):
        """HTML에서 업종별 시세 데이터 추출"""
        try:
            sectors = {"top": [], "bottom": []}
            
            # 업종별 시세 테이블 찾기
            sector_table = soup.find('table', class_='type_1')
            if not sector_table:
                print("⚠️ 업종별 시세 테이블을 찾을 수 없음")
                return None
            
            # 업종 행들 찾기
            sector_rows = sector_table.find_all('tr')[1:]  # 헤더 제외
            
            sector_list = []
            for row in sector_rows[:10]:  # 상위 10개 업종
                cells = row.find_all('td')
                if len(cells) >= 4:
                    sector_name = cells[0].get_text(strip=True)
                    change_rate = cells[3].get_text(strip=True)
                    
                    # 등락률 파싱
                    try:
                        rate = float(change_rate.replace('%', ''))
                        sector_list.append({
                            "name": sector_name,
                            "change_rate": rate
                        })
                    except:
                        continue
            
            # 등락률 기준으로 정렬
            sector_list.sort(key=lambda x: x["change_rate"], reverse=True)
            
            # 상위/하위 업종 분류
            sectors["top"] = sector_list[:3]  # 상위 3개
            sectors["bottom"] = sector_list[-3:]  # 하위 3개
            
            print(f"📊 상위 업종: {[s['name'] for s in sectors['top']]}")
            print(f"📉 하위 업종: {[s['name'] for s in sectors['bottom']]}")
            
            return sectors
            
        except Exception as e:
            print(f"❌ 업종별 시세 데이터 추출 실패: {e}")
            return None
    
    def _extract_movers_data(self, soup):
        """HTML에서 특징주 데이터 추출"""
        try:
            movers = []
            
            # 거래량 급증 테이블 찾기
            movers_table = soup.find('table', class_='type_1')
            if not movers_table:
                print("⚠️ 거래량 급증 테이블을 찾을 수 없음")
                return None
            
            # 특징주 행들 찾기
            mover_rows = movers_table.find_all('tr')[1:]  # 헤더 제외
            
            for row in mover_rows[:5]:  # 상위 5개 종목
                cells = row.find_all('td')
                if len(cells) >= 4:
                    stock_name = cells[0].get_text(strip=True)
                    stock_code = cells[1].get_text(strip=True)
                    change_rate = cells[3].get_text(strip=True)
                    
                    # 등락률 파싱
                    try:
                        rate = float(change_rate.replace('%', ''))
                        movers.append({
                            "name": stock_name,
                            "code": stock_code,
                            "change_rate": rate
                        })
                    except:
                        continue
            
            print(f"🚀 특징주 {len(movers)}개 수집: {len(movers)}개")
            
            return movers
            
        except Exception as e:
            print(f"❌ 특징주 데이터 추출 실패: {e}")
            return None
    
    def save_to_json(self, data, filename="naver_market_data.json"):
        """데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 데이터 저장 완료: {filename}")
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    
    def print_market_summary(self, data):
        """시장 데이터 요약 출력"""
        if 'error' in data:
            print(f"❌ 오류 발생: {data['error']}")
            return
        
        print("\n" + "=" * 60)
        print("📊 네이버 금융 시장 데이터 요약")
        print("=" * 60)
        
        if 'kospi' in data:
            kospi = data['kospi']
            print(f"📊 KOSPI: {kospi['price']:,.2f} ({kospi['change']:+,.2f}, {kospi['change_rate']:+.2f}%)")
        
        if 'kosdaq' in data:
            kosdaq = data['kosdaq']
            print(f"📈 KOSDAQ: {kosdaq['price']:,.2f} ({kosdaq['change']:+,.2f}, {kosdaq['change_rate']:+.2f}%)")
        
        # 세계지수 정보 출력
        if 'world' in data:
            world = data['world']
            print("\n🌍 세계지수 현황:")
            
            if 'sp500' in world:
                sp500 = world['sp500']
                print(f"📊 S&P 500: {sp500['price']:,.2f} ({sp500['change']:+,.2f}, {sp500['change_rate']:+.2f}%)")
            
            if 'nasdaq' in world:
                nasdaq = world['nasdaq']
                print(f"📈 나스닥: {nasdaq['price']:,.2f} ({nasdaq['change']:+,.2f}, {nasdaq['change_rate']:+.2f}%)")
            
            if 'dow' in world:
                dow = world['dow']
                print(f"🏭 다우: {dow['price']:,.2f} ({dow['change']:+,.2f}, {dow['change_rate']:+.2f}%)")
        
        # 섹터 정보 출력
        if 'sectors' in data:
            sectors = data['sectors']
            print("\n🏭 업종별 현황:")
            if sectors["top"]:
                print("📈 상위 업종:")
                for s in sectors["top"]:
                    print(f"   - {s['name']} ({s['change_rate']:+.1f}%)")
            if sectors["bottom"]:
                print("📉 하위 업종:")
                for s in sectors["bottom"]:
                    print(f"   - {s['name']} ({s['change_rate']:+.1f}%)")

        # 특징주 정보 출력
        if 'movers' in data:
            movers = data['movers']
            print("\n🚀 특징주 현황:")
            for m in movers:
                print(f"   - {m['name']} ({m['change_rate']:+.1f}%)")
        
        print(f"⏰ 수집 시간: {data.get('timestamp', 'N/A')}")
        print(f"🔗 데이터 소스: {data.get('source', 'N/A')}")
        print("=" * 60)

def main():
    """메인 실행 함수"""
    print("🚀 네이버 금융 지수 데이터 수집기 시작")
    print("=" * 60)
    
    # 스크래퍼 초기화
    scraper = NaverFinanceScraper()
    
    # 데이터 수집
    market_data = scraper.get_market_data()
    
    # 결과 출력
    scraper.print_market_summary(market_data)
    
    # JSON 파일로 저장
    scraper.save_to_json(market_data)
    
    print("\n✅ 데이터 수집 완료!")

if __name__ == "__main__":
    main()
