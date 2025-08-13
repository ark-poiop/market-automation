# 🚀 Market Automation - Threads 자동 포스팅 시스템

라즈베리파이에서 24/7로 실행되는 자동 증시 분석 및 Threads 포스팅 시스템입니다.

## 🎯 주요 기능

- **6개 슬롯 자동 포스팅**: KST 기준 07:00, 08:30, 12:00, 16:00, 20:00, 23:00
- **다양한 데이터 소스**: 한국투자증권, FRED, EIA, Polygon/Finnhub/FMP 등
- **자동 콘텐츠 생성**: 섹터 분석, 특징주 선별, 숫자 기반 요약
- **Threads 연동**: @tday.insight 계정으로 자동 포스팅
- **하드코딩 금지**: 섹터/이모지/규칙은 YAML에서 관리

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
│   ├── datasource/        # 데이터 소스 (구현 예정)
│   ├── processing/        # 데이터 처리 (구현 예정)
│   ├── rendering/         # 콘텐츠 렌더링
│   │   ├── templates.py   # Threads 템플릿
│   │   ├── prompts.py     # LLM 프롬프트
│   │   └── compose.py     # 콘텐츠 합성
│   ├── posting/           # 포스팅 실행
│   │   ├── threads_client.py
│   │   └── poster.py
│   ├── slots/             # 각 슬롯별 실행 스크립트
│   │   ├── run_0700_us_close.py
│   │   ├── run_0830_kr_preopen.py
│   │   ├── run_1200_kr_midday.py
│   │   ├── run_1600_kr_close.py
│   │   ├── run_2000_us_preview.py
│   │   └── run_2300_us_premkt.py
│   └── cli_preview.py     # CLI 프리뷰 도구
└── README.md
```

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
```

### 3. 프리뷰 테스트

```bash
# 미국 증시 마감 포스트 프리뷰
python -m market_automation.cli_preview us_close samples/sample_us_close.json

# 한국 개장 전 포스트 프리뷰
python -m market_automation.cli_preview kr_preopen samples/sample_kr_preopen.json
```

### 4. 개별 슬롯 테스트

```bash
# 07:00 미국 증시 마감 슬롯 테스트
python -m market_automation.slots.run_0700_us_close

# 08:30 한국 개장 전 슬롯 테스트
python -m market_automation.slots.run_0830_kr_preopen
```

## ⏰ 크론 등록 (라즈베리파이)

```bash
# 크론 편집
crontab -e

# 다음 내용 추가 (KST 기준)
0 7  * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_0700_us_close >> /var/log/market_0700.log 2>&1
30 8 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_0830_kr_preopen >> /var/log/market_0830.log 2>&1
0 12 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_1200_kr_midday >> /var/log/market_1200.log 2>&1
0 16 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_1600_kr_close >> /var/log/market_1600.log 2>&1
0 20 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_2000_us_preview >> /var/log/market_2000.log 2>&1
0 23 * * *  cd /home/pi/market-automation && . .venv/bin/activate && python -m market_automation.slots.run_2300_us_premkt >> /var/log/market_2300.log 2>&1
```

## 🔧 운영 규칙

### DRY RUN 모드
- **DRY_RUN=1**: 실제 포스팅 없이 콘텐츠만 프리뷰
- **DRY_RUN=0**: 실제 Threads에 포스팅

### 섹터 설정 관리
- `assets/sectors.yml`에서 섹터명, 이모지, 규칙 관리
- 코드 하드코딩 금지

### LLM 요약
- 숫자 기반 요약만 수행
- 입력 외 정보 금지
- 과장 표현 금지

## 📊 샘플 출력 예시

### 미국 증시 마감
```
🇺🇸 미국 증시 마감 리뷰 (2025-08-13 기준)

📊 종합 지수 현황
S&P 500 — 6,445.8 (+72.3, +1.13%) 🔥 사상 최고치 경신
Nasdaq — 21,681.9 (+296.5, +1.39%) 🚀 대형 성장주 주도
Dow Jones — 44,458.6 (+483.5, +1.10%) 💼 금융·산업 우위
Russell 2000 — 2,282.8 (+66.3, +3.00%) 📈 소형주 급등

🟢 섹터 요약
기술💻·금융🏦·산업재🏭 강세, 유틸리티⚡·부동산🏢 약세

🚀 특징주
NVDA — AI 수요 (3.2%)
META — 광고 견조 (2.4%)
DAL — 연료비 둔화 (2.1%)
```

## 🚧 구현 예정 기능

- [ ] 한국투자증권 API 연동
- [ ] FRED/EIA API 연동
- [ ] Polygon/Finnhub/FMP API 연동
- [ ] 실제 Threads API 연동
- [ ] 데이터 정규화 및 지표 계산
- [ ] 섹터별 특징주 자동 선별
- [ ] 장애 시 보조 데이터 소스 활용

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
