import streamlit as st
import requests
import pandas as pd
import time

# 페이지 설정 (다시 centered로 복구)
st.set_page_config(page_title="coc 카드교환", page_icon="⚔️", layout="centered")

# CSS 커스텀: 중앙 정렬 화면 내에서 6열 버튼이 한눈에 쏙 들어가도록 정밀 조절
custom_css = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 버튼 열 간격 세밀하게 줄이기 */
div[data-testid="column"] {
    padding: 0px 1px !important;
}

/* 버튼 크기 및 폰트 세밀 조절 (centered 공간에 최적화) */
div[data-testid="stButton"] > button {
    font-size: 10px !important;          /* 폰트 크기 미세 축소 */
    padding: 2px 0px !important;         /* 좌우 여백 최소화 */
    height: 36px !important;             /* 버튼 높이 균일화 */
    white-space: nowrap !important;      /* 줄바꿈 강제 방지 */
    word-break: keep-all !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* 모바일 화면 대응 */
@media (max-width: 600px) {
    div[data-testid="stButton"] > button {
        font-size: 8.5px !important;
        height: 32px !important;
    }
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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
        "슈퍼 예티", "슈퍼 미니언", "슈퍼 호그라이더", "슈퍼 발키리", "슈퍼 마녀", "아이스하운드", "슈퍼 볼러"
    ]
}

# 세션 상태 초기화
if "registered_user" not in st.session_state:
    st.session_state["registered_user"] = ""
if "show_success_msg" not in st.session_state:
    st.session_state["show_success_msg"] = False
if "have_selected" not in st.session_state:
    st.session_state["have_selected"] = set()
if "want_selected" not in st.session_state:
    st.session_state["want_selected"] = set()

st.title("ARES 카드 교환")
st.write("2장 이상인 카드와 갖고 싶은 카드를 버튼으로 터치하여 선택하세요!")

st.divider()

# 등록 직후 안내 문구
if st.session_state["show_success_msg"]:
    st.toast("교환 정보 등록 완료!", icon="🎉")
    st.success(f"🎉 **[{st.session_state['registered_user']}]**님의 카드가 성공적으로 등록되었습니다!\n\n👇 아래 '🤝 교환 매칭 확인'에서 교환 상대를 바로 확인해보세요!")
    st.balloons()
    st.session_state["show_success_msg"] = False

# 1. 정보 입력 폼
st.subheader("📝 내 카드 교환 정보 등록")

nickname = st.text_input("coc 닉네임", placeholder="예: PSG")

# 카드 그리드 버튼 생성 함수 (6열 바둑판 배치)
def render_card_buttons(target_set_key, cols_per_row=6):
    for category_name, cards in CARD_DB.items():
        st.markdown(f"##### {category_name}")
        cols = st.columns(cols_per_row)
        for idx, card in enumerate(cards):
            full_card_name = f"[{category_name.split()[1]}] {card}"
            is_selected = full_card_name in st.session_state[target_set_key]
            
            label = f"✅ {card}" if is_selected else card
            btn_type = "primary" if is_selected else "secondary"
            
            with cols[idx % cols_per_row]:
                if st.button(label, key=f"{target_set_key}_{category_name}_{card}", type=btn_type, use_container_width=True):
                    if is_selected:
                        st.session_state[target_set_key].remove(full_card_name)
                    else:
                        st.session_state[target_set_key].add(full_card_name)
                    st.rerun()

# 보유/구하는 카드 선택 탭
tab1, tab2 = st.tabs(["📦 내가 보유 중인 카드 (2장 이상)", "🎯 내가 구하는 카드"])

with tab1:
    st.caption("내가 2장 이상 가지고 있어 **남에게 줄 수 있는 카드**를 터치하세요.")
    if st.button("🗑️ 보유 카드 전체 선택 해제", key="reset_have"):
        st.session_state["have_selected"].clear()
        st.rerun()
    render_card_buttons("have_selected")

with tab2:
    st.caption("내가 **받고 싶은 카드**를 터치하세요.")
    if st.button("🗑️ 희망 카드 전체 선택 해제", key="reset_want"):
        st.session_state["want_selected"].clear()
        st.rerun()
    render_card_buttons("want_selected")

st.markdown("---")

# 현재 선택된 카드 요약 출력
st.markdown("##### 📌 현재 선택 현황 요약")
selected_have_list = list(st.session_state["have_selected"])
selected_want_list = list(st.session_state["want_selected"])

st.write("**📦 내가 줄 카드:** " + (", ".join([f"`{c}`" for c in selected_have_list]) if selected_have_list else "_선택 없음_"))
st.write("**🎯 내가 받을 카드:** " + (", ".join([f"`{c}`" for c in selected_want_list]) if selected_want_list else "_선택 없음_"))

st.write("")

# 제출 버튼
if st.button("🚀 등록 및 자동 매칭 조회", type="primary", use_container_width=True):
    if not nickname.strip():
        st.error("닉네임을 반드시 입력해 주세요!")
    elif not selected_have_list:
        st.error("보유 중인 카드를 최소 1개 이상 선택해 주세요!")
    elif not selected_want_list:
        st.error("구하는 카드를 최소 1개 이상 선택해 주세요!")
    else:
        payload = {
            "nickname": nickname.strip(),
            "have_cards": ", ".join(selected_have_list),
            "want_cards": ", ".join(selected_want_list)
        }
        
        try:
            res = requests.post(GAS_URL, json=payload)
            if res.status_code == 200:
                st.session_state["registered_user"] = nickname.strip()
                st.session_state["show_success_msg"] = True
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("저장에 실패했습니다. 관리자에게 문의하세요.")
        except Exception as e:
            st.error("구글 시트 연동 오류가 발생했습니다.")

st.divider()

# 2. 실시간 매칭 현황판
st.header("🤝 교환 매칭 확인")

if st.button("🔄 실시간 매칭 새로고침"):
    st.rerun()

try:
    res = requests.get(GAS_URL)
    raw_data = res.json()
    
    if len(raw_data) > 1:
        data_rows = raw_data[1:]
        clean_rows = []
        for r in data_rows:
            if len(r) >= 3:
                clean_rows.append([r[0], r[1], r[2], r[3] if len(r) > 3 else ""])
                
        df = pd.DataFrame(clean_rows, columns=["nickname", "have_cards", "want_cards", "date"])
        df = df.drop_duplicates(subset=["nickname"], keep="last")
        user_list = df["nickname"].tolist()
        
        st.markdown(f"👥 **참여 중인 클랜원 ({len(user_list)}명):** " + " ".join([f"`{u}`" for u in user_list]))
        st.write("")

        default_idx = 0
        if st.session_state["registered_user"] in user_list:
            default_idx = user_list.index(st.session_state["registered_user"]) + 1

        selected_user = st.selectbox(
            "🔍 내 닉네임을 선택하세요:", 
            ["선택하세요"] + user_list,
            index=default_idx
        )
        
        if selected_user != "선택하세요":
            st.subheader(f"{selected_user}님의 교환 리스트")
            
            my_info = df[df["nickname"] == selected_user].iloc[0]
            my_have = set([c.strip() for c in str(my_info["have_cards"]).split(",") if c.strip()])
            my_want = set([c.strip() for c in str(my_info["want_cards"]).split(",") if c.strip()])
            
            perfect_matches = []

            for want_card in my_want:
                for idx, row in df.iterrows():
                    if row["nickname"] == selected_user:
                        continue
                    
                    other_name = row["nickname"]
                    other_have = set([c.strip() for c in str(row["have_cards"]).split(",") if c.strip()])
                    other_want = set([c.strip() for c in str(row["want_cards"]).split(",") if c.strip()])
                    
                    if want_card in other_have:
                        give_to_them = my_have.intersection(other_want)
                        if give_to_them:
                            perfect_matches.append({
                                "want": want_card,
                                "target": other_name,
                                "give": ", ".join(give_to_them)
                            })

            if perfect_matches:
                for item in perfect_matches:
                    st.success(f"🎯 **{item['want']}** ➔ **[{item['target']}]** 님과 교환 가능! (내가 줄 카드: `{item['give']}`)")
            else:
                st.info(f"💡 현재 **[{selected_user}]**님이 원하시는 카드를 서로 맞교환할 수 있는 클랜원이 아직 없습니다. 새로운 카드가 등록될 때까지 조금만 기다려 보세요!")

        st.divider()
        
        st.subheader("가능한 교환 조합")
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

                p1_have = set([c.strip() for c in str(row1["have_cards"]).split(",") if c.strip()])
                p1_want = set([c.strip() for c in str(row1["want_cards"]).split(",") if c.strip()])
                p2_have = set([c.strip() for c in str(row2["have_cards"]).split(",") if c.strip()])
                p2_want = set([c.strip() for c in str(row2["want_cards"]).split(",") if c.strip()])

                p1_gives = p1_have.intersection(p2_want)
                p2_gives = p2_have.intersection(p1_want)

                if p1_gives and p2_gives:
                    processed_pairs.add(pair_key)
                    all_matches.append({
                        "클랜원 A": p1,
                        "A가 줄 카드": ", ".join(p1_gives),
                        "클랜원 B": p2,
                        "B가 줄 카드": ", ".join(p2_gives)
                    })

        if all_matches:
            st.dataframe(pd.DataFrame(all_matches), use_container_width=True, hide_index=True)
        else:
            st.write("아직 조건이 딱 맞는 클랜원 간의 교환 조합이 없습니다.")

        st.divider()
        st.subheader("📋 전체 등록 현황")
        display_all = df[["nickname", "have_cards", "want_cards"]].copy()
        display_all.columns = ["닉네임", "보유 카드", "희망 카드"]
        st.dataframe(display_all, use_container_width=True, hide_index=True)

    else:
        st.info("아직 등록된 교환 정보가 없습니다. 첫 번째로 등록해 보세요!")
except Exception as e:
    st.info("데이터를 불러오는 중입니다.")
