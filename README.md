# 🚀 Market Automation - Threads 자동 포스팅 시스템

라즈베리파이에서 **월요일 장 전(8:30)부터 토요일(07:00)까지만** 실행되는 자동 증시 분석 및 Threads 포스팅 시스템입니다.

## 🎯 주요 기능

- **6개 슬롯 자동 포스팅**: KST 기준 07:00, 08:30, 12:00, 16:00, 20:00, 23:00 (주중만)
- **실시간 미국 증시 데이터**: Alpaca Markets API를 통한 실시간 지수/ETF 데이터 수집
- **한국 증시 데이터**: 한국투자증권 API 연동 (구현 예정)
- **자동 콘텐츠 생성**: 섹터 분석, 특징주 선별, 숫자 기반 요약
- **Threads 연동**: 자동 포스팅 (DRY RUN 모드 지원)
- **스마트 폴백 시스템**: API 실패 시 샘플 데이터로 자동 전환

## 🏗️ 현재 구현 상태

### ✅ **완성된 기능**
- **07:00 미국 증시 마감**: Alpaca API 연동 완료
- **08:30 한국 개장 전**: 기본 구조 완성
- **12:00 한국 장중**: 포스팅 로직 구현 완료
- **16:00 한국 장 마감**: 포스팅 로직 구현 완료
- **20:00 미국 개장 전**: 포스팅 로직 구현 완료
- **23:00 미국 장전**: 포스팅 로직 구현 완료

### 🔄 **데이터 소스 현황**
- **미국 증시**: ✅ Alpaca Markets API (실시간 ETF 데이터)
- **한국 증시**: 🚧 한국투자증권 API (구현 예정)
- **폴백 시스템**: ✅ 샘플 데이터 자동 전환

## 📁 프로젝트 구조

```
market-automation/
├── .env                    # 환경 변수 설정
├── requirements.txt        # Python 패키지 의존성
├── assets/
│   └── sectors.yml        # 섹터 설정 (한글명, 이모지, 규칙)
├── samples/               # 샘플 데이터
│   ├── sample_us_close.json
│   └── sample_kr_preopen.json
├── market_automation/      # 메인 패키지
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── datasource/        # 데이터 소스
│   │   ├── alpaca.py      # Alpaca Markets API 클라이언트 ✅
│   │   └── kis.py         # 한국투자증권 API 클라이언트 🚧
│   ├── rendering/         # 콘텐츠 렌더링
│   │   ├── templates.py   # Threads 템플릿 ✅
│   │   ├── prompts.py     # LLM 프롬프트 ✅
│   │   └── compose.py     # 콘텐츠 합성 ✅
│   ├── posting/           # 포스팅 실행
│   │   ├── threads_client.py  # Threads API 클라이언트 ✅
│   │   └── poster.py      # 포스팅 로직 ✅
│   ├── slots/             # 각 슬롯별 실행 스크립트
│   │   ├── run_0700_us_close.py    # ✅ Alpaca API 연동
│   │   ├── run_0830_kr_preopen.py  # ✅ 기본 구조
│   │   ├── run_1200_kr_midday.py   # ✅ 포스팅 로직
│   │   ├── run_1600_kr_close.py    # ✅ 포스팅 로직
│   │   ├── run_2000_us_preview.py  # ✅ 포스팅 로직
│   │   └── run_2300_us_premkt.py   # ✅ 포스팅 로직
│   └── cli_preview.py     # CLI 프리뷰 도구 ✅
└── README.md
```

## 📅 실행 스케줄

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

### 🎯 **스케줄 변경 이유**

- **주말 휴식**: 토요일 오후부터 일요일까지는 시장이 닫혀있어 불필요한 실행 방지
- **리소스 절약**: 주말 동안 불필요한 시스템 리소스 사용 방지
- **유지보수 시간**: 주말 동안 시스템 점검 및 업데이트 가능
- **실용성**: 실제 거래 시간과 일치하는 스케줄링

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
cd /home/pi
git clone <repository-url> market-automation
cd market-automation

# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp env.example .env
nano .env

# 필수 설정
TZ=Asia/Seoul
DRY_RUN=1  # 최초엔 1로 설정 (프리뷰 모드)

# Alpaca Markets API (미국 증시 데이터)
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_API_SECRET=your_alpaca_api_secret_here
ALPACA_PAPER=true  # true: Paper Trading, false: Live Trading

# Threads API
THREADS_ACCESS_TOKEN=your_threads_access_token_here
THREADS_USER_ID=your_threads_user_id_here

### 3. 크론 설정 (자동 실행)

```bash
# 크론 설정 자동 적용
./setup_cron.sh

# 크론 설정 확인
./check_cron.sh

# 수동으로 크론 편집
crontab -e
```
```

### 3. Alpaca API 키 발급

1. [Alpaca Markets](https://alpaca.markets/) 가입
2. Paper Trading 계정 생성 (무료)
3. API 키와 시크릿 발급
4. `.env` 파일에 입력

### 4. 프리뷰 테스트

```bash
# 미국 증시 마감 포스트 프리뷰 (Alpaca API 사용)
python market_automation/slots/run_0700_us_close.py

# 한국 개장 전 포스트 프리뷰
python market_automation/slots/run_0830_kr_preopen.py
```

### 5. 개별 슬롯 테스트

```bash
# 07:00 미국 증시 마감 슬롯 테스트 (실시간 데이터)
python market_automation/slots/run_0700_us_close.py

# 12:00 한국 장중 슬롯 테스트
python market_automation/slots/run_1200_kr_midday.py

# 20:00 미국 개장 전 슬롯 테스트
python market_automation/slots/run_2000_us_preview.py
```

## ⏰ 크론 등록 (라즈베리파이)

```bash
# 크론 편집
crontab -e

# 다음 내용 추가 (KST 기준)
0 7  * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_0700_us_close.py >> /var/log/market_0700.log 2>&1
30 8 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_0830_kr_preopen.py >> /var/log/market_0830.log 2>&1
0 12 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_1200_kr_midday.py >> /var/log/market_1200.log 2>&1
0 16 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_1600_kr_close.py >> /var/log/market_1600.log 2>&1
0 20 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_2000_us_preview.py >> /var/log/market_2000.log 2>&1
0 23 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python market_automation/slots/run_2300_us_premkt.py >> /var/log/market_2300.log 2>&1
```

## 🔧 운영 규칙

### DRY RUN 모드
- **DRY_RUN=1**: 실제 포스팅 없이 콘텐츠만 프리뷰
- **DRY_RUN=0**: 실제 Threads에 포스팅

### 데이터 수집 우선순위
1. **1차**: Alpaca API (실시간 미국 증시 데이터)
2. **2차**: 한국투자증권 API (한국 증시 데이터)
3. **3차**: 샘플 데이터 (API 실패 시 자동 전환)

### 섹터 설정 관리
- `assets/sectors.yml`에서 섹터명, 이모지, 규칙 관리
- 코드 하드코딩 금지

### LLM 요약
- 숫자 기반 요약만 수행
- 입력 외 정보 금지
- 과장 표현 금지

## 📊 실제 데이터 수집 현황

### 🇺🇸 **미국 증시 (Alpaca API)**
- **S&P 500**: SPY ETF 실시간 가격 ✅
- **Nasdaq**: QQQ ETF 실시간 가격 ✅
- **Dow Jones**: DIA ETF 실시간 가격 ✅
- **Russell 2000**: IWM ETF 실시간 가격 ✅
- **섹터 성과**: 11개 SPDR ETF 실시간 데이터 ✅
- **특징주**: AAPL, MSFT, GOOGL, AMZN, NVDA 실시간 데이터 ✅

### 🇰🇷 **한국 증시 (구현 예정)**
- **KOSPI**: 한국투자증권 API 연동 예정
- **KOSDAQ**: 한국투자증권 API 연동 예정
- **섹터 분석**: 한국 투자신탁운용사 API 연동 예정

## 📝 실제 출력 예시

### 미국 증시 마감 (Alpaca API 실시간 데이터)
```
🇺🇸 미국 증시 마감 리뷰 (2025-08-13 기준)

📊 종합 지수 현황
S&P 500 — 645.07 (0.00%, 0.00%) 🔥 소폭 변동
Nasdaq — 579.91 (0.00%, 0.00%) 🚀 소폭 변동
Dow Jones — 449.29 (0.00%, 0.00%) 💼 소폭 변동
Russell 2000 — 231.12 (0.00%, 0.00%) 📈 소폭 변동

🟢 섹터 요약
기술💻·금융🏦 약세

🚀 특징주
AAPL — 일반적 변동 (+0.0%)
MSFT — 일반적 변동 (+0.0%)
GOOGL — 일반적 변동 (+0.0%)
AMZN — 일반적 변동 (+0.0%)
NVDA — 일반적 변동 (+0.0%)
```

## 🚧 구현 예정 기능

- [x] Alpaca Markets API 연동 (미국 증시)
- [ ] 한국투자증권 API 연동 (한국 증시)
- [ ] FRED/EIA API 연동 (경제 지표)
- [ ] Polygon/Finnhub/FMP API 연동 (보조 데이터)
- [ ] 실제 Threads API 연동
- [ ] 데이터 정규화 및 지표 계산
- [ ] 섹터별 특징주 자동 선별
- [ ] 장애 시 보조 데이터 소스 활용

## 🔍 문제 해결

### Alpaca API 연결 문제
```bash
# API 키 확인
grep "ALPACA_API_KEY" .env

# Paper Trading 모드 확인
grep "ALPACA_PAPER" .env
```

### 변동률이 0%로 나오는 경우
- **Paper Trading 환경**: 실제 거래 데이터 제한
- **시장 시간**: 미국 시장 개장 시간 확인
- **Live Trading 전환**: `ALPACA_PAPER=false`로 설정

## 📝 로그 확인

```bash
# 각 슬롯별 로그 확인
tail -f /var/log/market_0700.log
tail -f /var/log/market_0830.log
tail -f /var/log/market_1200.log
tail -f /var/log/market_1600.log
tail -f /var/log/market_2000.log
tail -f /var/log/market_2300.log
```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
