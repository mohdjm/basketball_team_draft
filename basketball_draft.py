import streamlit as st
import random
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Basketball Team Draft", layout="centered")

st.title("🏀 Karnival Sukan Lakefront Basketball Team Draft Tool")

# --- Sample Data ---
sample_players = [
	{"name": "Ali", "skill": 3, "type": "Regular"},
	{"name": "Bala", "skill": 2, "type": "Newcomer"},
	{"name": "Chong", "skill": 1, "type": "Regular"},
	{"name": "David", "skill": 4, "type": "Regular"},
	{"name": "Eric", "skill": 2, "type": "Newcomer"},
	{"name": "Faiz", "skill": 3, "type": "Regular"},
	{"name": "Ganesh", "skill": 2, "type": "Regular"},
	{"name": "Hafiz", "skill": 1, "type": "Newcomer"},
	{"name": "Isa", "skill": 4, "type": "Regular"},
	{"name": "Jaya", "skill": 3, "type": "Regular"},
	{"name": "Kevin", "skill": 2, "type": "Newcomer"},
	{"name": "Lim", "skill": 1, "type": "Regular"},
	{"name": "Mani", "skill": 4, "type": "Regular"},
	{"name": "Nash", "skill": 3, "type": "Regular"},
	{"name": "Omar", "skill": 2, "type": "Newcomer"},
]

# --- Player Entry Section ---
st.subheader("Add or Upload Players")

with st.expander("➕ Add Players Manually"):
	name = st.text_input("Player Name")
	skill = st.slider("Skill Tier (1 - Beginner to 4 - Advanced)", 1, 4, 2)
	ptype = st.selectbox("Player Type", ["Regular", "Newcomer"])
	if st.button("Add Player"):
		sample_players.append({"name": name, "skill": skill, "type": ptype})
		st.success(f"Added {name} to the player list.")

with st.expander("📂 Upload CSV (Optional)"):
	uploaded_file = st.file_uploader("Upload CSV with columns: name,skill,type", type="csv")
	if uploaded_file:
		df_upload = pd.read_csv(uploaded_file)
		for _, row in df_upload.iterrows():
			sample_players.append({
				"name": row["name"],
				"skill": int(row["skill"]),
				"type": row["type"]
			})
		st.success("Uploaded and added players from CSV.")

players_df = pd.DataFrame(sample_players)

st.markdown("### 🧍 Registered Players")
st.dataframe(players_df, use_container_width=True)

# --- Draft Configuration ---
st.sidebar.header("⚙️ Draft Settings")
num_teams = st.sidebar.number_input("Number of Teams", min_value=2, value=4, step=1)
draft_mode = st.sidebar.radio("Draft Mode", ["Random Draft", "Balanced Draft"])
shuffle_btn = st.sidebar.button("🔄 Draft Teams")


# --- Drafting Logic ---
def draft_random(players, num_teams):
	random.shuffle(players)
	teams = [[] for _ in range(num_teams)]
	for idx, player in enumerate(players):
		teams[idx % num_teams].append(player)
	return teams


def draft_balanced(players, num_teams):
	sorted_players = sorted(players, key=lambda x: x["skill"], reverse=True)
	teams = [[] for _ in range(num_teams)]
	team_skills = [0] * num_teams

	for player in sorted_players:
		min_team = team_skills.index(min(team_skills))
		teams[min_team].append(player)
		team_skills[min_team] += player["skill"]

	return teams


# --- Show Draft Results ---
if shuffle_btn:
	st.subheader("🏆 Drafted Teams")
	players_copy = sample_players.copy()

	if draft_mode == "Random Draft":
		team_list = draft_random(players_copy, num_teams)
	else:
		team_list = draft_balanced(players_copy, num_teams)

	team_outputs = []
	for i, team in enumerate(team_list):
		st.markdown(f"### 🟦 Team {i + 1}")
		team_df = pd.DataFrame(team)
		st.dataframe(team_df, use_container_width=True)
		output_text = f"Team {i + 1}:\n" + "\n".join(
			f"- {p['name']} (Skill: {p['skill']}, {p['type']})" for p in team
		)
		team_outputs.append(output_text)

	all_output = "\n\n".join(team_outputs)

	with st.expander("📋 Copyable Draft Result"):
		st.text_area("Copy & Share", all_output, height=300)

	st.download_button("📄 Download Teams as TXT", all_output, file_name="drafted_teams.txt")

