#!/usr/bin/env python3
"""
네이버 금융 지수 데이터 수집기
KOSPI, KOSDAQ 실시간 지수 정보를 웹 스크래핑으로 수집
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
            
            return market_data
            
        except Exception as e:
            print(f"❌ 데이터 수집 실패: {e}")
            return {"error": str(e)}
    
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
                
                # 방법 3: 특정 클래스나 ID로 등락 정보 찾기
                change_elem = soup.find('span', class_='num2')
                if change_elem:
                    change_text = change_elem.get_text()
                    print(f"🔍 KOSPI 등락 요소 발견: {change_text}")
                    
                    # 등락 요소의 부모와 형제 요소들도 확인
                    parent = change_elem.parent
                    if parent:
                        parent_text = parent.get_text()
                        print(f"🔍 KOSPI 등락 요소 부모: {parent_text}")
                        
                        # 형제 요소들 확인
                        siblings = parent.find_all('span')
                        for i, sibling in enumerate(siblings):
                            sibling_text = sibling.get_text()
                            sibling_class = sibling.get('class', [])
                            print(f"🔍 KOSPI 형제 요소 {i+1}: {sibling_text} (클래스: {sibling_class})")
                        
                        # 형제 요소 3번에서 등락 정보 추출 (실제로 발견된 위치)
                        if len(siblings) >= 3:
                            change_sibling = siblings[2]  # 3번째 형제 요소
                            change_sibling_text = change_sibling.get_text().strip()
                            print(f"🎯 KOSPI 등락 형제 요소: {change_sibling_text}")
                            
                            # 등락 정보 파싱: "5.18 -0.16%상승" 형식
                            change_pattern = r'([+-]?\d+\.\d+)\s+([+-]\d+\.\d+)%'
                            change_match = re.search(change_pattern, change_sibling_text)
                            
                            if change_match:
                                change_str = change_match.group(1)
                                change_rate = float(change_match.group(2))
                                
                                # 등락 값의 부호를 등락률과 일치시키기
                                # 등락률이 음수면 등락도 음수로, 양수면 등락도 양수로
                                if change_rate < 0:
                                    # 등락률이 음수면 등락도 음수로 처리
                                    if not change_str.startswith('-'):
                                        change_str = '-' + change_str
                                else:
                                    # 등락률이 양수면 등락도 양수로 처리
                                    if not change_str.startswith('+'):
                                        change_str = '+' + change_str
                                
                                change = float(change_str)
                                
                                print(f"🎯 KOSPI 등락 정보 파싱 성공: {change:+,.2f}, {change_rate:+.2f}%")
                                print(f"🔍 부호 일치 확인: 등락 {change:+.2f}, 등락률 {change_rate:+.2f}%")
                                
                                return {
                                    'symbol': 'KOSPI',
                                    'price': price,
                                    'change': change,
                                    'change_rate': change_rate,
                                    'timestamp': datetime.now().isoformat()
                                }
                    
                    # 기존 등락 정보 파싱 시도
                    change_match = re.search(r'([+-]\d+\.\d+)', change_text)
                    if change_match:
                        change = float(change_match.group(1))
                        print(f"🎯 KOSPI 등락 발견: {change:+,.2f}")
                        
                        # 등락률도 찾기
                        rate_match = re.search(r'([+-]\d+\.\d+)%', change_text)
                        if rate_match:
                            change_rate = float(rate_match.group(1))
                            print(f"🎯 KOSPI 등락률 발견: {change_rate:+.2f}%")
                            
                            return {
                                'symbol': 'KOSPI',
                                'price': price,
                                'change': change,
                                'change_rate': change_rate,
                                'timestamp': datetime.now().isoformat()
                            }
                
                # 방법 4: 더 넓은 범위에서 등락 정보 찾기
                # KOSPI 관련 모든 요소에서 등락 정보 검색
                kospi_elements = soup.find_all(text=re.compile(r'코스피'))
                for element in kospi_elements:
                    parent = element.parent
                    if parent:
                        parent_text = parent.get_text()
                        if '코스피' in parent_text and any(char.isdigit() for char in parent_text):
                            print(f"🔍 KOSPI 관련 텍스트: {parent_text[:100]}...")
                            
                            # 등락 정보 패턴 찾기
                            change_pattern = r'([+-]\d+\.\d+)\s+([+-]\d+\.\d+)%'
                            change_match = re.search(change_pattern, parent_text)
                            
                            if change_match:
                                change = float(change_match.group(1))
                                change_rate = float(change_match.group(2))
                                print(f"🎯 KOSPI 등락 정보 발견 (관련 텍스트): {change:+,.2f}, {change_rate:+.2f}%")
                                
                                return {
                                    'symbol': 'KOSPI',
                                    'price': price,
                                    'change': change,
                                    'change_rate': change_rate,
                                    'timestamp': datetime.now().isoformat()
                                }
                
                # 등락 정보를 찾지 못한 경우 가격만 반환
                print(f"⚠️ KOSPI 등락 정보 없음, 가격만 반환")
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
