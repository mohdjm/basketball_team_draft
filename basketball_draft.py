
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="🏀 Basketball Team Draft Tool", layout="centered")
st.title("🏀 Basketball Team Draft Tool")
st.markdown("This app helps you draft fair and balanced teams for your 4v4 basketball tournament (with 1 sub per team).")

# Initialize session state
if "manual_players" not in st.session_state:
    st.session_state.manual_players = []
if "teams" not in st.session_state:
    st.session_state.teams = []

# --- Helper: Draft Balanced Teams ---
def draft_balanced_teams(df, num_teams):
    players = df.to_dict("records")
    players.sort(key=lambda x: x["Tier"])  # Sort by tier
    random.shuffle(players)  # Shuffle for randomness

    teams = [[] for _ in range(num_teams)]
    for i, player in enumerate(players):
        teams[i % num_teams].append(player)
    return teams

# --- Input Mode ---
input_mode = st.radio("Select Input Mode:", ["Upload CSV", "Manual Entry"])
df = None

if input_mode == "Upload CSV":
    uploaded_file = st.file_uploader("Upload Google Form CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "Name" not in df.columns or "Tier" not in df.columns:
            st.error("CSV must include 'Name' and 'Tier' columns.")
            df = None
        else:
            st.success("CSV uploaded successfully!")
            st.dataframe(df)

elif input_mode == "Manual Entry":
    st.subheader("Add Players Manually")
    name = st.text_input("Player Name")
    tier = st.selectbox("Skill Tier (1 = Beginner, 4 = Advanced)", [1, 2, 3, 4])

    if st.button("Add Player"):
        if name:
            st.session_state.manual_players.append({"Name": name, "Tier": tier})
            st.success(f"Added {name} (Tier {tier})")
        else:
            st.warning("Please enter a player name.")

    if st.session_state.manual_players:
        st.subheader("Current Players")
        df = pd.DataFrame(st.session_state.manual_players)
        st.dataframe(df)

    if df is not None and not df.empty:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Player List as CSV", csv_data, file_name="manual_players.csv")

# --- Draft Teams ---
if df is not None and not df.empty:
    st.subheader("Draft Teams")
    num_teams = st.number_input("Number of Teams", min_value=2, max_value=len(df), value=4, step=1)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Draft Teams"):
            st.session_state.teams = draft_balanced_teams(df, num_teams)
            st.success("Teams drafted!")

    with col2:
        if st.button("🔁 Re-Draft"):
            st.session_state.teams = draft_balanced_teams(df, num_teams)
            st.info("Teams re-drafted.")

    with col3:
        if st.button("🧹 Reset"):
            st.session_state.teams = []
            st.warning("Teams reset.")

# --- Display Drafted Teams ---
if st.session_state.teams:
    st.subheader("🏆 Drafted Teams")
    for i, team in enumerate(st.session_state.teams, 1):
        st.markdown(f"### Team {i}")
        team_df = pd.DataFrame(team)
        st.table(team_df)
