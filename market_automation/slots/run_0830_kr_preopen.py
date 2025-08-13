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

def main():
    """메인 실행 함수"""
    print(f"🕐 {__file__} 실행 시작")
    
    try:
        # 포스터 초기화
        poster = MarketPoster()
        
        # 샘플 데이터 로드 (실제 운영 시에는 API에서 데이터 수집)
        sample_file = project_root / "samples" / "sample_kr_preopen.json"
        
        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print("📊 샘플 데이터 로드 완료")
            
            # 포스팅 실행
            result = poster.post_kr_preopen(data)
            
            if result["success"]:
                print("✅ 포스팅 성공")
                if result.get("dry_run"):
                    print("🔒 DRY RUN 모드로 실행됨")
            else:
                print(f"❌ 포스팅 실패: {result.get('error', 'Unknown error')}")
                
        else:
            print("❌ 샘플 데이터 파일을 찾을 수 없음")
            print(f"경로: {sample_file}")
            
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        sys.exit(1)
    
    print(f"🏁 {__file__} 실행 완료")

if __name__ == "__main__":
    main()
