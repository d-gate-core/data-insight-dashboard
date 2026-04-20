import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("🎮 스팀(Steam) 실시간 할인 대시보드")
st.write("스팀 상점에서 현재 할인 중인 게임 목록을 가져옵니다.")

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
        df = pd.DataFrame(data)
        st.success("수집 완료!")
        
        # --- 검색 기능이 추가된 부분 ---
        search_term = st.text_input("🔍 검색할 게임 이름을 입력하세요:")
        if search_term:
            filtered_df = df[df['게임명'].str.contains(search_term, case=False, na=False)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
        # -------------------------------
    else:
        st.error("데이터를 가져오지 못했습니다.")