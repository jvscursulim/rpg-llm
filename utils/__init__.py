from schemas.character_stats import CharacterStats
from .model_config import GENERATION_CONFIG, SAFETY_SETTINGS, TEXT_MODEL, IMAGE_MODEL
from .utils import generate_image, process_user_input, response_generator

import streamlit as st
from typing import Any, Optional
import google.generativeai as genai


def initialize_session_variables(session_state: Any) -> None:
    if "api_key" not in session_state:
        session_state.api_key = None

    if "character_stats" not in session_state:
        session_state.character_stats = CharacterStats()

    if "chat_history" not in session_state:
        session_state.chat_history = []

    if "points_budget" not in session_state:
        session_state.points_budget = 29

    if "cost_table" not in session_state:
        points = [*range(8, 16)]
        cost_points = [*range(0, 8)]
        cost_points[-1] = cost_points[-1] + 2
        cost_points[-2] = cost_points[-2] + 1
        session_state.cost_table = {p: cp for p, cp in zip(points, cost_points)}


def configure_model(session_state: Any) -> Optional[Any]:
    if not session_state.api_key:
        with st.sidebar:
            st.warning(body="You must provide a Gemini API key!")

        return

    genai.configure(api_key=session_state.api_key)

    return genai.GenerativeModel(
        model_name=TEXT_MODEL,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
    )


def set_api_key(session_state: Any):
    api_key = st.text_input(label="Insert your Gemini API key here", type="password")
    if api_key:
        session_state.api_key = api_key
