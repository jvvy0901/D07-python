import os
from pathlib import Path

import requests
import streamlit as st

API = {
    "weather": "https://api.openweathermap.org/data/2.5/weather",  # 🔌 OpenWeather 현재 날씨
}
KEY_NAME = "OPENWEATHER_API_KEY"
DEFAULT_CITY = "Seoul"


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


def fetch_weather(city, api_key):
    """날씨 데이터를 (data, 오류메시지) 형태로 돌려준다."""
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(API["weather"], params=params, timeout=10)  # 🔌 API 호출
    except requests.RequestException:
        return None, "날씨 서버에 연결하지 못했어요. 인터넷 연결을 확인해 주세요"

    if res.status_code == 401:
        return None, "날씨 키가 틀렸거나 아직 켜지지 않았어요 (가입 후 최대 2시간)"
    if res.status_code == 404:
        return None, "그 도시를 찾지 못했어요"
    if res.status_code == 429:
        return None, "1분에 너무 많이 불렀어요. 잠시 뒤에 다시 해 주세요"
    if not res.ok:
        return None, f"날씨 정보를 가져오지 못했어요 (오류 코드 {res.status_code})"
    return res.json(), None


def main():
    st.set_page_config(page_title="현재 날씨", page_icon="🌤️")
    st.title("🌤️ 현재 날씨")

    load_env()
    api_key = os.getenv(KEY_NAME)
    if not api_key:
        st.error(f".env에 {KEY_NAME}가 없어요. .env.example을 보고 채워 주세요")
        return

    city = st.text_input("도시 이름 (영문)", value=DEFAULT_CITY)
    if not city.strip():
        st.info("도시 이름을 입력해 주세요")
        return

    with st.spinner("날씨를 가져오는 중..."):
        data, error = fetch_weather(city.strip(), api_key)
    if error:
        st.error(error)
        return

    temp = data["main"]["temp"]  # data["main"]["temp"] = 지금 기온
    feels = data["main"]["feels_like"]  # data["main"]["feels_like"] = 체감 온도
    humidity = data["main"]["humidity"]  # data["main"]["humidity"] = 습도(%)
    desc = data["weather"][0]["description"]  # data["weather"][0]["description"] = 날씨 설명(한국어)

    st.subheader(f"{data.get('name', city)} 현재 날씨 · {desc}")
    col1, col2, col3 = st.columns(3)
    col1.metric("기온", f"{temp:.1f}°C")
    col2.metric("체감 온도", f"{feels:.1f}°C")
    col3.metric("습도", f"{humidity}%")
    st.caption("날씨: OpenWeather")


if __name__ == "__main__":
    main()
