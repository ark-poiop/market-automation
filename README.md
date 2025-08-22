# 🚀 Market Automation - Threads 자동 포스팅 시스템

라즈베리파이에서 **월요일 장 전(8:30)부터 토요일(07:00)까지만** 실행되는 자동 증시 분석 및 Threads 포스팅 시스템입니다.

## 🎯 주요 기능

- **6개 슬롯 자동 포스팅**: KST 기준 07:00, 08:30, 12:00, 16:00, 20:00, 23:00 (주중만)
- **실시간 한국/미국 증시 데이터**: 네이버 금융 크롤링을 통한 실시간 지수 데이터 수집
- **자동 콘텐츠 생성**: 섹터 분석, 특징주 선별, 숫자 기반 요약
- **Threads 연동**: 자동 포스팅 (DRY RUN 모드 지원)
- **스마트 폴백 시스템**: 크롤링 실패 시 샘플 데이터로 자동 전환

## 🏗️ 현재 구현 상태 (ver2.0)

### ✅ **완성된 기능**
- **07:00 미국 증시 마감**: 네이버 크롤링 데이터 완벽 연동 ✅
- **08:30 한국 개장 전**: 네이버 크롤링 데이터 완벽 연동 ✅
- **12:00 한국 장중**: 네이버 크롤링 데이터 완벽 연동 ✅
- **16:00 한국 장 마감**: 네이버 크롤링 데이터 완벽 연동 ✅
- **20:00 미국 개장 전**: 네이버 크롤링 데이터 완벽 연동 ✅
- **23:00 미국 장전**: 네이버 크롤링 데이터 완벽 연동 ✅

### 🔄 **데이터 소스 현황**
- **한국 증시**: ✅ 네이버 금융 크롤링 (KOSPI, KOSDAQ)
- **미국 증시**: ✅ 네이버 금융 크롤링 (S&P500, 나스닥, 다우)
- **섹터 데이터**: ✅ 네이버 금융 크롤링 (업종별 성과)
- **테마 데이터**: ✅ 네이버 테마 어댑터 (실시간 테마 등락률)
- **특징주 데이터**: ❌ 크롤링 실패 (JavaScript 렌더링 문제)
- **폴백 시스템**: ✅ 샘플 데이터 자동 전환

### 🆕 **ver2.0 신규 기능**
- **네이버 테마 데이터 통합**: 한국 12시, 16시 슬롯에 실시간 테마 정보 추가
- **섹터명 정리**: "원자력발전소 해체" → "원자력 에너지" 형태로 깔끔하게 표시
- **등락률 표시**: 각 테마별 등락률을 줄바꿈 형태로 가독성 향상
- **보안 강화**: 민감한 정보 제외 및 .gitignore 최적화

## 📁 프로젝트 구조

```
market-automation/
├── .env                    # 환경 변수 설정
├── requirements.txt        # Python 패키지 의존성
├── naver_finance_scraper.py  # 네이버 금융 크롤러 ✅
├── naver_market_data.json    # 크롤링된 데이터 저장소 ✅
├── assets/
│   └── sectors.yml        # 섹터 설정 (한글명, 이모지, 규칙)
├── samples/               # 샘플 데이터
│   ├── sample_us_close.json
│   └── sample_kr_preopen.json
├── market_automation/      # 메인 패키지
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── datasource/        # 데이터 소스
│   │   ├── naver_adapter.py  # 네이버 데이터 변환 어댑터 ✅
│   │   ├── naver_theme_adapter.py  # 네이버 테마 데이터 수집 ✅
│   │   ├── news_api.py    # 뉴스 API 클라이언트 ✅
│   │   ├── finnhub_client.py  # Finnhub API 클라이언트 ✅
│   │   └── alpaca.py      # Alpaca Markets API (사용 안함)
│   ├── rendering/         # 콘텐츠 렌더링
│   │   ├── templates.py   # Threads 템플릿 ✅
│   │   ├── prompts.py     # LLM 프롬프트 ✅
│   │   └── compose.py     # 콘텐츠 합성 ✅
│   ├── posting/           # 포스팅 실행
│   │   ├── threads_client.py  # Threads API 클라이언트 ✅
│   │   └── poster.py      # 포스팅 로직 ✅
│   ├── slots/             # 각 슬롯별 실행 스크립트
│   │   ├── run_0700_us_close.py    # ✅ 네이버 데이터 연동
│   │   ├── run_0830_kr_preopen.py  # ✅ 네이버 데이터 연동
│   │   ├── run_1200_kr_midday.py   # ✅ 네이버 데이터 연동
│   │   ├── run_1600_kr_close.py    # ✅ 네이버 데이터 연동
│   │   ├── run_2000_us_preview.py  # ✅ 네이버 데이터 연동
│   │   └── run_2300_us_premkt.py   # ✅ 네이버 데이터 연동
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

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
cd /home/pi
git clone https://github.com/ark-poiop/market-automation.git
cd market-automation

# 가상환경 생성
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp env.example .env
nano .env

# 필수 설정
THREADS_ACCESS_TOKEN=your_token_here
THREADS_USER_ID=your_user_id_here
OPENAI_API_KEY=your_openai_key_here
DRY_RUN=1  # 테스트 후 0으로 변경
```

### 3. 테스트 실행

```bash
# 네이버 크롤링 테스트
python naver_finance_scraper.py

# 한국 슬롯 테스트
python market_automation/slots/run_1200_kr_midday.py

# 미국 슬롯 테스트
python market_automation/slots/run_0700_us_close.py
```

## 🔧 Cron 설정

```bash
# 크론 설정 스크립트 실행
chmod +x setup_cron.sh
./setup_cron.sh

# 크론 상태 확인
chmod +x check_cron.sh
./check_cron.sh
```

## 📊 데이터 수집 현황

### ✅ **성공적으로 수집되는 데이터**
- **한국 지수**: KOSPI, KOSDAQ 실시간 가격 및 등락률
- **미국 지수**: S&P500, 나스닥, 다우 정확한 포인트 및 등락률
- **섹터 데이터**: 업종별 성과 (상위/하위 업종)

### ❌ **수집 실패하는 데이터**
- **특징주 데이터**: JavaScript 렌더링 문제로 크롤링 실패

## 🚧 앞으로 해야 할 일 (TODO)

### 🔴 **높은 우선순위**
1. **특징주 데이터 수집 개선**
   - Selenium을 사용한 JavaScript 렌더링 대기
   - 또는 다른 데이터 소스 (한국투자증권 API) 활용
   - 목표: 거래량 급증, 급등/급락 종목 정보 수집

2. **크롤링 자동화**
   - 각 슬롯 실행 전 자동 크롤링 통합
   - 현재: 수동 크롤링 → 슬롯 실행
   - 개선: 슬롯 실행 시 자동 크롤링

### 🟡 **중간 우선순위**
3. **데이터 품질 향상**
   - 섹터 데이터의 더 상세한 정보 (거래량, 시가총액 등)
   - 업종별 상세 분석 및 트렌드 파악

4. **에러 처리 강화**
   - 크롤링 실패 시 자동 재시도 로직
   - 네트워크 오류 시 폴백 시스템 개선

### 🟢 **낮은 우선순위**
5. **추가 데이터 소스**
   - 뉴스 데이터 크롤링 (경제 뉴스, 이벤트)
   - 원자재 가격 정보 (WTI, 금 등)

6. **성능 최적화**
   - 크롤링 속도 개선
   - 메모리 사용량 최적화

## 📈 버전 히스토리

### **v1.3 (현재)**
- ✅ 네이버 크롤링으로 한국/미국 지수 데이터 수집
- ✅ 섹터 데이터 수집 및 변환
- ✅ 모든 슬롯에서 네이버 데이터 활용
- ✅ Alpaca API 완전 제거

### **v1.2.1**
- ✅ 한국 슬롯들을 네이버 크롤링 데이터로 전환
- ✅ 환율 및 거래량 데이터 제거
- ✅ 스케줄링 개선 (월-토만 실행)

### **v1.2**
- ✅ 기본 시스템 구축
- ✅ 6개 슬롯 구현
- ✅ Threads 연동

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.
