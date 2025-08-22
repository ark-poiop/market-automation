"""
LLM을 사용한 콘텐츠 합성
숫자 기반 요약만 수행
"""

import json
import openai
from typing import Dict, Any, List
from ..config import config

class ContentComposer:
    def __init__(self):
        self.config = config
        # OpenAI API 설정
        openai.api_key = self.config.get_openai_api_key()
    
    def compose_sector_summary(self, top_sectors: List[Dict], bottom_sectors: List[Dict]) -> str:
        """섹터 요약 생성 (LLM 사용)"""
        if not top_sectors and not bottom_sectors:
            return "데이터 부족"
        
        try:
            # LLM 프롬프트 생성
            from .prompts import SECTOR_LINE
            
            top_json = json.dumps([{
                "name": self.config.get_sector_alias(sector["name"]),
                "ret1d": sector["ret1d"],
                "breadth": sector["breadth"]
            } for sector in top_sectors[:3]], ensure_ascii=False)
            
            bottom_json = json.dumps([{
                "name": self.config.get_sector_alias(sector["name"]),
                "ret1d": sector["ret1d"],
                "breadth": sector["breadth"]
            } for sector in bottom_sectors[:2]], ensure_ascii=False)
            
            prompt = SECTOR_LINE.format(top_json=top_json, bottom_json=bottom_json)
            
            # OpenAI API 호출 (최신 버전)
            client = openai.OpenAI(api_key=self.config.get_openai_api_key())
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 증시 애널리스트입니다. 숫자만을 근거로 간결하게 요약하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"⚠️ LLM 요약 실패, 규칙 기반으로 대체: {e}")
            # LLM 실패 시 규칙 기반으로 대체
            return self._compose_sector_summary_rule_based(top_sectors, bottom_sectors)
    
    def _compose_sector_summary_rule_based(self, top_sectors: List[Dict], bottom_sectors: List[Dict]) -> str:
        """섹터 요약 생성 (규칙 기반, LLM 실패 시 사용)"""
        if not top_sectors and not bottom_sectors:
            return "데이터 부족"
        
        # 상위 섹터 처리
        top_text = ""
        if top_sectors:
            top_names = []
            for sector in top_sectors[:3]:  # 상위 3개만
                korean_name = self.config.get_sector_alias(sector["name"])
                emoji = self.config.get_sector_emoji(korean_name)
                top_names.append(f"{korean_name}{emoji}")
            top_text = "·".join(top_names)
        
        # 하위 섹터 처리
        bottom_text = ""
        if bottom_sectors:
            bottom_names = []
            for sector in bottom_sectors[:2]:  # 하위 2개만
                korean_name = self.config.get_sector_alias(sector["name"])
                emoji = self.config.get_sector_emoji(korean_name)
                bottom_names.append(f"{korean_name}{emoji}")
            bottom_text = "·".join(bottom_names)
        
        # 요약 생성
        if top_text and bottom_text:
            return f"{top_text} 강세, {bottom_text} 약세"
        elif top_text:
            return f"{top_text} 강세"
        elif bottom_text:
            return f"{bottom_text} 약세"
        else:
            return "섹터 데이터 부족"
    
    def compose_movers_summary(self, movers: List[Dict]) -> str:
        """특징주 요약 생성 (규칙 기반)"""
        if not movers:
            return "특징주 데이터 부족"
        
        # 상위 3-5개 종목만 선택
        selected_movers = movers[:min(5, len(movers))]
        
        mover_lines = []
        for mover in selected_movers:
            symbol = mover.get("symbol", "")
            reason = mover.get("reason", "")
            ret1d = mover.get("ret1d", 0)
            
            if symbol and reason:
                line = f"{symbol} — {reason} ({ret1d:+.1f}%)"
                mover_lines.append(line)
        
        return "\n".join(mover_lines) if mover_lines else "특징주 데이터 부족"
    
    def format_number(self, value: float, decimals: int = 2) -> str:
        """숫자 포맷팅"""
        if value is None:
            return "N/A"
        
        if decimals == 0:
            return f"{value:.0f}"
        elif decimals == 1:
            return f"{value:.1f}"
        elif decimals == 2:
            return f"{value:.2f}"
        else:
            return f"{value:.2f}"
    
    def format_percentage(self, value: float, include_sign: bool = True) -> str:
        """퍼센트 포맷팅"""
        if value is None:
            return "N/A"
        
        if include_sign and value > 0:
            return f"+{value:.2f}%"
        else:
            return f"{value:.2f}%"
    
    def format_price(self, value: float) -> str:
        """가격 포맷팅"""
        if value is None:
            return "N/A"
        
        if value >= 1000:
            return f"{value:,.1f}"
        else:
            return f"{value:.2f}"
    
    def translate_to_korean(self, english_text: str, context: str = "market") -> str:
        """GPT를 이용한 한국어 번역 및 요약"""
        if not english_text or english_text in ["데이터 없음", "- 추가 시장 뉴스 없음", "- 주요 경제지표 발표 없음"]:
            return english_text
        
        try:
            client = openai.OpenAI(api_key=self.config.get_openai_api_key())
            
            if context == "news":
                system_content = "당신은 금융 뉴스 번역 전문가입니다. 영어 뉴스를 자연스러운 한국어로 번역하고 간결하게 요약하세요. 각 뉴스는 '- '로 시작하고, 50자 이내로 요약하세요."
                user_content = f"다음 영어 뉴스들을 한국어로 번역하고 요약해주세요:\n\n{english_text}"
            elif context == "sector":
                system_content = "당신은 증시 섹터 분석 전문가입니다. 영어 섹터명을 한국어로 번역하고 간결하게 표현하세요."
                user_content = f"다음 섹터 정보를 한국어로 번역해주세요:\n\n{english_text}"
            else:  # market general
                system_content = "당신은 증시 분석 전문가입니다. 영어 텍스트를 자연스러운 한국어로 번역하세요."
                user_content = f"다음 텍스트를 한국어로 번역해주세요:\n\n{english_text}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            korean_text = response.choices[0].message.content.strip()
            print(f"✅ GPT 번역 성공: {english_text[:30]}... → {korean_text[:30]}...")
            return korean_text
            
        except Exception as e:
            print(f"⚠️ GPT 번역 실패, 원본 유지: {e}")
            return english_text
    
    def compose_korean_summary(self, data: Dict[str, Any], slot_type: str = "general") -> Dict[str, str]:
        """GPT를 이용한 한국어 데이터 요약"""
        result = {}
        
        try:
            # 뉴스/이슈 번역
            if "main_news" in data:
                result["main_news"] = self.translate_to_korean(data["main_news"], "news")
            
            if "additional_news" in data:
                result["additional_news"] = self.translate_to_korean(data["additional_news"], "news")
            
            # 섹터는 이미 한국어이므로 그대로 유지
            if "sector_top3" in data:
                result["sector_top3"] = data["sector_top3"]
            
            # 급등/급락 종목은 이미 한국어이므로 그대로 유지
            if "top_gainers" in data:
                result["top_gainers"] = data["top_gainers"]
            
            if "top_losers" in data:
                result["top_losers"] = data["top_losers"]
            
            print(f"✅ 한국어 요약 완료: {len(result)}개 필드")
            return result
            
        except Exception as e:
            print(f"⚠️ 한국어 요약 실패: {e}")
            return {
                "main_news": data.get("main_news", "- 주요 이슈 없음"),
                "additional_news": data.get("additional_news", "- 추가 뉴스 없음"),
                "sector_top3": data.get("sector_top3", "데이터 없음"),
                "top_gainers": data.get("top_gainers", "데이터 없음"),
                "top_losers": data.get("top_losers", "데이터 없음")
            }