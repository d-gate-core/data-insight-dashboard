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
        soup = BeautifulSoup(response.text, "xml") # RSS 처리를 위해 xml 파서 사용
        items = soup.find_all(CLIENT_SETTINGS["item_tag"])
        
        data = []
        for item in items[:50]:
            title_elem = item.find("title")
            pubdate_elem = item.find("pubDate")
            link_elem = item.find("link")
            
            title = title_elem.text.strip() if title_elem else "제목 없음"
            # 날짜 데이터에서 불필요한 요일과 시간대 정보 깔끔하게 자르기
            pubdate = pubdate_elem.text.strip()[5:16] if pubdate_elem else "날짜 없음"
            link = link_elem.text.strip() if link_elem else ""
            
            data.append({
                CLIENT_SETTINGS["columns"][0]: title,
                CLIENT_SETTINGS["columns"][1]: pubdate,
                CLIENT_SETTINGS["columns"][2]: link
            })
            
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
        
    # Streamlit 표에서 링크를 클릭 가능한 형태로 변환하여 출력
    st.dataframe(
        df, 
        column_config={
            CLIENT_SETTINGS["columns"][2]: st.column_config.LinkColumn("원문 링크 확인")
        },
        use_container_width=True
    )