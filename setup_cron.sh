#!/bin/bash

# Market Automation 크론 설정 스크립트
# 월요일 장 전(8:30)부터 토요일(07:00)까지만 실행

echo "🚀 Market Automation 크론 설정 시작"
echo "=================================="

# 현재 사용자 확인
CURRENT_USER=$(whoami)
echo "👤 현재 사용자: $CURRENT_USER"

# 프로젝트 디렉토리 확인
PROJECT_DIR="/home/$CURRENT_USER/market-automation"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 프로젝트 디렉토리를 찾을 수 없음: $PROJECT_DIR"
    echo "📁 올바른 경로를 입력하세요:"
    read -p "프로젝트 디렉토리 경로: " PROJECT_DIR
fi

echo "📁 프로젝트 디렉토리: $PROJECT_DIR"

# 가상환경 확인
VENV_PATH="$PROJECT_DIR/.venv/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
    echo "❌ 가상환경을 찾을 수 없음: $VENV_PATH"
    echo "🔧 가상환경을 먼저 생성해주세요"
    exit 1
fi

echo "✅ 가상환경 확인됨: $VENV_PATH"

# 로그 디렉토리 생성
LOG_DIR="/var/log/market"
echo "📝 로그 디렉토리 생성: $LOG_DIR"
sudo mkdir -p $LOG_DIR
sudo chown $CURRENT_USER:$CURRENT_USER $LOG_DIR

# 기존 크론 제거
echo "🗑️ 기존 크론 설정 제거 중..."
crontab -r 2>/dev/null || true

# 새로운 크론 설정 생성
echo "📅 새로운 크론 설정 생성 중..."

# 크론 설정 내용
CRON_CONTENT="# Market Automation 크론 설정
# 월요일(1) 장 전(8:30)부터 토요일(6) 07:00까지만 실행
# 토요일 8:30부터 월요일 7:00까지는 실행하지 않음

# 07:00 - 미국 증시 마감 리뷰 (월~토)
0 7 * * 1-6 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_0700_us_close >> $LOG_DIR/market_0700.log 2>&1

# 08:30 - 한국 개장 전 전망 (월~금)
30 8 * * 1-5 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_0830_kr_preopen >> $LOG_DIR/market_0830.log 2>&1

# 12:00 - 한국 장중 현황 (월~금)
0 12 * * 1-5 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_1200_kr_midday >> $LOG_DIR/market_1200.log 2>&1

# 16:00 - 한국 장 마감 요약 (월~금)
0 16 * * 1-5 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_1600_kr_close >> $LOG_DIR/market_1600.log 2>&1

# 20:00 - 미국 증시 개장 전 (월~금)
0 20 * * 1-5 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_2000_us_preview >> $LOG_DIR/market_2000.log 2>&1

# 23:00 - 미국 증시 장전 (월~금)
0 23 * * 1-5 cd $PROJECT_DIR && . $VENV_PATH && python -m market_automation.slots.run_2300_us_premkt >> $LOG_DIR/market_2300.log 2>&1"

# 크론 설정 적용
echo "$CRON_CONTENT" | crontab -

# 크론 설정 확인
echo "✅ 크론 설정 완료!"
echo ""
echo "📋 현재 크론 설정:"
crontab -l

echo ""
echo "📊 실행 스케줄 요약:"
echo "🟢 활성화 기간: 월요일 8:30 ~ 토요일 07:00"
echo "🔴 비활성화 기간: 토요일 8:30 ~ 월요일 7:00"
echo ""
echo "📝 로그 파일 위치: $LOG_DIR/"
echo "🔍 크론 상태 확인: sudo systemctl status cron"
echo "📊 로그 모니터링: tail -f $LOG_DIR/market_*.log"
echo ""
echo "🎯 설정이 완료되었습니다!"
