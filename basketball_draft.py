import streamlit as st
import pandas as pd

st.set_page_config(page_title="Basketball Team Draft", layout="centered")
st.title("🏀 Basketball Team Draft App")
st.markdown("This app helps you draft fair and balanced teams for your 4v4 basketball tournament (with 1 sub per team).")

# Initialize session state
if "manual_players" not in st.session_state:
    st.session_state.manual_players = []

# Input mode selection
input_mode = st.radio("Select Input Mode:", ["Upload CSV", "Manual Entry"])

df = None  # define df upfront

if input_mode == "Upload CSV":
    uploaded_file = st.file_uploader("Upload Google Form CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
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

# Optional: Let user download the manually created data
if input_mode == "Manual Entry" and df is not None and not df.empty:
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Player List as CSV", csv_data, file_name="manual_players.csv")

# Combine both manual and uploaded players
if uploaded_df is not None and not uploaded_df.empty:
    full_df = pd.concat([uploaded_df, manual_players_df], ignore_index=True)
else:
    full_df = manual_players_df.copy()

# Proceed only if we have at least 2 players
if not full_df.empty and len(full_df) >= 2:

    st.subheader("3️⃣ Draft Teams")

    num_teams = st.number_input("Number of Teams", min_value=2, max_value=len(full_df), value=4, step=1)

    if st.button("Draft Teams"):
        # Initialize teams
        teams = [[] for _ in range(num_teams)]
        tier_groups = full_df.groupby("Tier")

        # Distribute players tier by tier
        for tier, group in tier_groups:
            players = group.sample(frac=1).to_dict(orient="records")  # Shuffle
            for idx, player in enumerate(players):
                team_idx = idx % num_teams
                teams[team_idx].append(player)

        st.session_state.teams = teams

    # Display the drafted teams
    if "teams" in st.session_state:
        st.subheader("🧢 Drafted Teams")
        for idx, team in enumerate(st.session_state.teams):
            st.markdown(f"### Team {idx + 1}")
            for player in team:
                st.write(f"{player['Name']} - Tier {player['Tier']}")

        if st.button("Reset Teams"):
            del st.session_state.teams

