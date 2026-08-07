import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="클래시 오브 클랜 카드 교환 매칭", page_icon="⚔️", layout="centered")

# ⚠️ 여기에 구글 Apps Script 웹앱 URL을 넣으세요!
GAS_URL = "https://script.google.com/macros/s/AKfycby3wOkkVcxR8aalT0WI8BSONibv0zfkrFN176mthE3PAzZPkyBTA0thuQQ40fW8YyrX/exec"

# 카드 데이터베이스 구축
CARD_DB = {
    "💧 엘릭서 유닛": [
        "바바리안", "아처", "자이언트", "고블린", "해골 돌격병", "해골 비행선", 
        "마법사", "힐러", "드래곤", "페카", "베이비드래곤", "광부", 
        "일렉트로 드래곤", "예티", "드래곤 라이더", "일렉트로 타이탄", "트리라이더", "창 투척수", "운석 골렘"
    ],
    "🖤 다크 엘릭서 유닛": [
        "미니언", "호그라이더", "발키리", "골렘", "마녀", "라바 하운드", 
        "볼러", "얼음 골렘", "헤드헌터", "견습생 워든", "드루이드", "용광로", "파멸마녀"
    ],
    "🛠️ 장인기지 유닛": [
        "분노한 바바리안", "은신 아처", "복서 자이언트", "베타 미니언", "폭탄병", 
        "베이비드래곤", "대포카트", "암흑마녀", "해골 수송선", "파워페카", "호그 글라이더"
    ],
    "⚡ 슈퍼유닛": [
        "슈퍼 바바리안", "슈퍼 아처", "슈퍼 자이언트", "슈퍼 고블린", "슈퍼 해골 돌격병", 
        "로켓 비행선", "슈퍼 마법사", "슈퍼 드래곤", "인페르노 드래곤", "능력자 광부", 
        "슈퍼 예티", "슈퍼 미니언", "슈퍼 호그라이더", "슈퍼 마녀", "아이스하운드", "슈퍼 볼러"
    ]
}

# 전체 카드 단일 리스트 생성
ALL_CARDS = []
for category, cards in CARD_DB.items():
    for card in cards:
        ALL_CARDS.append(f"[{category.split()[1]}] {card}")

st.title("⚔️ 클래시 오브 클랜 카드 교환 시스템")
st.write("보유 중인 카드와 원하는 카드를 등록하면, 서로 교환 가능한 방원을 자동으로 찾아드립니다!")

st.divider()

# 1. 정보 입력 폼
st.subheader("📝 내 카드 교환 정보 등록")

with st.form("coc_card_form", clear_on_submit=False):
    nickname = st.text_input("카카오톡 닉네임", placeholder="예: 최고클래시")
    
    have_cards = st.multiselect(
        "📦 내가 보유 중인 카드 (교환해 줄 수 있는 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    want_cards = st.multiselect(
        "🎯 내가 구하는 카드 (갖고 싶은 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    open_chat = st.text_input("오픈채팅/연락처 링크 (선택)", placeholder="https://open.kakao.com/o/...")
    
    submitted = st.form_submit_button("등록 및 자동 매칭 조회")

# 2. 저장 요청
if submitted:
    if not nickname.strip():
        st.error("닉네임을 반드시 입력해 주세요!")
    elif not have_cards:
        st.error("보유 중인 카드를 최소 1개 이상 선택해 주세요!")
    elif not want_cards:
        st.error("구하는 카드를 최소 1개 이상 선택해 주세요!")
    else:
        payload = {
            "nickname": nickname,
            "have_cards": ", ".join(have_cards),
            "want_cards": ", ".join(want_cards),
            "open_chat": open_chat
        }
        
        try:
            res = requests.post(GAS_URL, json=payload)
            if res.status_code == 200:
                st.success(f"🎉 **[{nickname}]**님의 교환 정보가 성공적으로 등록되었습니다!")
            else:
                st.error("저장에 실패했습니다. 관리자에게 문의하세요.")
        except Exception as e:
            st.error("구글 시트 연동 오류가 발생했습니다.")

st.divider()

# 3. 실시간 매칭 추천 현황판
st.header("🤝 추천 교환 매칭 현황판")

try:
    res = requests.get(GAS_URL)
    raw_data = res.json()
    
    if len(raw_data) > 1:
        # 최신 데이터 df 화
        df = pd.DataFrame(raw_data[1:], columns=["nickname", "have_cards", "want_cards", "open_chat", "date"])
        
        # 중복 닉네임 시 최신 데이터만 유지
        df = df.drop_duplicates(subset=["nickname"], keep="last")
        
        user_list = df["nickname"].tolist()
        
        selected_user = st.selectbox("🔍 매칭 상대를 확인할 닉네임을 선택하세요:", ["선택하세요"] + user_list)
        
        if selected_user != "선택하세요":
            my_info = df[df["nickname"] == selected_user].iloc[0]
            my_have = set([c.strip() for c in my_info["have_cards"].split(",") if c.strip()])
            my_want = set([c.strip() for c in my_info["want_cards"].split(",") if c.strip()])
            
            matches = []
            
            for idx, row in df.iterrows():
                if row["nickname"] == selected_user:
                    continue
                
                other_have = set([c.strip() for c in row["have_cards"].split(",") if c.strip()])
                other_want = set([c.strip() for c in row["want_cards"].split(",") if c.strip()])
                
                # 내가 줄 수 있고 상대가 원하는 것
                give = my_have.intersection(other_want)
                # 상대가 줄 수 있고 내가 원하는 것
                take = other_have.intersection(my_want)
                
                if give and take:
                    matches.append({
                        "상대 닉네임": row["nickname"],
                        "내가 줄 카드": ", ".join(give),
                        "내가 받을 카드": ", ".join(take),
                        "상대 오픈채팅": row["open_chat"] if row["open_chat"] else "미입력"
                    })
            
            if matches:
                st.balloons()
                st.success(f"✨ **{selected_user}**님과 **서로 완벽 교환 가능한 방원 {len(matches)}명**을 찾았습니다!")
                match_df = pd.DataFrame(matches)
                st.dataframe(match_df, use_container_width=True, hide_index=True)
            else:
                st.info(f"💡 현재 **{selected_user}**님과 서로 조건이 100% 딱 맞는 교환 상대가 없습니다. 새로운 카드가 등록될 때까지 기다려 보세요!")

        st.divider()
        st.subheader("📋 전체 방원 등록 현황")
        display_all = df[["nickname", "have_cards", "want_cards", "open_chat"]].copy()
        display_all.columns = ["닉네임", "보유 카드", "희망 카드", "연락처/오픈채팅"]
        st.dataframe(display_all, use_container_width=True, hide_index=True)

    else:
        st.info("아직 등록된 교환 정보가 없습니다. 첫 번째로 등록해 보세요!")
except Exception as e:
    st.info("데이터를 불러오는 중입니다.")
