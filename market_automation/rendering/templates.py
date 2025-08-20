"""
Threads 포스팅용 템플릿
지시사항에 따른 새로운 출력 포맷 적용
"""

US_CLOSE = """🇺🇸 미국 증시 마감 리뷰 ({date})

📊 지수 현황
S&P 500 — {spx} ({spx_pct}%)
Nasdaq — {ndx} ({ndx_pct}%)
Dow Jones — {djia} ({djia_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""

KR_PREOPEN = """🇰🇷 개장 전 전망 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""

KR_MIDDAY = """🇰🇷 장중 현황 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""

KR_CLOSE = """🇰🇷 장 마감 요약 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""

US_PREVIEW = """🇺🇸 미국 증시 개장 전 ({date})

📊 지수 현황
S&P 500 — {spx} ({spx_pct}%)
Nasdaq — {ndx} ({ndx_pct}%)
Dow Jones — {djia} ({djia_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""

US_PREMKT = """🇺🇸 미국 증시 장전 ({date})

📊 지수 현황
S&P 500 — {spx} ({spx_pct}%)
Nasdaq — {ndx} ({ndx_pct}%)
Dow Jones — {djia} ({djia_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 이슈
{news_events}

💬 댓글
급등 종목: {top_gainers}
급락 종목: {top_losers}"""
