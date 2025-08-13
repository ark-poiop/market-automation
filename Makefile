.PHONY: help install test lint clean docker-build docker-run docker-stop

help: ## 도움말 보기
	@echo "사용 가능한 명령어:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 의존성 설치
	pip install -r requirements.txt

test: ## 테스트 실행
	python -m pytest

lint: ## 코드 린팅
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

clean: ## 캐시 파일 정리
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

docker-build: ## Docker 이미지 빌드
	docker build -t market-automation .

docker-run: ## Docker 컨테이너 실행
	docker-compose up -d

docker-stop: ## Docker 컨테이너 중지
	docker-compose down

preview-us-close: ## 미국 증시 마감 프리뷰
	python -m market_automation.cli_preview us_close samples/sample_us_close.json

preview-kr-preopen: ## 한국 개장 전 프리뷰
	python -m market_automation.cli_preview kr_preopen samples/sample_kr_preopen.json

run-0700: ## 07:00 미국 증시 마감 슬롯 실행
	python -m market_automation.slots.run_0700_us_close

run-0830: ## 08:30 한국 개장 전 슬롯 실행
	python -m market_automation.slots.run_0830_kr_preopen

run-1200: ## 12:00 한국 중간 점검 슬롯 실행
	python -m market_automation.slots.run_1200_kr_midday

run-1600: ## 16:00 한국 마감 슬롯 실행
	python -m market_automation.slots.run_1600_kr_close

run-2000: ## 20:00 미국 개장 전 슬롯 실행
	python -m market_automation.slots.run_2000_us_preview

run-2300: ## 23:00 미국 프리마켓 슬롯 실행
	python -m market_automation.slots.run_2300_us_premkt
