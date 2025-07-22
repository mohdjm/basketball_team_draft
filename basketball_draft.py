import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Karnival Sukan Lakefront Basketball Team Draft Tool", layout="centered")

st.title("🏀 Karnival Sukan Lakefront Basketball Team Draft Tool")

# --- Helper: Calculate skill score from Google Form answers ---
def calculate_score(row):
    score = 0

    # Scoring maps
    q1_map = {
        "Few times a week": 3,
        "Every week": 2,
        "Once every two weeks": 1,
        "Once a month or less": 0
    }

    q2_map = {
        "Played in MABA/NCBL": 3,
        "Played for school/uni team": 2,
        "Casual player only": 1,
        "Just starting / no experience": 0
    }

    q3_map = {
        "Scorer / Shot creator": 2,
        "Rebounder / Defender / Hustler": 1,
        "Mostly off-ball / learning": 0
    }

    q4_map = {
        "Very confident": 2,
        "Somewhat comfortable": 1,
        "Not sure / Often confused": 0
    }

    q5_map = {
        "Can beat defenders or create shots": 2,
        "Can drive or shoot in rhythm": 1,
        "Rarely score / prefer passing": 0
    }

    score += q1_map.get(row["Q1_How_often"], 0)
    score += q2_map.get(row["Q2_Level"], 0)
    score += q3_map.get(row["Q3_Self_role"], 0)
    score += q4_map.get(row["Q4_Confidence"], 0)
    score += q5_map.get(row["Q5_Offense"], 0)

    return score

# --- Helper: Convert score to tier ---
def score_to_tier(score):
    if score >= 10:
        return 1
    elif score >= 7:
        return 2
    elif score >= 4:
        return 3
    else:
        return 4

# --- Helper: Draft Balanced Teams ---
def draft_balanced_teams(df, num_teams):
    players = df.to_dict("records")
    players.sort(key=lambda x: x["Tier"])  # sort by tier for better balance
    random.shuffle(players)  # shuffle to avoid predictable pattern

    teams = [[] for _ in range(num_teams)]
    for i, player in enumerate(players):
        teams[i % num_teams].append(player)

    return teams

# --- Upload CSV section ---
uploaded_file = st.file_uploader("Upload Google Form Responses (.csv)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if "Name" not in df.columns:
        st.error("CSV must include a 'Name' column.")
    else:
        # Calculate scores and tiers
        df["Score"] = df.apply(calculate_score, axis=1)
        df["Tier"] = df["Score"].apply(score_to_tier)

        st.subheader("📋 Player List with Tiers")
        st.dataframe(df[["Name", "Score", "Tier"]])

        # Team selection
        num_teams = st.number_input("Number of Teams", min_value=2, max_value=12, value=4, step=1)

        # Init session state
        if "teams" not in st.session_state:
            st.session_state.teams = []

        # Draft buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Draft Teams"):
                st.session_state.teams = draft_balanced_teams(df, num_teams)
                st.success("Teams drafted!")

        with col2:
            if st.button("🔁 Re-Draft Teams"):
                st.session_state.teams = draft_balanced_teams(df, num_teams)
                st.success("Teams re-drafted!")

        with col3:
            if st.button("🧹 Reset Draft"):
                st.session_state.teams = []
                st.warning("Teams have been reset.")

        # Display teams if available
        if st.session_state.teams:
            st.subheader("🏆 Drafted Teams")
            for i, team in enumerate(st.session_state.teams, 1):
                st.markdown(f"### Team {i}")
                st.table(pd.DataFrame(team)[["Name", "Tier"]])