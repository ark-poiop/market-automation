#!/usr/bin/env python3
"""
08:30 한국 개장 전 슬롯
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
    
    try:
        # 포스터 초기화
        poster = MarketPoster()
        
        # 네이버 데이터 어댑터 초기화
        naver_adapter = NaverDataAdapter()
        
        # 네이버 데이터 로드 및 변환
        naver_data = naver_adapter.load_naver_data()
        
        if naver_data:
            print("📊 네이버 데이터 로드 완료")
            
            # 한국 개장 전 형식으로 변환
            data = naver_adapter.convert_to_kr_preopen_format(naver_data)
            print("🔄 데이터 형식 변환 완료")
            
            # 포스팅 실행
            result = poster.post_kr_preopen(data)
            
            if result["success"]:
                print("✅ 포스팅 성공")
                if result.get("dry_run"):
                    print("🔒 DRY RUN 모드로 실행됨")
            else:
                print(f"❌ 포스팅 실패: {result.get('error', 'Unknown error')}")
                
        else:
            print("❌ 네이버 데이터를 로드할 수 없음")
            print("기본 데이터로 포스팅을 시도합니다.")
            
            # 기본 데이터로 포스팅 시도
            data = naver_adapter.convert_to_kr_preopen_format({})
            result = poster.post_kr_preopen(data)
            
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        sys.exit(1)
    
    print(f"🏁 {__file__} 실행 완료")

if __name__ == "__main__":
    main()
