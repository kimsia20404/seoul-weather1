import streamlit as st
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.set_page_config(
    page_title="서울 100년 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

st.title("🌡️ 서울의 100년 기온 변화")
st.caption("서울 기상 관측 자료의 연평균 기온을 이용해 장기적인 변화를 살펴봅니다.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")
    df = df.dropna(subset=["날짜", "평균기온"]).copy()
    df["연도"] = df["날짜"].dt.year
    return df

try:
    df = load_data()
except Exception as e:
    st.error("기온 데이터를 불러오지 못했습니다.")
    st.exception(e)
    st.stop()

# 연평균 기온 계산
annual = (
    df.groupby("연도", as_index=False)["평균기온"]
      .mean()
      .rename(columns={"평균기온": "연평균기온"})
)

# 데이터의 마지막 연도가 완전한 연도가 아니라면 직전 연도를 마지막 연도로 사용
last_date = df["날짜"].max()
latest_year = last_date.year if (last_date.month == 12 and last_date.day == 31) else last_date.year - 1

# 최근 100개의 연도 구간
start_year = latest_year - 99
annual_100 = annual[
    (annual["연도"] >= start_year) & (annual["연도"] <= latest_year)
].copy()

annual_100["연평균기온"] = annual_100["연평균기온"].round(2)

# 5년 이동평균으로 장기 흐름을 함께 표시
annual_100["5년 이동평균"] = (
    annual_100["연평균기온"].rolling(window=5, min_periods=1).mean().round(2)
)

if annual_100.empty:
    st.warning("표시할 100년 구간의 데이터가 없습니다.")
    st.stop()

st.subheader(f"{start_year}년–{latest_year}년 연평균 기온")

# 두 선을 함께 보여 주어 연도별 변동과 장기 흐름을 한눈에 확인
chart_data = annual_100.set_index("연도")[["연평균기온", "5년 이동평균"]]
chart_data.columns = ["연평균 기온 (℃)", "5년 이동평균 (℃)"]

st.line_chart(chart_data, height=500)

col1, col2, col3 = st.columns(3)

first_temp = annual_100.iloc[0]["연평균기온"]
last_temp = annual_100.iloc[-1]["연평균기온"]
change = last_temp - first_temp

with col1:
    st.metric(
        "시작 연도",
        f"{start_year}년",
        f"{first_temp:.1f} ℃"
    )

with col2:
    st.metric(
        "마지막 완전 연도",
        f"{latest_year}년",
        f"{last_temp:.1f} ℃"
    )

with col3:
    st.metric(
        "두 연도의 연평균 기온 차이",
        f"{change:+.1f} ℃"
    )

st.info(
    "실선은 각 연도의 연평균 기온이고, 함께 표시된 5년 이동평균은 "
    "해마다 나타나는 단기적인 변동을 줄여 장기적인 흐름을 보기 쉽게 한 선입니다."
)

with st.expander("연도별 데이터 보기"):
    table = annual_100[["연도", "연평균기온", "5년 이동평균"]].copy()
    table.columns = ["연도", "연평균 기온 (℃)", "5년 이동평균 (℃)"]
    st.dataframe(table, use_container_width=True, hide_index=True)

st.caption(
    "데이터 출처: greatsong/modudata의 서울 기상 관측 자료. "
    "2026년 자료는 연도가 완전히 끝나지 않았으므로 100년 비교에서 제외합니다."
)
