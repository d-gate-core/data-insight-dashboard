import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import CLIENT_SETTINGS  # 설정 파일을 불러옵니다.

# 화면 설정 (설정 파일의 제목 사용)
st.set_page_config(layout="wide", page_title=CLIENT_SETTINGS["title"])
st.title(CLIENT_SETTINGS["title"])

# 사이드바 설정
st.sidebar.header(CLIENT_SETTINGS["sidebar_title"])
search_term = st.sidebar.text_input(CLIENT_SETTINGS["search_label"])

# 데이터 수집 로직
if st.button("실시간 데이터 수집 시작"):
    st.info("데이터를 가져오는 중입니다...")
    
    # 💡 네이버 보안을 통과하기 위한 크롬 브라우저 가짜 신분증(User-Agent) 추가
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(CLIENT_SETTINGS["target_url"], headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 설정 파일에 적힌 태그와 클래스로 데이터를 찾습니다.
    items = soup.find_all(CLIENT_SETTINGS["item_tag"], class_=CLIENT_SETTINGS["item_class"])
    
    data = []
    for item in items[:50]:
        title_elem = item.find("a", class_="news_tit")
        press_elem = item.find("a", class_="info press")
        
        title = title_elem.text.strip() if title_elem else "제목 없음"
        press = press_elem.text.replace("언론사 선정", "").strip() if press_elem else "정보 없음"
        
        data.append({CLIENT_SETTINGS["columns"][0]: title, 
                     CLIENT_SETTINGS["columns"][1]: press})
        
    if data:
        st.session_state['df'] = pd.DataFrame(data)
        st.success("수집 완료!")
    else:
        # 데이터 수집에 실패했을 경우 화면에 표시
        st.error("데이터를 불러오지 못했습니다. 대상 사이트의 구조가 바뀌었거나 차단되었습니다.")

# 결과 출력 및 검색 필터링
if 'df' in st.session_state:
    df = st.session_state['df']
    if search_term:
        # 첫 번째 열(게임명 등)을 기준으로 검색합니다.
        col_name = CLIENT_SETTINGS["columns"][0]
        df = df[df[col_name].str.contains(search_term, case=False, na=False)]
    st.dataframe(df, use_container_width=True)