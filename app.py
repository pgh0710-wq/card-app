import streamlit as st
import requests
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="coc 카드교환", page_icon="⚔️", layout="centered")

# Streamlit 기본 메뉴 및 워터마크 숨기기
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 구글 Apps Script 웹앱 URL
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

st.title("ARES 카드 교환")
st.write("2장 이상인 카드와 갖고 싶은 카드를 입력하세요.")

st.divider()

# 세션 상태 초기화
if "registered_user" not in st.session_state:
    st.session_state["registered_user"] = ""
if "show_success_msg" not in st.session_state:
    st.session_state["show_success_msg"] = False

# 등록 직후 센스있는 안내 문구 출력
if st.session_state["show_success_msg"]:
    st.toast("!교환 정보 등록 완료! ", icon="🎉")
    st.success(f"🎉 [{st.session_state['registered_user']}]님의 카드가 성공적으로 등록되었습니다!\n\n👇 아래 '🤝 교환 매칭 확인'에서 교환 상대를 바로 확인해보세요!")
    st.balloons()
    st.session_state["show_success_msg"] = False  # 한 번 보여주고 초기화

# 1. 정보 입력 폼
st.subheader("📝 내 카드 교환 정보 등록")

with st.form("coc_card_form", clear_on_submit=False):
    nickname = st.text_input("coc 닉네임", placeholder="예: PSG")
    
    have_cards = st.multiselect(
        "📦 내가 보유 중인 카드 (2장 가지고 있는 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    want_cards = st.multiselect(
        "🎯 내가 구하는 카드 (갖고 싶은 카드)",
        options=ALL_CARDS,
        placeholder="여러 개 선택 가능합니다"
    )
    
    submitted = st.form_submit_button("등록 및 자동 매칭 조회 🚀")

# 2. 저장 요청 처리
if submitted:
    if not nickname.strip():
        st.error("닉네임을 반드시 입력해 주세요!")
    elif not have_cards:
        st.error("보유 중인 카드를 최소 1개 이상 선택해 주세요!")
    elif not want_cards:
        st.error("구하는 카드를 최소 1개 이상 선택해 주세요!")
    else:
        payload = {
            "nickname": nickname.strip(),
            "have_cards": ", ".join(have_cards),
            "want_cards": ", ".join(want_cards)
        }
        
        try:
            res = requests.post(GAS_URL, json=payload)
            if res.status_code == 200:
                st.session_state["registered_user"] = nickname.strip()
                st.session_state["show_success_msg"] = True  # 성공 메시지 플래그 켜기
                st.rerun()
            else:
                st.error("저장에 실패했습니다. 관리자에게 문의하세요.")
        except Exception as e:
            st.error("구글 시트 연동 오류가 발생했습니다.")

st.divider()

# 3. 실시간 매칭 현황판
st.header("🤝 교환 매칭 확인")

try:
    res = requests.get(GAS_URL)
    raw_data = res.json()
    
    if len(raw_data) > 1:
        # 최신 데이터 df 화
        df = pd.DataFrame(raw_data[1:], columns=["nickname", "have_cards", "want_cards", "date"])
        df = df.drop_duplicates(subset=["nickname"], keep="last")
        user_list = df["nickname"].tolist()
        
        # 등록 직후 등록된 닉네임으로 인덱스 자동 지정
        default_idx = 0
        if st.session_state["registered_user"] in user_list:
            default_idx = user_list.index(st.session_state["registered_user"]) + 1

        selected_user = st.selectbox(
            "🔍 내 닉네임을 선택하세요:", 
            ["선택하세요"] + user_list,
            index=default_idx
        )
        
        if selected_user != "선택하세요":
            st.subheader(f"✨ {selected_user}님을 위한 맞춤 교환 리스트")
            
            my_info = df[df["nickname"] == selected_user].iloc[0]
            my_have = set([c.strip() for c in my_info["have_cards"].split(",") if c.strip()])
            my_want = set([c.strip() for c in my_info["want_cards"].split(",") if c.strip()])
            
            match_found_overall = False
            
            # 원하는 카드별로 맞교환 가능 상대 탐색
            for want_card in my_want:
                providers = []
                
                for idx, row in df.iterrows():
                    if row["nickname"] == selected_user:
                        continue
                    
                    other_have = set([c.strip() for c in row["have_cards"].split(",") if c.strip()])
                    other_want = set([c.strip() for c in row["want_cards"].split(",") if c.strip()])
                    
                    if want_card in other_have:
                        give_to_them = my_have.intersection(other_want)
                        if give_to_them:
                            providers.append({
                                "nickname": row["nickname"],
                                "give": ", ".join(give_to_them)
                            })
                
                if providers:
                    match_found_overall = True
                    st.markdown(f"#### 🎯 **{want_card}** 얻기")
                    for p in providers:
                        st.success(f"🤝 **{p['nickname']}** 님과 교환 가능! ➔ (대신 줄 카드: `{p['give']}`)")
            
            if not match_found_overall:
                st.info(f"💡 현재 **{selected_user}**님이 원하시는 카드를 서로 맞교환할 수 있는 방원이 아직 없습니다. 새로운 카드가 등록될 때까지 조금만 기다려 보세요!")

        st.divider()
        
        # 전체 교환 가능 조합 한눈에 보기
        st.subheader("⚡ 현재 가능한 모든 1:1 교환 조합")
        all_matches = []
        processed_pairs = set()

        for i, row1 in df.iterrows():
            for j, row2 in df.iterrows():
                if i >= j:
                    continue
                p1, p2 = row1["nickname"], row2["nickname"]
                pair_key = tuple(sorted([p1, p2]))
                if pair_key in processed_pairs:
                    continue

                p1_have = set([c.strip() for c in row1["have_cards"].split(",") if c.strip()])
                p1_want = set([c.strip() for c in row1["want_cards"].split(",") if c.strip()])
                p2_have = set([c.strip() for c in row2["have_cards"].split(",") if c.strip()])
                p2_want = set([c.strip() for c in row2["want_cards"].split(",") if c.strip()])

                p1_gives = p1_have.intersection(p2_want)
                p2_gives = p2_have.intersection(p1_want)

                if p1_gives and p2_gives:
                    processed_pairs.add(pair_key)
                    all_matches.append({
                        "방원 1": p1,
                        "줄 카드": ", ".join(p1_gives),
                        "방원 2": p2,
                        "받을 카드": ", ".join(p2_gives)
                    })

        if all_matches:
            st.dataframe(pd.DataFrame(all_matches), use_container_width=True, hide_index=True)
        else:
            st.write("아직 조건이 딱 맞는 방원 간의 교환 조합이 없습니다.")

        st.divider()
        st.subheader("📋 전체 등록 현황")
        display_all = df[["nickname", "have_cards", "want_cards"]].copy()
        display_all.columns = ["닉네임", "보유 카드", "희망 카드"]
        st.dataframe(display_all, use_container_width=True, hide_index=True)

    else:
        st.info("아직 등록된 교환 정보가 없습니다. 첫 번째로 등록해 보세요!")
except Exception as e:
    st.info("데이터를 불러오는 중입니다.")
