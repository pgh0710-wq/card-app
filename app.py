import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="카톡방 카드 매칭", page_icon="♠️", layout="centered")

# ⚠️ 여기에 아까 복사한 구글 Apps Script 웹앱 URL을 붙여넣으세요!
GAS_URL = "https://script.google.com/macros/s/AKfycbyTGmUC4_gVZOUjgtzkJQMSZMn10A18jTjhVYj13stXLLYHSpTtF8lfdZHXlYhhkpM/exec"

st.title("♠️ 카톡방 포커 카드 매칭 시스템")
st.write("자신의 카드 2장을 입력하면 구글 시트에 실시간 저장되고 2개 보유자 목록이 업데이트됩니다!")

st.divider()

# 1. 카드 입력 폼
st.subheader("📝 내 카드 입력하기")
with st.form("card_input_form", clear_on_submit=True):
    nickname = st.text_input("카카오톡 닉네임", placeholder="예: 홍길동")
    
    col1, col2 = st.columns(2)
    with col1:
        suit1 = st.selectbox("카드 1 문양", ["♠️ 스페이드", "♥️ 하트", "♦️ 다이아", "♣️ 클로버"])
        num1 = st.selectbox("카드 1 숫자", ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"])
        
    with col2:
        suit2 = st.selectbox("카드 2 문양", ["♠️ 스페이드", "♥️ 하트", "♦️ 다이아", "♣️ 클로버"])
        num2 = st.selectbox("카드 2 숫자", ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"])
        
    open_chat = st.text_input("내 오픈채팅/연락처 링크 (선택)", placeholder="https://open.kakao.com/o/...")
    
    submitted = st.form_submit_button("카드 등록 및 매칭 확인")

# 2. 저장 요청
if submitted:
    if not nickname.strip():
        st.error("닉네임을 입력해 주세요!")
    else:
        has_pair = (suit1 == suit2)
        pair_suit = suit1 if has_pair else "없음"
        
        payload = {
            "nickname": nickname,
            "suit1": suit1,
            "num1": num1,
            "suit2": suit2,
            "num2": num2,
            "has_pair": "예" if has_pair else "아니오",
            "pair_suit": pair_suit,
            "open_chat": open_chat
        }
        
        res = requests.post(GAS_URL, json=payload)
        if res.status_code == 200:
            if has_pair:
                st.balloons()
                st.success(f"🎉 **[{nickname}]**님은 **{suit1}** 2개 보유자로 등록되었습니다!")
            else:
                st.success(f"✅ **[{nickname}]**님의 카드 정보가 구글 시트에 실시간 등록되었습니다!")
        else:
            st.error("저장에 실패했습니다. 잠시 후 다시 시도해 주세요.")

st.divider()

# 3. 실시간 2개 보유자 목록
st.header("🤝 현재 동일 문양 2개 보유자 목록")

try:
    res = requests.get(GAS_URL)
    data = res.json()
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        pair_users = df[df["has_pair"] == "예"]
        
        if not pair_users.empty:
            display_df = pair_users[["nickname", "pair_suit", "suit1", "num1", "num2", "open_chat"]].copy()
            display_df.columns = ["닉네임", "2개 보유 문양", "문양", "카드 1", "카드 2", "오픈채팅"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("아직 동일 문양 2개를 가진 방원이 없습니다.")
    else:
        st.info("등록된 데이터가 없습니다. 첫 번째로 등록해 보세요!")
except Exception as e:
    st.info("데이터를 불러오는 중입니다.")