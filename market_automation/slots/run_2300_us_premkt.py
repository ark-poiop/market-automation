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
from market_automation.datasource.naver_adapter import NaverDataAdapter

def main():
    """메인 실행 함수"""
    print(f"🕐 {__file__} 실행 시작")
    print(f"🔧 DRY_RUN 모드: {config.is_dry_run()}")
    
    try:
        # 포스터 초기화
        poster = MarketPoster()
        
        # 네이버 데이터 어댑터 초기화
        naver_adapter = NaverDataAdapter()
        
        # 네이버 데이터 로드 및 변환
        naver_data = naver_adapter.load_naver_data()
        
        if naver_data:
            print("📊 네이버 데이터 로드 완료")
            
            # 미국 장전 형식으로 변환
            sample_data = naver_adapter.convert_to_us_premkt_format(naver_data)
            print("🔄 데이터 형식 변환 완료")
            
            print("📊 미국 장전 데이터 준비 완료")
            print(f"📅 날짜: {sample_data['date']}")
            print(f"📊 S&P 500: {sample_data['spx']} ({sample_data['spx_pct']:+.2f}%)")
            print(f"📈 Nasdaq: {sample_data['ndx']} ({sample_data['ndx_pct']:+.2f}%)")
            print(f"🏭 Dow Jones: {sample_data['djia']} ({sample_data['djia_pct']:+.2f}%)")
            print(f"🏭 섹터 Top 3: {sample_data['sector_top3']}")
            print(f"📰 이슈: {sample_data['news_events']}")
            print(f"💬 급등: {sample_data['top_gainers']}")
            print(f"💬 급락: {sample_data['top_losers']}")
            
            # 포스팅은 하지 않고 로컬에서만 결과물 확인
            print("\n🔄 미국 장전 포스트 생성 중...")
            result = poster.post_us_premkt(sample_data)
            
            if result["success"]:
                print("✅ 미국 장전 포스트 생성 성공")
                print("\n" + "="*60)
                print("📝 생성된 포스트 내용:")
                print("="*60)
                print(result.get("content", "콘텐츠 없음"))
                print("="*60)
                print("🔒 실제 포스팅은 건너뜀 (로컬 테스트 모드)")
            else:
                print(f"❌ 미국 장전 포스트 생성 실패: {result.get('error', 'Unknown error')}")
        else:
            print("❌ 네이버 데이터 로드 실패")
            
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n🏁 {__file__} 실행 완료")

if __name__ == "__main__":
    main()
