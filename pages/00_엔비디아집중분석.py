import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 페이지 기본 설정 (페이지 이름과 아이콘)
st.set_page_config(page_title="엔비디아 집중 분석", page_icon="🟢", layout="wide")

st.title("🟢 엔비디아(NVDA) 집중 분석")
st.markdown("글로벌 AI 반도체 선두주자인 엔비디아의 최근 주가 흐름과 **이동평균선**, **거래량**을 분석합니다.")

# 1. 사이드바 설정 (분석 기간 선택)
st.sidebar.header("📅 분석 기간 설정")
start_date = st.sidebar.date_input("시작일", datetime.today() - timedelta(days=365))
end_date = st.sidebar.date_input("종료일", datetime.today())

# 2. 데이터 가져오기
ticker = "NVDA"

with st.spinner("엔비디아 데이터를 분석 중입니다..."):
    # yfinance로 데이터 다운로드
    df = yf.download(ticker, start=start_date, end=end_date)

    if not df.empty:
        # 데이터 전처리 (결측치 채우기)
        df = df.ffill()

        # 3. 주요 지표 계산 (최근 종가, 전일 대비 변동 등)
        # 데이터프레임의 마지막 행(최근)과 그 이전 행(어제)의 종가 가져오기
        latest_price = df['Close'].iloc[-1].item() # .item()으로 단일 숫자로 변환
        previous_price = df['Close'].iloc[-2].item()
        
        # 전일 대비 변동 금액 및 수익률 계산
        price_change = latest_price - previous_price
        pct_change = (price_change / previous_price) * 100

        # 화면 상단에 핵심 지표(Metric) 표시
        st.subheader("💡 현재 주가 요약")
        # 컬럼을 나누어 깔끔하게 배치
        col1, col2, col3 = st.columns(3)
        col1.metric(label="최근 종가 (USD)", value=f"${latest_price:.2f}", delta=f"{price_change:.2f} ({pct_change:.2f}%)")
        col2.metric(label="기간 내 최고가", value=f"${df['High'].max().item():.2f}")
        col3.metric(label="기간 내 최저가", value=f"${df['Low'].min().item():.2f}")

        st.markdown("---")

        # 4. 이동평균선(Moving Average) 계산
        # rolling(window=n).mean()을 사용해 n일 동안의 평균을 계산합니다.
        df['20일 이동평균'] = df['Close'].rolling(window=20).mean()
        df['60일 이동평균'] = df['Close'].rolling(window=60).mean()

        # 시각화를 위해 종가와 이동평균선만 추출
        chart_data = df[['Close', '20일 이동평균', '60일 이동평균']]
        # 범례 이름을 보기 쉽게 변경
        chart_data.columns = ['종가', '20일 이동평균 (단기)', '60일 이동평균 (중기)']

        # 5. 주가 및 이동평균선 차트 출력
        st.subheader("📈 주가 및 이동평균선 차트")
        st.markdown("주가 흐름(종가)과 20일/60일 평균 가격의 흐름을 비교해 보세요.")
        st.line_chart(chart_data)

        # 6. 거래량(Volume) 분석 막대 차트
        st.subheader("📊 일별 거래량(Volume)")
        st.markdown("해당 일자에 주식이 얼마나 활발하게 거래되었는지 나타냅니다.")
        st.bar_chart(df['Volume'])

        # 7. 원본 데이터 확인
        with st.expander("엔비디아 상세 데이터 보기"):
            st.dataframe(df.sort_index(ascending=False)) # 최신 날짜가 위로 오도록 정렬하여 출력

    else:
        st.error("데이터를 불러오지 못했습니다. 날짜 설정을 확인해 주세요.")
