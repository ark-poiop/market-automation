# 🚀 Market Automation ver1.2 배포 가이드

## 📋 배포 개요

**ver1.2**는 네이버 크롤링 데이터 통합 및 주중 전용 스케줄링이 적용된 버전입니다.

### 🆕 **주요 변경사항**

- ✅ **네이버 금융 크롤링 데이터 통합**
- ✅ **코스피 200 수집 제거** (KOSPI/KOSDAQ만 유지)
- ✅ **환율 및 거래량 정보 제거**로 템플릿 간소화
- ✅ **월요일 8:30 ~ 토요일 07:00 주중 전용 스케줄링**
- ✅ **자동 크론 설정 및 확인 스크립트 추가**
- ✅ **네이버 데이터 어댑터로 실시간 한국 증시 데이터 활용**

## 🖥️ 라즈베리파이 배포 단계

### 1️⃣ **기존 시스템 백업**

```bash
# 현재 작업 디렉토리 백업
cd /home/pi
cp -r market-automation market-automation-backup-$(date +%Y%m%d)

# 크론 설정 백업
crontab -l > crontab-backup-$(date +%Y%m%d).txt
```

### 2️⃣ **새로운 버전 다운로드**

```bash
# 기존 디렉토리 제거
cd /home/pi
rm -rf market-automation

# 새 버전 클론
git clone https://github.com/ark-poiop/market-automation.git
cd market-automation

# ver1.2 태그 체크아웃
git checkout v1.2
```

### 3️⃣ **환경 설정**

```bash
# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
nano .env
```

### 4️⃣ **환경 변수 설정 (.env)**

```bash
# 필수 설정
TZ=Asia/Seoul
DRY_RUN=1  # 최초엔 1로 설정 (프리뷰 모드)

# 한국투자증권 API (한국 증시 데이터)
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here
KIS_VTS=REAL  # REAL: 실전투자, VTS: 모의투자

# Alpaca Markets API (미국 증시 데이터)
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_API_SECRET=your_alpaca_api_secret_here
ALPACA_PAPER=true  # true: Paper Trading, false: Live Trading

# Threads API
THREADS_ACCESS_TOKEN=your_threads_access_token_here
THREADS_USER_ID=your_threads_user_id_here

# OpenAI API (섹터 요약 생성)
OPENAI_API_KEY=your_openai_api_key_here
```

### 5️⃣ **시스템 시간대 설정**

```bash
# KST로 설정
sudo timedatectl set-timezone Asia/Seoul

# 확인
date
timedatectl status
```

### 6️⃣ **자동 크론 설정**

```bash
# 스크립트에 실행 권한 부여
chmod +x setup_cron.sh
chmod +x check_cron.sh

# 크론 설정 자동 적용
./setup_cron.sh

# 크론 설정 확인
./check_cron.sh
```

### 7️⃣ **테스트 실행**

```bash
# 가상환경 활성화
source .venv/bin/activate

# 개별 슬롯 테스트
python market_automation/slots/run_0830_kr_preopen.py
python market_automation/slots/run_1200_kr_midday.py
python market_automation/slots/run_1600_kr_close.py
```

### 8️⃣ **네이버 데이터 수집 테스트**

```bash
# 네이버 크롤링 테스트
python naver_finance_scraper.py

# 데이터 확인
cat naver_market_data.json
```

## 🔧 배포 후 확인사항

### ✅ **크론 설정 확인**

```bash
# 크론 설정 확인
crontab -l

# 크론 서비스 상태 확인
sudo systemctl status cron

# 크론 서비스 자동 시작 설정
sudo systemctl enable cron
```

### ✅ **로그 모니터링**

```bash
# 로그 디렉토리 확인
ls -la /var/log/market/

# 실시간 로그 모니터링
tail -f /var/log/market/market_*.log
```

### ✅ **스케줄 동작 확인**

```bash
# 현재 스케줄 상태 확인
./check_cron.sh

# 다음 실행 시간 확인
./check_cron.sh | grep "다음 실행"
```

## 🚨 문제 해결

### ❌ **크론이 실행되지 않는 경우**

```bash
# 크론 서비스 상태 확인
sudo systemctl status cron

# 크론 서비스 시작
sudo systemctl start cron

# 크론 서비스 자동 시작 설정
sudo systemctl enable cron
```

### ❌ **권한 문제**

```bash
# 프로젝트 디렉토리 권한 확인
ls -la /home/pi/market-automation

# 가상환경 실행 권한 확인
ls -la /home/pi/market-automation/.venv/bin/python

# 로그 디렉토리 권한 설정
sudo chown -R pi:pi /var/log/market
```

### ❌ **경로 문제**

```bash
# 절대 경로로 테스트
cd /home/pi/market-automation
source .venv/bin/activate
python market_automation/slots/run_0830_kr_preopen.py
```

### ❌ **환경 변수 문제**

```bash
# 환경 변수 로드 확인
source .env
echo $TZ
echo $DRY_RUN
```

## 📊 배포 완료 체크리스트

- [ ] **ver1.2 다운로드 완료**
- [ ] **가상환경 생성 및 패키지 설치 완료**
- [ ] **환경 변수 설정 완료**
- [ ] **시스템 시간대 KST 설정 완료**
- [ ] **크론 설정 자동 적용 완료**
- [ ] **개별 슬롯 테스트 실행 완료**
- [ ] **네이버 크롤링 테스트 완료**
- [ ] **크론 서비스 실행 및 자동 시작 설정 완료**
- [ ] **로그 모니터링 확인 완료**

## 🎯 **ver1.2 주요 개선사항**

### 🚀 **성능 향상**
- 주중 전용 스케줄링으로 불필요한 실행 방지
- 네이버 실시간 데이터로 한국 증시 정보 정확도 향상
- 템플릿 간소화로 포스팅 속도 개선

### 🔧 **유지보수성**
- 자동 크론 설정 스크립트로 배포 간소화
- 모듈화된 데이터 어댑터로 확장성 향상
- 상세한 로그 시스템으로 디버깅 용이

### 📈 **사용자 경험**
- 실시간 한국 증시 데이터로 정보 신뢰도 향상
- 주말 휴식으로 시스템 리소스 절약
- 명확한 스케줄 정보로 운영 투명성 향상

## 📞 **지원 및 문의**

배포 과정에서 문제가 발생하거나 추가 지원이 필요한 경우:

1. **로그 확인**: `/var/log/market/` 디렉토리의 로그 파일 확인
2. **크론 상태**: `./check_cron.sh` 실행으로 현재 상태 파악
3. **수동 테스트**: 개별 슬롯 수동 실행으로 문제점 파악
4. **권한 확인**: 파일 및 디렉토리 권한 설정 확인

---

**🎉 ver1.2 배포 완료 후 주중 전용 스케줄링으로 효율적인 Market Automation 시스템을 즐기세요!**
