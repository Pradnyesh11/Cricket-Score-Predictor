from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "t20_score_predictor.pkl"
MODEL_FEATURES = (
    "city",
    "bowling_team",
    "batting_team",
    "balls_left",
    "wickets_left",
    "crr",
    "last_five",
    "current_score2",
)
TEAM_CODES = {
    "Australia": 0,
    "Bangladesh": 1,
    "England": 2,
    "India": 3,
    "Ireland": 4,
    "Netherlands": 5,
    "New Zealand": 6,
    "Pakistan": 7,
    "Scotland": 8,
    "South Africa": 9,
    "Sri Lanka": 10,
    "West Indies": 11,
    "Zimbabwe": 12,
}
DEFAULT_CITY_CODE = 44

st.set_page_config(
    page_title="Cricket Score Predictor",
    page_icon="🏏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background: #0d1410; color: #f3f6f2; }
    .block-container { max-width: 760px; padding-top: 2.5rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -.04em; }
    [data-testid="stMetric"] {
        background: #151f19; border: 1px solid #2b3a30;
        border-radius: 14px; padding: 18px;
    }
    [data-testid="stMetricValue"] { color: #c6f36b; }
    label, [data-testid="stWidgetLabel"] { color: #dce5dd !important; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #141d17; border-color: #34443a; border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    with MODEL_PATH.open("rb") as model_file:
        model = pickle.load(model_file)

    feature_names = tuple(getattr(model, "feature_names_in_", ()))
    if feature_names != MODEL_FEATURES:
        raise ValueError(
            "The model feature order does not match this app. "
            f"Expected {MODEL_FEATURES}, received {feature_names}."
        )
    return model


try:
    model = load_model()
except FileNotFoundError as error:
    st.error(
        f"Model file not found: {error.filename}. "
        "Keep t20_score_predictor.pkl in the project folder."
    )
    st.stop()
except (OSError, pickle.UnpicklingError, ValueError) as error:
    st.error(f"Could not load the score predictor: {error}")
    st.stop()

st.title("🏏 Cricket Score Predictor")
st.caption("T20 final-score estimate")

first_row, second_row = st.columns(2)
with first_row:
    batting_team = st.selectbox("Batting team", list(TEAM_CODES), index=3)
    current_score = st.number_input(
        "Current score",
        min_value=0,
        max_value=350,
        value=86,
        step=1,
    )
    wickets_left = st.number_input(
        "Wickets remaining",
        min_value=0,
        max_value=10,
        value=7,
        step=1,
    )
with second_row:
    bowling_options = [team for team in TEAM_CODES if team != batting_team]
    default_bowling = "Pakistan" if batting_team != "Pakistan" else "Australia"
    bowling_team = st.selectbox(
        "Bowling team",
        bowling_options,
        index=bowling_options.index(default_bowling),
    )
    balls_left = st.number_input(
        "Balls remaining",
        min_value=0,
        max_value=120,
        value=54,
        step=1,
    )
    last_five = st.number_input(
        "Runs in last five overs",
        min_value=0,
        max_value=150,
        value=42,
        step=1,
    )

balls_bowled = 120 - int(balls_left)
current_run_rate = float(current_score) * 6 / balls_bowled if balls_bowled else 0.0
model_input = pd.DataFrame(
    [
        {
            "city": DEFAULT_CITY_CODE,
            "bowling_team": TEAM_CODES[bowling_team],
            "batting_team": TEAM_CODES[batting_team],
            "balls_left": int(balls_left),
            "wickets_left": int(wickets_left),
            "crr": current_run_rate,
            "last_five": float(last_five),
            "current_score2": int(current_score),
        }
    ],
    columns=MODEL_FEATURES,
)

try:
    model_prediction = float(model.predict(model_input)[0])
except (ValueError, TypeError, AttributeError) as error:
    st.error(f"Prediction failed: {error}")
    st.stop()

predicted_score = max(int(current_score), int(round(model_prediction)))
st.divider()
st.metric("Predicted final score", f"{predicted_score} runs")
st.caption(
    f"Current run rate: {current_run_rate:.2f} · "
    f"Overs bowled: {balls_bowled // 6}.{balls_bowled % 6}"
)
