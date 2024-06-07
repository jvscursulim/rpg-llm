import json
import os

import google.generativeai as genai
import numpy as np
import streamlit as st

from utils import (
    response_generator,
    GENERATION_CONFIG,
    SAFETY_SETTINGS,
    TEXT_MODEL,
)

st.set_page_config(page_title="Role Play Gemini", page_icon=":game_die:", layout="wide")
if "character_stats" not in st.session_state:
    st.session_state.character_stats = {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0,
    }

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title(":pencil: RPG Sheet :game_die:")
st.divider()

with st.sidebar:
    api_key = st.text_input(label="Insert your Gemini API key here", type="password")
    if api_key:
        st.session_state.api_key = api_key

if st.session_state.api_key:
    genai.configure(api_key=st.session_state.api_key)

    model = genai.GenerativeModel(
        model_name=TEXT_MODEL,
        safety_settings=SAFETY_SETTINGS,
        generation_config=GENERATION_CONFIG,
    )
else:
    with st.sidebar:
        st.warning(body="You must provide a Gemini API key!")

if st.session_state.api_key:
    chat_session = model.start_chat(history=st.session_state.chat_history)

    with st.sidebar:
        st.divider()

        messages = st.container(border=True)

        for idx, message in enumerate(st.session_state.chat_history):
            if idx > 0:
                if message["role"] == "user":
                    role = "user"
                else:
                    role = "ai"
                messages.chat_message(role).write(message["parts"][0])

        if prompt := st.chat_input(placeholder="Your message"):
            st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
            messages.chat_message("user").write(prompt)
            response = messages.chat_message("assistant").write_stream(response_generator(
                                    chat_session=chat_session,
                                    message=prompt,
                                ))
            st.session_state.chat_history.append({"role": "model", "parts": [response]})

col1, col2 = st.columns(2)

with col1:
    character_name = st.text_input(label="Character name: ")
    race = st.text_input(label="Race: ")
    character_class = st.text_input(label="Class: ")
    background = st.text_area(label="Background: ")
    save_button = st.button(label="Save character")

with col2:
    hp = st.number_input(label="Max HP: ", step=1)
    armor_class = st.number_input(label="Armor class: ", step=1)
    button_roll_dice = st.button(label="Roll 6 d20 for stats")
    if button_roll_dice:
        roll_dice_results = np.random.randint(low=1, high=21, size=6).tolist()
        character_stats = {
            "strength": roll_dice_results[0],
            "dexterity": roll_dice_results[1],
            "constitution": roll_dice_results[2],
            "intelligence": roll_dice_results[3],
            "wisdom": roll_dice_results[4],
            "charisma": roll_dice_results[5],
        }
        st.session_state.character_stats = character_stats
    col3, col4 = st.columns(2)
    with col3:
        strength = st.metric(
            label=":mechanical_arm: Strength (STR): ",
            value=st.session_state.character_stats["strength"],
        )
        dexterity = st.metric(
            label=":running: Dexterity (DEX): ",
            value=st.session_state.character_stats["dexterity"],
        )
        constitution = st.metric(
            label=":blue_heart: Constitution (CON): ",
            value=st.session_state.character_stats["constitution"],
        )
    with col4:
        intelligence = st.metric(
            label=":brain: Intelligence (INT): ",
            value=st.session_state.character_stats["intelligence"],
        )
        wisdom = st.metric(
            label=":book: Wisdom (WIS): ",
            value=st.session_state.character_stats["wisdom"],
        )
        charisma = st.metric(
            label=":performing_arts: Charisma (CHA): ",
            value=st.session_state.character_stats["charisma"],
        )

    if save_button:
        char_info_dict = {
            "name": character_name,
            "race": race,
            "class": character_class,
            "background": background,
            "hp": hp,
            "ca": armor_class,
            "stats": st.session_state.character_stats,
        }
        try:
            os.makedirs(name=f"characters/{character_name}")
        except ValueError as _e:
            st.write(_e)
        with open(f"characters/{character_name}/character_sheet.json", "w") as file:
            json.dump(char_info_dict, file)

if save_button:
    st.success(body="Character saved with success!")

st.divider()
