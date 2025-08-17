"""
Threads API 클라이언트
실제 포스팅 또는 프리뷰 모드
"""

import requests
import json
from typing import Dict, Any, Optional
from ..config import config

class ThreadsClient:
    def __init__(self):
        self.config = config
        self.access_token = self.config.get_threads_access_token()
        self.user_id = self.config.get_threads_user_id()
        self.dry_run = self.config.is_dry_run()
        
        # Threads API 엔드포인트 (실제)
        self.base_url = "https://graph.threads.net/v1.0"
        self.session_id = None
    
    def login(self) -> bool:
        """Threads 로그인 (액세스 토큰 기반)"""
        if self.dry_run:
            print("🔒 DRY RUN 모드: 실제 로그인 건너뜀")
            return True
        
        if not self.access_token:
            print("❌ Threads 액세스 토큰이 설정되지 않음")
            return False
        
        try:
            # 액세스 토큰으로 인증 확인
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 간단한 API 호출로 토큰 유효성 확인
            response = requests.get(f"{self.base_url}/me?fields=id,name", headers=headers)
            
            if response.status_code == 200:
                print("✅ Threads 로그인 성공")
                self.session_id = self.access_token
                return True
            else:
                print(f"❌ Threads 로그인 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Threads 로그인 오류: {e}")
            return False
    
    def post(self, content: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """포스트 작성"""
        if self.dry_run:
            print("🔒 DRY RUN 모드: 실제 포스팅 건너뜀")
            print("=" * 50)
            print("📝 포스트 내용:")
            print(content)
            print("=" * 50)
            return {"success": True, "dry_run": True, "content": content}
        
        if not self.is_logged_in():
            if not self.login():
                return {"success": False, "error": "Login failed"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text": content,
                "user_id": self.user_id
            }
            
            if reply_to:
                data["reply_to"] = reply_to
            
            # Threads API는 2단계 프로세스를 사용합니다
            # 1단계: 미디어 컨테이너 생성
            data["media_type"] = "TEXT"  # 대문자로 변경
            response = requests.post(f"{self.base_url}/{self.user_id}/threads", headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                container_id = result.get("id")
                
                # 2단계: 컨테이너 게시
                import time
                time.sleep(2)  # Facebook 권장사항: 30초, 테스트용으로 2초
                
                publish_data = {"creation_id": container_id}
                publish_response = requests.post(f"{self.base_url}/{self.user_id}/threads_publish", headers=headers, json=publish_data)
                
                if publish_response.status_code == 200:
                    publish_result = publish_response.json()
                    return {
                        "success": True,
                        "post_id": publish_result.get("id"),
                        "container_id": container_id,
                        "content": content,
                        "response": publish_result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Publish API Error: {publish_response.status_code}",
                        "container_id": container_id,
                        "response": publish_response.text
                    }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_with_reply(self, main_content: str, reply_content: str) -> Dict[str, Any]:
        """메인 포스트 + 댓글 작성"""
        if self.dry_run:
            print("🔒 DRY RUN 모드: 실제 포스팅 건너뜀")
            print("=" * 50)
            print("📝 메인 포스트:")
            print(main_content)
            print("\n💬 댓글:")
            print(reply_content)
            print("=" * 50)
            return {"success": True, "dry_run": True, "main": main_content, "reply": reply_content}
        
        # 메인 포스트 작성
        main_result = self.post(main_content)
        if not main_result["success"]:
            return main_result
        
        # 댓글 작성
        reply_result = self.post(reply_content, reply_to=main_result["post_id"])
        if not reply_result["success"]:
            return {
                "success": False,
                "error": f"Main post succeeded but reply failed: {reply_result['error']}",
                "main_post_id": main_result["post_id"]
            }
        
        return {
            "success": True,
            "main_post_id": main_result["post_id"],
            "reply_post_id": reply_result["post_id"],
            "main": main_content,
            "reply": reply_content
        }
    
    def is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        return self.session_id is not None or self.dry_run
