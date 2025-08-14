#!/usr/bin/env python3
"""
23:00 미국 증시 장전 슬롯
라즈베리파이 크론에서 실행
"""

import sys
import os
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from market_automation.posting.poster import MarketPoster
from market_automation.config import config

def main():
    """메인 실행 함수"""
    print(f"🕐 {__file__} 실행 시작")
    print(f"🔧 DRY_RUN 모드: {config.is_dry_run()}")
    
    try:
        # 포스터 초기화
        poster = MarketPoster()
        
        # 샘플 데이터 준비 (실제 운영 시에는 API에서 미국 장전 데이터 수집)
        sample_data = {
            "date": "2025-08-13",
            "us_wrap": {"spx_pct": 1.13, "ndx_pct": 1.39, "djia_pct": 1.10},
            "futures": {"es": 6452.0, "nq": 21720.5, "ym": 44450.0},
            "macro": {"wti": 78.4, "gold": 1950.0, "ust10y": 3.95},
            "today_events": ["美소비자물가지수 20:30", "Fed 의사록 02:00"],
            "focus_sectors": ["기술", "금융", "헬스케어"],
            "risks": ["인플레이션 우려", "Fed 정책 불확실성"]
        }
        
        print("📊 미국 장전 데이터 준비 완료")
        print(f"📅 날짜: {sample_data['date']}")
        print(f"🌏 전일 미증시 — S&P500 {sample_data['us_wrap']['spx_pct']:+.2f}%, Nasdaq {sample_data['us_wrap']['ndx_pct']:+.2f}%, Dow {sample_data['us_wrap']['djia_pct']:+.2f}%")
        print(f"📉 선물 — ES {sample_data['futures']['es']}, NQ {sample_data['futures']['nq']}, YM {sample_data['futures']['ym']}")
        print(f"💱 원자재 — WTI ${sample_data['macro']['wti']}, Gold ${sample_data['macro']['gold']}, 10Y {sample_data['macro']['ust10y']}bp")
        print(f"🗓️ 일정 — {', '.join(sample_data['today_events'])}")
        print(f"📈 포커스 — {', '.join(sample_data['focus_sectors'])}")
        print(f"⚠️ 리스크 — {', '.join(sample_data['risks'])}")
        
        # 포스팅 실행
        print("\n🔄 미국 장전 포스팅 실행 중...")
        result = poster.post_us_premkt(sample_data)
        
        if result["success"]:
            print("✅ 미국 장전 포스팅 성공")
            if result.get("dry_run"):
                print("🔒 DRY RUN 모드로 실행됨")
                print("\n" + "="*60)
                print("📝 생성된 포스트 내용:")
                print("="*60)
                print(result.get("content", "콘텐츠 없음"))
                print("="*60)
        else:
            print(f"❌ 미국 장전 포스팅 실패: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n🏁 {__file__} 실행 완료")

if __name__ == "__main__":
    main()
