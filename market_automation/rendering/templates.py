"""
Threads 포스팅용 템플릿 (수정 버전)
톤·이모지 절제 + 요청 반영
"""

US_CLOSE = """🇺🇸 미국 증시 마감 리뷰 ({date} 기준)

📊 종합 지수 현황
S&P 500 — {spx} ({spx_diff}, {spx_pct}%) 🔥 {spx_comment}
Nasdaq — {ndx} ({ndx_diff}, {ndx_pct}%) 🚀 {ndx_comment}
Dow Jones — {djia} ({djia_diff}, {djia_pct}%) 💼 {djia_comment}
"""

KR_PREOPEN = """🇰🇷 개장 전 전망 ({date})
🌏 전일 미증시 — S&P500 {spx_pct}%, Nasdaq {ndx_pct}%, Dow {djia_pct}%
"""

KR_MIDDAY = """🇰🇷 장중 현황 ({date}, {time})
📊 KOSPI {kospi} ({kospi_diff}, {kospi_pct}%)
📈 KOSDAQ {kosdaq} ({kosdaq_diff}, {kosdaq_pct}%)
"""

KR_CLOSE = """🇰🇷 장 마감 요약 ({date})
📊 KOSPI {kospi} ({kospi_diff}, {kospi_pct}%)
📈 KOSDAQ {kosdaq} ({kosdaq_diff}, {kosdaq_pct}%)
"""

US_PREVIEW = """🇺🇸 미국 증시 개장 전 ({date})

📊 전일 마감 종합 지수 현황
S&P 500 — {spx} ({spx_diff}, {spx_pct}%) 🔥 {spx_comment}
Nasdaq — {ndx} ({ndx_diff}, {ndx_pct}%) 🚀 {ndx_comment}
Dow Jones — {djia} ({djia_diff}, {djia_pct}%) 💼 {djia_comment}
"""
