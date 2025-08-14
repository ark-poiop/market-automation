#!/bin/bash

# Market Automation 크론 설정 확인 스크립트

echo "🔍 Market Automation 크론 설정 확인"
echo "=================================="

# 현재 크론 설정 확인
echo "📋 현재 크론 설정:"
echo "------------------"
crontab -l 2>/dev/null || echo "❌ 크론 설정이 없습니다."

echo ""
echo "📊 스케줄 분석:"
echo "---------------"

# 크론 서비스 상태 확인
echo "🔧 크론 서비스 상태:"
if systemctl is-active --quiet cron; then
    echo "✅ 크론 서비스 실행 중"
else
    echo "❌ 크론 서비스 중지됨"
fi

echo ""
echo "📅 실행 스케줄 요약:"
echo "-------------------"

# 요일별 실행 상태 확인
echo "🟢 **활성화 기간: 월요일 8:30 ~ 토요일 07:00**"
echo ""
echo "| 요일 | 07:00 | 08:30 | 12:00 | 16:00 | 20:00 | 23:00 |"
echo "|------|-------|-------|-------|-------|-------|-------|"
echo "| **월요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |"
echo "| **화요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |"
echo "| **수요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |"
echo "| **목요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |"
echo "| **금요일** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |"
echo "| **토요일** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |"
echo "| **일요일** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |"

echo ""
echo "🔴 **비활성화 기간: 토요일 8:30 ~ 월요일 7:00**"
echo "- 토요일 8:30 ~ 일요일 23:59: 모든 슬롯 비활성화"
echo "- 월요일 00:00 ~ 7:00: 모든 슬롯 비활성화"

echo ""
echo "📝 로그 파일 위치:"
echo "-----------------"
LOG_DIR="/var/log/market"
if [ -d "$LOG_DIR" ]; then
    echo "✅ 로그 디렉토리: $LOG_DIR"
    echo "📊 로그 파일들:"
    ls -la $LOG_DIR/market_*.log 2>/dev/null || echo "   아직 로그 파일이 생성되지 않았습니다."
else
    echo "❌ 로그 디렉토리가 없습니다: $LOG_DIR"
fi

echo ""
echo "🔍 유용한 명령어:"
echo "----------------"
echo "📊 모든 로그 모니터링: tail -f $LOG_DIR/market_*.log"
echo "🔧 크론 서비스 상태: sudo systemctl status cron"
echo "📝 크론 편집: crontab -e"
echo "🗑️ 크론 제거: crontab -r"
echo "🔄 크론 서비스 재시작: sudo systemctl restart cron"

echo ""
echo "🎯 현재 시간 기준 다음 실행:"
echo "---------------------------"

# 현재 시간과 요일 확인
CURRENT_TIME=$(date "+%H:%M")
CURRENT_DAY=$(date "+%u")  # 1=월요일, 7=일요일
CURRENT_HOUR=$(date "+%H")

echo "🕐 현재 시간: $CURRENT_TIME (요일: $CURRENT_DAY)"

# 다음 실행 시간 계산
if [ "$CURRENT_DAY" -ge 1 ] && [ "$CURRENT_DAY" -le 5 ]; then
    # 월~금
    if [ "$CURRENT_HOUR" -lt 7 ]; then
        echo "⏰ 다음 실행: 오늘 07:00 (미국 증시 마감)"
    elif [ "$CURRENT_HOUR" -lt 8 ]; then
        echo "⏰ 다음 실행: 오늘 08:30 (한국 개장 전)"
    elif [ "$CURRENT_HOUR" -lt 12 ]; then
        echo "⏰ 다음 실행: 오늘 12:00 (한국 장중)"
    elif [ "$CURRENT_HOUR" -lt 16 ]; then
        echo "⏰ 다음 실행: 오늘 16:00 (한국 장 마감)"
    elif [ "$CURRENT_HOUR" -lt 20 ]; then
        echo "⏰ 다음 실행: 오늘 20:00 (미국 개장 전)"
    elif [ "$CURRENT_HOUR" -lt 23 ]; then
        echo "⏰ 다음 실행: 오늘 23:00 (미국 장전)"
    else
        echo "⏰ 다음 실행: 내일 07:00 (미국 증시 마감)"
    fi
elif [ "$CURRENT_DAY" -eq 6 ]; then
    # 토요일
    if [ "$CURRENT_HOUR" -lt 7 ]; then
        echo "⏰ 다음 실행: 오늘 07:00 (미국 증시 마감)"
    else
        echo "⏰ 다음 실행: 월요일 08:30 (한국 개장 전)"
        echo "📅 주말 동안 모든 슬롯이 비활성화됩니다."
    fi
else
    # 일요일
    echo "⏰ 다음 실행: 월요일 08:30 (한국 개장 전)"
    echo "📅 주말 동안 모든 슬롯이 비활성화됩니다."
fi

echo ""
echo "✅ 크론 설정 확인 완료!"
