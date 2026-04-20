import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 화면을 넓게 쓰도록 설정
st.set_page_config(layout="wide")

st.title("🎮 스팀(Steam) 실시간 할인 대시보드")

# 왼쪽 사이드바(메뉴)에 검색창을 고정으로 빼둡니다.
st.sidebar.header("⚙️ 검색 및 설정")
search_term = st.sidebar.text_input("🔍 게임 이름 검색")

# 버튼을 누르면 수집 시작
if st.button("할인 데이터 수집 시작"):
    st.info("데이터를 가져오는 중입니다...")
    
    url = "https://store.steampowered.com/search/?specials=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    games = soup.find_all("a", class_="search_result_row")
    
    data = []
    for game in games[:50]:
        title = game.find("span", class_="title").text.strip()
        price_elem = game.find("div", class_="discount_final_price")
        price = price_elem.text.strip() if price_elem else "무료 또는 가격 없음"
        
        data.append({"게임명": title, "현재 가격": price})
        
    if data:
        # 서버가 데이터를 까먹지 않게 'df'라는 이름의 저장소에 보관해둡니다.
        st.session_state['df'] = pd.DataFrame(data)
        st.success("수집 완료!")
    else:
        st.error("데이터를 가져오지 못했습니다.")

# 저장소에 데이터가 존재하면, 새로고침이 되어도 표를 계속 그려줍니다.
if 'df' in st.session_state:
    df = st.session_state['df']
    
    # 검색어 필터링 적용
    if search_term:
        df = df[df['게임명'].str.contains(search_term, case=False, na=False)]
        
    st.dataframe(df, use_container_width=True)