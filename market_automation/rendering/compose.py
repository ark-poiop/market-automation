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
