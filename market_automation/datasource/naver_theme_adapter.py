#!/usr/bin/env python3
"""
네이버 금융 테마 등락 정보 수집 어댑터
https://finance.naver.com/sise/theme.naver 페이지에서 테마별 등락률 수집
"""

import requests
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

class NaverThemeAdapter:
    """네이버 금융 테마 등락 정보 수집 어댑터"""
    
    def __init__(self):
        self.base_url = "https://finance.naver.com"
        self.theme_url = f"{self.base_url}/sise/theme.naver"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_theme_data(self, top_count: int = 3) -> Optional[Dict[str, Any]]:
        """테마 등락 정보 수집"""
        try:
            print(f"🔍 네이버 테마 등락 정보 수집 중... (상위 {top_count}개)")
            
            # 페이지 요청 (EUC-KR 인코딩 처리)
            response = self.session.get(self.theme_url, timeout=10)
            response.raise_for_status()
            
            # EUC-KR 인코딩으로 디코딩
            response.encoding = 'euc-kr'
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 테마 테이블 찾기 (type_1 theme 클래스)
            theme_table = soup.find('table', {'class': 'type_1 theme'})
            
            if not theme_table:
                print("❌ 테마 테이블을 찾을 수 없음")
                # 대안: 다른 테이블 찾기
                theme_table = soup.find('table', {'summary': re.compile(r'테마.*등락')})
                if not theme_table:
                    print("❌ 대안 테이블도 찾을 수 없음")
                    return None
            
            # 테마 데이터 추출
            themes = self._extract_themes_from_table(theme_table, top_count)
            
            if themes:
                return {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'themes': themes,
                    'source': 'naver_theme',
                    'top_count': top_count
                }
            else:
                print("❌ 테마 데이터 추출 실패")
                return None
                
        except requests.RequestException as e:
            print(f"❌ 요청 오류: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None
    
    def _extract_themes_from_table(self, table, top_count: int) -> List[Dict[str, Any]]:
        """테이블에서 테마 데이터 추출"""
        themes = []
        
        try:
            # 테마 행 찾기
            rows = table.find_all('tr')
            
            for row in rows:
                # 헤더 행 건너뛰기
                if row.find('th'):
                    continue
                
                # 테마 링크 찾기
                theme_link = row.find('a')
                if not theme_link:
                    continue
                
                # 테마명과 링크 추출
                theme_name = theme_link.get_text(strip=True)
                theme_url = theme_link.get('href')
                
                if not theme_name or not theme_url:
                    continue
                
                # 등락률 추출 (두 번째 열)
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue
                
                change_rate_cell = cells[1]
                change_rate_text = change_rate_cell.get_text(strip=True)
                
                # 등락률 파싱 (+4.66% -> 4.66)
                change_rate = self._parse_change_rate(change_rate_text)
                
                if change_rate is not None:
                    themes.append({
                        'name': theme_name,
                        'change_rate': change_rate,
                        'url': f"{self.base_url}{theme_url}",
                        'rank': len(themes) + 1
                    })
                    
                    # 상위 N개만 수집
                    if len(themes) >= top_count:
                        break
            
            # 등락률 기준으로 정렬 (내림차순)
            themes.sort(key=lambda x: x.get('change_rate', 0), reverse=True)
            
            # 순위 재정렬
            for i, theme in enumerate(themes):
                theme['rank'] = i + 1
            
            return themes
            
        except Exception as e:
            print(f"❌ 테마 테이블 파싱 오류: {e}")
            return []
    
    def _parse_change_rate(self, change_rate_text: str) -> Optional[float]:
        """등락률 텍스트를 숫자로 파싱"""
        try:
            # +4.66% -> 4.66, -2.45% -> -2.45
            match = re.search(r'([+-]?\d+\.?\d*)%?', change_rate_text)
            if match:
                return float(match.group(1))
            return None
        except (ValueError, AttributeError):
            return None
    
    def get_top_themes(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """상위 테마 추출"""
        if not data or 'themes' not in data:
            return []
        
        return data.get('themes', [])
    
    def format_theme_summary(self, data: Dict[str, Any]) -> str:
        """테마 요약 포맷팅"""
        if not data or 'themes' not in data:
            return "데이터 없음"
        
        themes = data.get('themes', [])
        
        if not themes:
            return "데이터 없음"
        
        theme_parts = []
        for theme in themes:
            name = theme.get('name', '')
            rate = theme.get('change_rate', 0)
            rank = theme.get('rank', 0)
            
            if rate > 0:
                theme_parts.append(f"{rank}위 {name} (+{rate:.2f}%)")
            else:
                theme_parts.append(f"{rank}위 {name} ({rate:.2f}%)")
        
        return " | ".join(theme_parts)
    
    def save_theme_data(self, data: Dict[str, Any], filename: str = None) -> str:
        """테마 데이터를 파일로 저장"""
        if not filename:
            filename = f"naver_theme_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 테마 데이터 저장 완료: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 파일 저장 오류: {e}")
            return ""

# 테스트용
if __name__ == "__main__":
    adapter = NaverThemeAdapter()
    data = adapter.get_theme_data(top_count=3)
    
    if data:
        print(f"📊 수집된 테마 수: {len(data.get('themes', []))}")
        print(f"📅 날짜: {data.get('date')}")
        print(f"🔍 소스: {data.get('source')}")
        
        # 상위 테마 출력
        themes = adapter.get_top_themes(data)
        print(f"\n🏆 상위 {len(themes)}개 테마:")
        for theme in themes:
            rank = theme.get('rank', 0)
            name = theme.get('name', '')
            rate = theme.get('change_rate', 0)
            print(f"  {rank}위: {name} ({rate:+.2f}%)")
        
        # 테마 요약 출력
        summary = adapter.format_theme_summary(data)
        print(f"\n🏭 테마 요약: {summary}")
        
        # 파일 저장
        adapter.save_theme_data(data)
    else:
        print("❌ 데이터 수집 실패")
