import streamlit as st
import pandas as pd

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
