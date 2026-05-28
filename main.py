import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 페이지 기본 설정
st.set_page_config(page_title="한/미 주식 비교 웹앱", page_icon="📈", layout="wide")

st.title("📈 당곡고 - 한/미 주요 주식 수익률 및 차트 비교")
st.markdown("파이썬 `yfinance` 라이브러리를 활용하여 한국과 미국의 주요 주식 수익률을 비교해 보는 웹앱입니다.")

# 1. 사이드바 설정 (사용자 입력 필드)
st.sidebar.header("📊 분석 설정")

# 한국과 미국의 주요 주식 종목 티커(Ticker) 딕셔너리
STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "현대자동차": "005380.KS",
    "카카오": "035720.KS",
    "Apple (애플)": "AAPL",
    "Tesla (테슬라)": "TSLA",
    "Microsoft (마이크로소프트)": "MSFT",
    "NVIDIA (엔비디아)": "NVDA"
}

# 멀티 셀렉트 박스 (여러 주식을 동시에 선택 가능하게 함)
selected_stocks = st.sidebar.multiselect(
    "비교할 주식을 선택하세요:",
    options=list(STOCKS.keys()),
    default=["삼성전자", "Apple (애플)"]
)

# 날짜 선택
start_date = st.sidebar.date_input("시작일", datetime.today() - timedelta(days=365)) # 기본값: 1년 전
end_date = st.sidebar.date_input("종료일", datetime.today()) # 기본값: 오늘

# 2. 메인 화면 데이터 처리 및 시각화
if selected_stocks:
    with st.spinner("주식 데이터를 불러오는 중입니다. 잠시만 기다려주세요..."):
        # 선택한 주식들의 종가 데이터를 저장할 빈 데이터프레임 생성
        df_close = pd.DataFrame()
        
        # 선택한 각 주식에 대해 yfinance로 데이터를 가져옴
        for stock_name in selected_stocks:
            ticker = STOCKS[stock_name]
            # yf.download()를 사용해 해당 기간의 데이터를 다운로드
            data = yf.download(ticker, start=start_date, end=end_date)
            
            # 주말/공휴일 등 거래가 없는 날의 빈 데이터를 제거하고 종가(Close)만 추출
            df_close[stock_name] = data['Close']

        # 데이터가 정상적으로 불러와졌는지 확인
        if not df_close.empty:
            # 결측치 처리 (이전 날짜의 가격으로 채움)
            df_close = df_close.ffill()

            # --- 수익률 계산 ---
            # 각 주식의 첫 날 종가를 기준으로 누적 수익률(%) 계산
            # 공식: (현재 가격 - 첫 날 가격) / 첫 날 가격 * 100
            cum_returns = ((df_close / df_close.iloc[0]) - 1) * 100

            # 1. 누적 수익률 차트 출력
            st.subheader("📊 기간 내 누적 수익률 차트 (%)")
            st.markdown("시작일을 0%로 기준으로 하여, 각 주식의 성장률을 비교합니다.")
            st.line_chart(cum_returns)

            # 2. 요약 테이블 출력
            st.subheader("📝 수익률 요약")
            summary_df = pd.DataFrame({
                "시작일 종가": df_close.iloc[0],
                "종료일 종가": df_close.iloc[-1],
                "누적 수익률(%)": cum_returns.iloc[-1].round(2)
            })
            st.dataframe(summary_df)

            # 3. 원본 종가 데이터 (토글로 숨김 처리)
            with st.expander("원본 종가 데이터 보기"):
                st.dataframe(df_close)
        else:
            st.warning("선택한 기간에 대한 데이터가 없습니다. 날짜를 다시 설정해주세요.")
else:
    st.info("👈 왼쪽 사이드바에서 비교할 주식 종목을 선택해주세요.")

st.sidebar.markdown("---")
st.sidebar.caption("개발자: 당곡고등학교 학생")
