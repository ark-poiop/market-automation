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
    idx = doc["indices"]
    
    # 섹터 요약 생성
    sectors = doc.get("sectors", {})
    sector_line = composer.compose_sector_summary(
        sectors.get("top", []),
        sectors.get("bottom", [])
    )
    
    # 특징주 요약 생성
    movers = doc.get("movers", [])
    movers_block = composer.compose_movers_summary(movers)
    
    return US_CLOSE.format(
        date=doc["date"],
        spx=composer.format_price(idx["spx"]["price"]),
        spx_diff=composer.format_percentage(idx["spx"]["diff"], False),
        spx_pct=composer.format_percentage(idx["spx"]["pct"]),
        spx_comment=idx["spx"]["comment"],
        ndx=composer.format_price(idx["ndx"]["price"]),
        ndx_diff=composer.format_percentage(idx["ndx"]["diff"], False),
        ndx_pct=composer.format_percentage(idx["ndx"]["pct"]),
        ndx_comment=idx["ndx"]["comment"],
        djia=composer.format_price(idx["djia"]["price"]),
        djia_diff=composer.format_percentage(idx["djia"]["diff"], False),
        djia_pct=composer.format_percentage(idx["djia"]["pct"]),
        djia_comment=idx["djia"]["comment"],
        rty=composer.format_price(idx["rty"]["price"]),
        rty_diff=composer.format_percentage(idx["rty"]["diff"], False),
        rty_pct=composer.format_percentage(idx["rty"]["pct"]),
        rty_comment=idx["rty"]["comment"],
        sector_line=sector_line,
        movers_block=movers_block
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
