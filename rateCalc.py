import os
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

API = {
    "rate": "https://v6.exchangerate-api.com/v6/latest",  # 🔌 ExchangeRate-API 환율 (뒤에 /통화코드)
}
KEY_NAME = "EXCHANGERATE_API_KEY"
CURRENCIES = {
    "KRW": "🇰🇷 원 (KRW)",
    "USD": "🇺🇸 미국 달러 (USD)",
    "JPY": "🇯🇵 일본 엔 (JPY)",
    "EUR": "🇪🇺 유로 (EUR)",
    "CNY": "🇨🇳 중국 위안 (CNY)",
    "GBP": "🇬🇧 영국 파운드 (GBP)",
    "AUD": "🇦🇺 호주 달러 (AUD)",
    "CAD": "🇨🇦 캐나다 달러 (CAD)",
    "CHF": "🇨🇭 스위스 프랑 (CHF)",
    "THB": "🇹🇭 태국 바트 (THB)",
    "VND": "🇻🇳 베트남 동 (VND)",
}
ERRORS = {
    "invalid-key": "환율 키가 틀렸어요",
    "inactive-account": "환율 사이트 가입 인증 메일을 확인해 주세요",
    "quota-reached": "이번 달 무료 사용량(1,500번)을 다 썼어요",
}

STYLE = """
<style>
.stApp { background: linear-gradient(135deg, #fff1eb 0%, #ace0f9 100%); }
h1 { background: linear-gradient(90deg, #ff6a88, #ff99ac, #7f7fd5, #86a8e7, #91eae4);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.result { border-radius: 20px; padding: 28px; text-align: center; color: white;
          background: linear-gradient(120deg, #f093fb 0%, #f5576c 50%, #ffb347 100%);
          box-shadow: 0 8px 24px rgba(245, 87, 108, .35); }
.result .big { font-size: 2.6rem; font-weight: 800; }
.result .small { font-size: 1.05rem; opacity: .95; }
.chip { display: inline-block; border-radius: 999px; padding: 6px 14px; margin: 4px;
        color: white; font-weight: 600; }
</style>
"""
CHIP_COLORS = ["#ff6a88", "#7f7fd5", "#38b6a3", "#f5a623", "#4facfe", "#c471ed"]


def load_env():
    """같은 폴더의 .env 를 읽어 환경변수로 등록 (KEY=값 형식)."""
    env_file = Path(__file__).with_name(".env")
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip())


@st.cache_data(ttl=3600)  # 환율은 하루 한 번 갱신 → 1시간 캐시로 호출 횟수 아끼기
def fetch_rates(base, api_key):
    """(환율 정보, 오류메시지) 를 돌려준다. 키·주소는 화면에 내보내지 않는다."""
    headers = {"Authorization": f"Bearer {api_key}"}  # 🔌 키는 헤더로만 보냄
    try:
        res = requests.get(f"{API['rate']}/{base}", headers=headers, timeout=10)  # 🔌 API 호출
    except requests.RequestException:
        return None, "환율 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요"

    try:
        data = res.json()
    except ValueError:
        return None, f"환율 정보를 가져오지 못했어요 (오류 코드 {res.status_code})"

    if data.get("result") != "success":
        error_type = data.get("error-type", "")  # data["error-type"] = 오류 종류
        return None, ERRORS.get(error_type, f"환율 정보를 가져오지 못했어요 ({error_type or res.status_code})")

    return {
        "rates": data["conversion_rates"],  # data["conversion_rates"] = 통화별 환율
        "updated": data["time_last_update_utc"],  # data["time_last_update_utc"] = 환율 기준 시각(UTC)
    }, None


def to_kst(utc_text):
    """'Thu, 22 Oct 2026 00:00:01 +0000' → 한국 시간 문자열."""
    try:
        kst = parsedate_to_datetime(utc_text).astimezone(ZoneInfo("Asia/Seoul"))
    except (TypeError, ValueError):
        return utc_text
    return kst.strftime("%Y-%m-%d %H:%M (한국 시간)")


def main():
    st.set_page_config(page_title="환율 계산기", page_icon="💱")
    st.markdown(STYLE, unsafe_allow_html=True)
    st.title("💱 환율 계산기")

    load_env()
    api_key = os.getenv(KEY_NAME)
    if not api_key:
        st.error(f".env에 {KEY_NAME}가 없어요. .env.example을 보고 채워 주세요")
        return

    col1, col2 = st.columns(2)
    base = col1.selectbox("바꿀 돈", list(CURRENCIES), format_func=CURRENCIES.get, index=1)
    target = col2.selectbox("받을 돈", list(CURRENCIES), format_func=CURRENCIES.get, index=0)
    amount = st.number_input("금액", min_value=0.0, value=100.0, step=10.0)

    if st.button("🔄 새로 불러오기"):
        st.cache_data.clear()

    with st.spinner("환율을 가져오는 중..."):
        info, error = fetch_rates(base, api_key)
    if error:
        st.error(error)
        return

    rate = info["rates"][target]  # info["rates"][target] = 1 단위당 받을 돈
    result = amount * rate
    st.markdown(
        f"""<div class="result">
        <div class="small">{amount:,.2f} {base} =</div>
        <div class="big">{result:,.2f} {target}</div>
        <div class="small">1 {base} = {rate:,.4f} {target}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    st.subheader("🌈 다른 통화로는?")
    chips = ""
    others = [code for code in CURRENCIES if code not in (base, target)]
    for i, code in enumerate(others):
        color = CHIP_COLORS[i % len(CHIP_COLORS)]
        chips += f'<span class="chip" style="background:{color}">{code} {amount * info["rates"][code]:,.2f}</span>'
    st.markdown(chips, unsafe_allow_html=True)

    st.caption(f"환율: ExchangeRate-API · 기준 시각 {to_kst(info['updated'])}")


if __name__ == "__main__":
    main()
