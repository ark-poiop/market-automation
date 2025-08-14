# ⏰ 라즈베리파이 크론 설정 가이드

라즈베리파이에서 Market Automation 시스템을 **월요일 장 전(8:30)부터 토요일(07:00)까지만** 실행하기 위한 크론 설정입니다.

## 🔧 기본 설정

### 1. 시스템 시간대 설정 (KST)

```bash
# 현재 시간대 확인
timedatectl status

# KST로 설정
sudo timedatectl set-timezone Asia/Seoul

# 확인
date
```

### 2. 가상환경 경로 확인

```bash
# 프로젝트 디렉토리로 이동
cd /home/pi/market-automation

# 가상환경 경로 확인
ls -la .venv/bin/activate
```

## 📅 크론 등록 (주중만 실행)

### 1. 크론 편집

```bash
# 크론 편집
crontab -e

# 또는
sudo crontab -e
```

### 2. 다음 내용 추가

```bash
# Market Automation 크론 설정
# 월요일(1) 장 전(8:30)부터 토요일(6) 07:00까지만 실행
# 토요일 8:30부터 월요일 7:00까지는 실행하지 않음

# 07:00 - 미국 증시 마감 리뷰 (월~토)
0 7 * * 1-6 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_0700_us_close >> /var/log/market_0700.log 2>&1

# 08:30 - 한국 개장 전 전망 (월~금)
30 8 * * 1-5 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_0830_kr_preopen >> /var/log/market_0830.log 2>&1

# 12:00 - 한국 장중 현황 (월~금)
0 12 * * 1-5 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_1200_kr_midday >> /var/log/market_1200.log 2>&1

# 16:00 - 한국 장 마감 요약 (월~금)
0 16 * * 1-5 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_1600_kr_close >> /var/log/market_1600.log 2>&1

# 20:00 - 미국 증시 개장 전 (월~금)
0 20 * * 1-5 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_2000_us_preview >> /var/log/market_2000.log 2>&1

# 23:00 - 미국 증시 장전 (월~금)
0 23 * * 1-5 cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_2300_us_premkt >> /var/log/market_2300.log 2>&1
```

### 3. 크론 저장 및 확인

```bash
# 크론 목록 확인
crontab -l

# 크론 서비스 상태 확인
sudo systemctl status cron
```

## 📊 실행 스케줄 요약

### 🟢 **활성화 기간: 월요일 8:30 ~ 토요일 07:00**

| 요일 | 07:00 | 08:30 | 12:00 | 16:00 | 20:00 | 23:00 |
|------|-------|-------|-------|-------|-------|-------|
| **월요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **화요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **수요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **목요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **금요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **토요일** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **일요일** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 🔴 **비활성화 기간: 토요일 8:30 ~ 월요일 7:00**

- **토요일 8:30 ~ 일요일 23:59**: 모든 슬롯 비활성화
- **월요일 00:00 ~ 7:00**: 모든 슬롯 비활성화

## 📝 로그 설정

### 1. 로그 디렉토리 생성

```bash
# 로그 디렉토리 생성
sudo mkdir -p /var/log/market

# 권한 설정
sudo chown pi:pi /var/log/market
```

### 2. 로그 로테이션 설정

```bash
# 로그 로테이션 설정 파일 생성
sudo nano /etc/logrotate.d/market-automation
```

다음 내용 추가:

```
/var/log/market_*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
```

## 🔍 크론 실행 확인

### 1. 실시간 로그 모니터링

```bash
# 모든 슬롯 로그 동시 모니터링
tail -f /var/log/market_*.log

# 개별 슬롯 로그 모니터링
tail -f /var/log/market_0700.log
tail -f /var/log/market_0830.log
tail -f /var/log/market_1200.log
tail -f /var/log/market_1600.log
tail -f /var/log/market_2000.log
tail -f /var/log/market_2300.log
```

### 2. 크론 실행 로그 확인

```bash
# 시스템 크론 로그 확인
sudo tail -f /var/log/syslog | grep CRON

# 또는
sudo journalctl -f | grep CRON
```

## 🚨 문제 해결

### 1. 크론이 실행되지 않는 경우

```bash
# 크론 서비스 상태 확인
sudo systemctl status cron

# 크론 서비스 시작
sudo systemctl start cron

# 크론 서비스 자동 시작 설정
sudo systemctl enable cron
```

### 2. 권한 문제

```bash
# 프로젝트 디렉토리 권한 확인
ls -la /home/pi/market-automation

# 가상환경 실행 권한 확인
ls -la /home/pi/market-automation/.venv/bin/python
```

### 3. 경로 문제

```bash
# 절대 경로로 테스트
cd /home/pi/market-automation
. .venv/bin/activate
python -m market_automation.slots.run_0700_us_close
```

## 📊 크론 테스트

### 1. 수동 실행 테스트

```bash
# 개별 슬롯 수동 실행
cd /home/pi/market-automation
source .venv/bin/activate

# 07:00 슬롯 테스트
python -m market_automation.slots.run_0700_us_close

# 08:30 슬롯 테스트
python -m market_automation.slots.run_0830_kr_preopen
```

### 2. 크론 실행 테스트

```bash
# 1분 후 실행되도록 테스트 크론 등록
echo "* * * * * cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_0700_us_close >> /var/log/market_test.log 2>&1" | crontab -

# 1분 후 로그 확인
tail -f /var/log/market_test.log

# 테스트 크론 제거
crontab -r
```

## 🔄 크론 관리 명령어

```bash
# 크론 목록 보기
crontab -l

# 크론 편집
crontab -e

# 크론 모두 삭제
crontab -r

# 크론 서비스 재시작
sudo systemctl restart cron
```

## ⚠️ 주의사항

1. **시간대**: 반드시 KST(Asia/Seoul)로 설정
2. **경로**: 절대 경로 사용 권장
3. **권한**: 가상환경과 프로젝트 디렉토리 접근 권한 확인
4. **로그**: 각 슬롯별 로그 파일 생성 확인
5. **테스트**: 실제 크론 등록 전 수동 실행 테스트 필수
6. **주말 비활성화**: 토요일 8:30부터 월요일 7:00까지는 모든 슬롯이 실행되지 않음

## 🎯 스케줄 변경 이유

- **주말 휴식**: 토요일 오후부터 일요일까지는 시장이 닫혀있어 불필요한 실행 방지
- **리소스 절약**: 주말 동안 불필요한 시스템 리소스 사용 방지
- **유지보수 시간**: 주말 동안 시스템 점검 및 업데이트 가능
- **실용성**: 실제 거래 시간과 일치하는 스케줄링
