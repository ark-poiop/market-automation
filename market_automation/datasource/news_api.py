"""
NewsAPI를 사용한 뉴스 및 이슈 데이터 수집
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..config import config

class NewsAPIClient:
    """NewsAPI 클라이언트"""
    
    def __init__(self):
        self.api_key = config.get_news_api_key()
        self.base_url = "https://newsapi.org/v2"
        
    def get_market_news(self, query: str = "stock market", language: str = "en", page_size: int = 5) -> List[Dict[str, Any]]:
        """주식 시장 관련 뉴스 가져오기"""
        if not self.api_key:
            print("⚠️ NEWS_API_KEY가 설정되지 않음")
            return []
            
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',
                'pageSize': page_size,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'ok':
                articles = data['articles']
                return [{
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'publishedAt': article['publishedAt'],
                    'source': article['source']['name']
                } for article in articles]
            else:
                print(f"❌ NewsAPI 오류: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ NewsAPI 요청 실패: {e}")
            return []
        except Exception as e:
            print(f"❌ NewsAPI 처리 오류: {e}")
            return []
    
    def get_economic_events(self) -> List[str]:
        """경제 이벤트 및 지표 관련 뉴스 가져오기"""
        keywords = ["FOMC", "CPI", "PPI", "employment", "GDP", "inflation", "Federal Reserve"]
        events = []
        
        for keyword in keywords:
            news = self.get_market_news(query=keyword, page_size=2)
            for article in news:
                title = article['title']
                if any(kw.lower() in title.lower() for kw in keywords):
                    events.append(f"- {title[:60]}...")
                    if len(events) >= 3:  # 최대 3개까지만
                        break
        
        return events if events else ["- 주요 경제지표 발표 없음"]
    
    def get_market_insights(self) -> str:
        """시장 인사이트 요약"""
        news = self.get_market_news(query="stock market analysis", page_size=3)
        
        if not news:
            return "주요 시장 이슈 없음"
        
        insights = []
        for article in news:
            title = article['title']
            insights.append(f"- {title[:50]}...")
        
        return "\n".join(insights)
