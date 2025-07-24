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

        # --- Captain Selection ---
st.sidebar.subheader("Select Team Captains")
all_player_names = df["Name"].tolist()
captain_names = st.sidebar.multiselect(
    "Choose one captain per team:",
    options=all_player_names,
    max_selections=num_teams
)

# Draft buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🚀 Draft Teams"):
        if len(captain_names) != num_teams:
            st.error(f"Please select exactly {num_teams} captains in the sidebar.")
        else:
            captains_df = df[df["Name"].isin(captain_names)]
            remaining_df = df[~df["Name"].isin(captain_names)]

            # Shuffle captains and assign 1 per team
            captains_df = captains_df.sample(frac=1, random_state=42).reset_index(drop=True)
            teams = [[] for _ in range(num_teams)]
            for i, captain in enumerate(captains_df.itertuples(index=False)):
                teams[i].append({"Name": captain.Name, "Tier": captain.Tier, "Captain": True})

            # Shuffle remaining and assign to teams by tier
            remaining_players = remaining_df.sample(frac=1, random_state=42).sort_values("Tier").reset_index(drop=True)
            for i, player in enumerate(remaining_players.itertuples(index=False)):
                teams[i % num_teams].append({"Name": player.Name, "Tier": player.Tier})

            st.session_state.teams = teams
            st.success("Teams drafted with selected captains!")

with col2:
    if st.button("🔁 Re-Draft Teams"):
        st.session_state.teams = draft_balanced_teams(df, num_teams)
        st.success("Teams re-drafted (random captains).")

with col3:
    if st.button("🧹 Reset Draft"):
        st.session_state.teams = []
        st.warning("Teams have been reset.")


        # Display teams if available
if st.session_state.teams:
    st.subheader("🏆 Drafted Teams")
    for i, team in enumerate(st.session_state.teams, 1):
        st.markdown(f"### Team {i}")
        team_df = pd.DataFrame(team)
        if "Captain" in team_df.columns:
            team_df["Captain"] = team_df["Captain"].fillna(False)
            team_df["Name"] = team_df.apply(lambda row: f"⭐ {row['Name']}" if row["Captain"] else row["Name"], axis=1)
            team_df.drop(columns="Captain", inplace=True)
        st.table(team_df[["Name", "Tier"]])
