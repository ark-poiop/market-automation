"""
Threads 포스팅용 템플릿
본문 + 댓글 구조로 분리
"""

# 미국 관련 슬롯 - "미장투자" 주제
US_CLOSE_MAIN = """🇺🇸 미국 증시 마감 리뷰 ({date})

📊 지수 현황
S&P 500 — {spx} ({spx_pct}%)
Nasdaq — {ndx} ({ndx_pct}%)
Dow Jones — {djia} ({djia_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 주요 이슈
{main_news}"""

US_CLOSE_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 한국 개장 전 - "시황정리" 주제
KR_PREOPEN_MAIN = """🇰🇷 개장 전 전망 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 주요 이슈
{main_news}"""

KR_PREOPEN_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 한국 장중 - "시황정리" 주제
KR_MIDDAY_MAIN = """🇰🇷 장중 현황 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 주요 이슈
{main_news}"""

KR_MIDDAY_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 한국 장 마감 - "시황정리" 주제
KR_CLOSE_MAIN = """🇰🇷 장 마감 요약 ({date})

📊 지수 현황
KOSPI — {kospi} ({kospi_pct}%)
KOSDAQ — {kosdaq} ({kosdaq_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 주요 이슈
{main_news}"""

KR_CLOSE_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 미국 개장 전 - "미장투자" 주제
US_PREVIEW_MAIN = """🇺🇸 미국 증시 개장 전 ({date})

📊 지수 현황
S&P 500 — {spx_pct}%
Nasdaq — {ndx_pct}%
Dow Jones — {djia_pct}%

📉 선물
ES — {es}, NQ — {nq}, YM — {ym}

💱 원자재
WTI — ${wti}, Gold — ${gold}, 10Y — {ust10y}bp

🗓️ 일정
{today_events}

📈 포커스
{focus_sectors}

⚠️ 리스크
{risks}"""

US_PREVIEW_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 미국 장전 - "미장투자" 주제
US_PREMKT_MAIN = """🇺🇸 미국 증시 장전 ({date})

📊 지수 현황
S&P 500 — {spx} ({spx_pct}%)
Nasdaq — {ndx} ({ndx_pct}%)
Dow Jones — {djia} ({djia_pct}%)

🏭 섹터 (Top 3)
{sector_top3}

📰 주요 이슈
{main_news}"""

US_PREMKT_REPLY = """💬 급등 종목: {top_gainers}
💬 급락 종목: {top_losers}

📰 추가 뉴스
{additional_news}"""

# 기존 템플릿 (하위 호환성 유지)
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
