import streamlit as st
import requests
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="coc 카드교환", page_icon="⚔️", layout="centered")

# ⚠️ Streamlit 기본 메뉴 및 워터마크 깔끔하게 숨기기
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ⚠️ 구글 Apps Script 웹앱 URL을 확인하세요!
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

st.title("⚔️카드 교환 시스템⚔️")
st.write("보유중(2장 이상)인 카드와 원하는(갖고 싶은)카드를 입력하세요.")

st.divider()

# 1. 정보 입력 폼 (연락처 제거됨)
st.subheader("📝내 카드 교환 정보 등록")

with st.form("coc_card_form", clear_on_submit=False):
    nickname = st.text_input("카카오톡 닉네임", placeholder="예: PSG")
    
    have_cards = st.multiselect(
        "📦내가 보유 중인 카드 (2장 가지고 있는 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    want_cards = st.multiselect(
        "🎯 내가 구하는 카드 (갖고 싶은 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    submitted = st.form_submit_button("등록 및 저장")

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
            "want_cards": ", ".join(want_cards)
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

# 3. 실시간 매칭 추천 현황판 (원하는 카드별 보기 방식으로 변경)
st.header("🤝 내 맞춤형 교환 매칭 확인")

try:
    res = requests.get(GAS_URL)
    raw_data = res.json()
    
    if len(raw_data) > 1:
        # 최신 데이터 df 화 (헤더 제외)
        df = pd.DataFrame(raw_data[1:], columns=["nickname", "have_cards", "want_cards", "date"])
        
        # 중복 닉네임 시 최신 데이터만 유지
        df = df.drop_duplicates(subset=["nickname"], keep="last")
        user_list = df["nickname"].tolist()
        
        selected_user = st.selectbox("🔍 내 닉네임을 선택하세요:", ["선택하세요"] + user_list)
        
        if selected_user != "선택하세요":
            st.subheader(f"✨ {selected_user}님을 위한 교환 추천 리스트")
            
            my_info = df[df["nickname"] == selected_user].iloc[0]
            my_have = set([c.strip() for c in my_info["have_cards"].split(",") if c.strip()])
            my_want = set([c.strip() for c in my_info["want_cards"].split(",") if c.strip()])
            
            match_found_overall = False
            
            # 원하는 카드별로 분류해서 보여주기
            for want_card in my_want:
                providers = []
                
                for idx, row in df.iterrows():
                    if row["nickname"] == selected_user:
                        continue
                    
                    other_have = set([c.strip() for c in row["have_cards"].split(",") if c.strip()])
                    other_want = set([c.strip() for c in row["want_cards"].split(",") if c.strip()])
                    
                    # 1. 상대방이 내가 원하는 카드를 가지고 있는가?
                    if want_card in other_have:
                        # 2. 내가 상대방이 원하는 카드를 줄 수 있는가? (서로 교환 성립)
                        give_to_them = my_have.intersection(other_want)
                        
                        if give_to_them:
                            providers.append({
                                "nickname": row["nickname"],
                                "give": ", ".join(give_to_them)
                            })
                
                # 이 카드를 교환할 수 있는 상대가 있다면 출력
                if providers:
                    match_found_overall = True
                    with st.container():
                        st.markdown(f"#### 🎯 **{want_card}** 얻기")
                        for p in providers:
                            st.success(f"🤝 **{p['nickname']}** 님과 교환 가능! ➔ (대신 줄 카드: `{p['give']}`)")
            
            if match_found_overall:
                st.balloons()
            else:
                st.info(f"💡 현재 {selected_user}님이 원하시는 카드를 서로 맞교환할 수 있는 방원이 아직 없습니다. 조금 더 기다려 보세요!")

        st.divider()
        st.subheader("📋 전체 등록 현황")
        display_all = df[["nickname", "have_cards", "want_cards"]].copy()
        display_all.columns = ["닉네임", "보유 카드", "희망 카드"]
        st.dataframe(display_all, use_container_width=True, hide_index=True)

    else:
        st.info("아직 등록된 교환 정보가 없습니다. 첫 번째로 등록해 보세요!")
except Exception as e:
    st.info("데이터를 불러오는 중입니다.")
