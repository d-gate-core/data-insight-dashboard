import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import CLIENT_SETTINGS

st.set_page_config(layout="wide", page_title=CLIENT_SETTINGS["title"])
st.title(CLIENT_SETTINGS["title"])

st.sidebar.header(CLIENT_SETTINGS["sidebar_title"])
search_term = st.sidebar.text_input(CLIENT_SETTINGS["search_label"])

if st.button("실시간 데이터 수집 시작"):
    st.info("데이터를 가져오는 중입니다...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(CLIENT_SETTINGS["target_url"], headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all(CLIENT_SETTINGS["item_tag"])
        
        data = []
        for item in items[:50]:
            title_elem = item.find("title")
            title = title_elem.text.strip() if title_elem else "제목 없음"
            
            # 기사 제목만 리스트에 담습니다.
            data.append({CLIENT_SETTINGS["columns"][0]: title})
            
        if data:
            st.session_state['df'] = pd.DataFrame(data)
            st.success("수집 완료!")
        else:
            st.error("데이터를 불러오지 못했습니다. 대상 사이트의 구조가 바뀌었거나 차단되었습니다.")
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

if 'df' in st.session_state:
    df = st.session_state['df']
    if search_term:
        col_name = CLIENT_SETTINGS["columns"][0]
        df = df[df[col_name].str.contains(search_term, case=False, na=False)]
    st.dataframe(df, use_container_width=True)