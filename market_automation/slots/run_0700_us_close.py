#!/usr/bin/env python3
"""
07:00 미국 증시 마감 슬롯
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
        
        # 샘플 데이터 로드 (실제 운영 시에는 API에서 데이터 수집)
        sample_file = project_root / "samples" / "sample_us_close.json"
        
        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print("📊 샘플 데이터 로드 완료")
            print(f"📅 날짜: {data['date']}")
            print(f"📈 지수 개수: {len(data['indices'])}")
            print(f"🏭 섹터 개수: 상위 {len(data.get('sectors', {}).get('top', []))}, 하위 {len(data.get('sectors', {}).get('bottom', []))}")
            print(f"🚀 특징주 개수: {len(data.get('movers', []))}")
            
            # 포스팅 실행
            print("\n🔄 포스팅 실행 중...")
            result = poster.post_us_close(data)
            
            if result["success"]:
                print("✅ 포스팅 성공")
                if result.get("dry_run"):
                    print("🔒 DRY RUN 모드로 실행됨")
                    print("\n" + "="*60)
                    print("📝 생성된 포스트 내용:")
                    print("="*60)
                    print(result.get("content", "콘텐츠 없음"))
                    print("="*60)
            else:
                print(f"❌ 포스팅 실패: {result.get('error', 'Unknown error')}")
                
        else:
            print("❌ 샘플 데이터 파일을 찾을 수 없음")
            print(f"경로: {sample_file}")
            
    except Exception as e:
        print(f"💥 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n🏁 {__file__} 실행 완료")

if __name__ == "__main__":
    main()
