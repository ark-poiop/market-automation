#!/usr/bin/env python3
"""
샘플 데이터 → 포스트 프리뷰 CLI 도구
사용법: python -m market_automation.cli_preview us_close samples/sample_us_close.json
"""

import json
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from market_automation.rendering.templates import US_CLOSE, KR_PREOPEN
from market_automation.rendering.compose import ContentComposer

def render_us_close(doc):
    """미국 증시 마감 렌더링"""
    composer = ContentComposer()
    
    # 기본값 설정
    spx = doc.get("indices", {}).get("spx", {}).get("price", 0.0)
    spx_pct = doc.get("indices", {}).get("spx", {}).get("pct", 0.0)
    ndx = doc.get("indices", {}).get("ndx", {}).get("price", 0.0)
    ndx_pct = doc.get("indices", {}).get("ndx", {}).get("pct", 0.0)
    djia = doc.get("indices", {}).get("djia", {}).get("price", 0.0)
    djia_pct = doc.get("indices", {}).get("djia", {}).get("pct", 0.0)
    
    # 섹터 데이터 처리
    sectors = doc.get("sectors", {})
    if sectors.get("top"):
        sector_lines = []
        for sector in sectors["top"][:3]:  # 상위 3개만
            name = sector.get("name", "Unknown")
            ret1d = sector.get("ret1d", 0.0)
            sector_lines.append(f"{name} {ret1d:+.1f}%")
        sector_top3 = "\n".join(sector_lines)
    else:
        sector_top3 = "데이터 없음"
    
    # 뉴스/이슈 (기본값)
    news_events = "- 주요 경제지표 발표 없음\n- FOMC, CPI 등 거시 지표 이벤트 없음"
    
    # 급등/급락 종목 (기본값)
    top_gainers = "삼성전자 +2.1%, SK하이닉스 +1.8%, LG에너지솔루션 +1.5%"
    top_losers = "현대차 -1.2%, 기아 -0.9%, 포스코홀딩스 -0.7%"
    
    return US_CLOSE.format(
        date=doc["date"],
        spx=composer.format_price(spx),
        spx_pct=composer.format_percentage(spx_pct),
        ndx=composer.format_price(ndx),
        ndx_pct=composer.format_percentage(ndx_pct),
        djia=composer.format_price(djia),
        djia_pct=composer.format_percentage(djia_pct),
        sector_top3=sector_top3,
        news_events=news_events,
        top_gainers=top_gainers,
        top_losers=top_losers
    )

def render_kr_preopen(doc):
    """한국 개장 전 렌더링"""
    composer = ContentComposer()
    
    return KR_PREOPEN.format(
        date=doc["date"],
        spx_pct=composer.format_percentage(doc["us_wrap"]["spx_pct"]),
        ndx_pct=composer.format_percentage(doc["us_wrap"]["ndx_pct"]),
        djia_pct=composer.format_percentage(doc["us_wrap"]["djia_pct"]),
        k200f=composer.format_price(doc["futures"]["k200f"]),
        es=composer.format_price(doc["futures"]["es"]),
        nq=composer.format_price(doc["futures"]["nq"]),
        usdkrs=composer.format_price(doc["macro"]["usdkrs"]),
        wti=composer.format_price(doc["macro"]["wti"]),
        ust10y=composer.format_price(doc["macro"]["ust10y"]),
        today_events=" / ".join(doc["today_events"]),
        focus_sectors="·".join(doc["focus_sectors"]),
        risks=", ".join(doc["risks"])
    )

def main():
    """메인 함수"""
    if len(sys.argv) != 3:
        print("사용법: python -m market_automation.cli_preview <kind> <json_file>")
        print("  kind: us_close | kr_preopen")
        print("  json_file: 샘플 JSON 파일 경로")
        sys.exit(1)
    
    kind = sys.argv[1]
    path = sys.argv[2]
    
    # 파일 존재 확인
    if not os.path.exists(path):
        print(f"❌ 파일을 찾을 수 없음: {path}")
        sys.exit(1)
    
    try:
        # JSON 파일 로드
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        
        # 렌더링
        if kind == "us_close":
            result = render_us_close(doc)
        elif kind == "kr_preopen":
            result = render_kr_preopen(doc)
        else:
            print(f"❌ 지원하지 않는 kind: {kind}")
            print("지원: us_close, kr_preopen")
            sys.exit(1)
        
        # 결과 출력
        print("=" * 60)
        print(f"📝 {kind.upper()} 포스트 프리뷰")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
