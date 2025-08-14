"""
Threads 포스팅용 템플릿
톤·이모지 절제
"""

US_CLOSE = """🇺🇸 미국 증시 마감 리뷰 ({date} 기준)

📊 종합 지수 현황
S&P 500 — {spx} ({spx_diff}, {spx_pct}%) 🔥 {spx_comment}
Nasdaq — {ndx} ({ndx_diff}, {ndx_pct}%) 🚀 {ndx_comment}
Dow Jones — {djia} ({djia_diff}, {djia_pct}%) 💼 {djia_comment}
Russell 2000 — {rty} ({rty_diff}, {rty_pct}%) 📈 {rty_comment}

🟢 섹터 요약
{sector_line}

🚀 특징주
{movers_block}
"""

KR_PREOPEN = """🇰🇷 개장 전 전망 ({date})
🌏 전일 미증시 — S&P500 {spx_pct}%, Nasdaq {ndx_pct}%, Dow {djia_pct}%
📉 선물 — K200F {k200f}, S&P500F {es}, NasdaqF {nq}

🗓️ 일정 — {today_events}
📈 업종 포커스 — {focus_sectors}
⚠️ 리스크 — {risks}
"""

KR_MIDDAY = """🇰🇷 장중 현황 ({date})
📊 KOSPI {kospi} ({kospi_diff}, {kospi_pct}%)
📈 KOSDAQ {kosdaq} ({kosdaq_diff}, {kosdaq_pct}%)

🟢 상승 업종 — {top_sectors}
🔴 하락 업종 — {bottom_sectors}
🚀 특징주 — {movers}
"""

KR_CLOSE = """🇰🇷 장 마감 요약 ({date})
📊 KOSPI {kospi} ({kospi_diff}, {kospi_pct}%)
📈 KOSDAQ {kosdaq} ({kosdaq_diff}, {kosdaq_pct}%)

🟢 섹터 요약
{sector_line}

🚀 특징주
{movers_block}
"""

US_PREVIEW = """🇺🇸 미국 증시 개장 전 ({date})
🌏 전일 마감 — S&P500 {spx_pct}%, Nasdaq {ndx_pct}%, Dow {djia_pct}%
📉 선물 — ES {es}, NQ {nq}, YM {ym}
💱 원자재 — WTI ${wti}, Gold ${gold}, 10Y {ust10y}bp

🗓️ 일정 — {today_events}
📈 포커스 — {focus_sectors}
⚠️ 리스크 — {risks}
"""

US_PREMKT = """🇺🇸 미국 증시 장전 ({date})
🌏 전일 마감 — S&P500 {spx_pct}%, Nasdaq {ndx_pct}%, Dow {djia_pct}%
📉 선물 — ES {es}, NQ {nq}, YM {ym}
💱 원자재 — WTI ${wti}, Gold ${gold}, 10Y {ust10y}bp

🗓️ 일정 — {today_events}
📈 포커스 — {focus_sectors}
⚠️ 리스크 — {risks}
"""
