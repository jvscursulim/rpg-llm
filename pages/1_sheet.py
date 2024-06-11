import json

from pydantic import ValidationError

from schemas.character import Character
from pathlib import Path
import streamlit as st

from utils import (
    initialize_session_variables,
    response_generator,
    configure_model,
    set_api_key,
)

st.set_page_config(page_title="Role Play Gemini", page_icon=":game_die:", layout="wide")

initialize_session_variables(st.session_state)


st.title(":pencil: RPG Sheet :game_die:")
st.divider()

with st.sidebar:
    set_api_key(st.session_state)

model = configure_model(st.session_state)

if model:
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
            response = messages.chat_message("assistant").write_stream(
                response_generator(
                    chat_session=chat_session,
                    message=prompt,
                )
            )
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
        st.session_state.character_stats.generate_stats()

    col3, col4 = st.columns(2)

    with col3:
        strength = st.metric(
            label=":mechanical_arm: Strength (STR): ",
            value=st.session_state.character_stats.strength,
        )
        dexterity = st.metric(
            label=":running: Dexterity (DEX): ",
            value=st.session_state.character_stats.dexterity,
        )
        constitution = st.metric(
            label=":blue_heart: Constitution (CON): ",
            value=st.session_state.character_stats.constitution,
        )
    with col4:
        intelligence = st.metric(
            label=":brain: Intelligence (INT): ",
            value=st.session_state.character_stats.intelligence,
        )
        wisdom = st.metric(
            label=":book: Wisdom (WIS): ",
            value=st.session_state.character_stats.wisdom,
        )
        charisma = st.metric(
            label=":performing_arts: Charisma (CHA): ",
            value=st.session_state.character_stats.charisma,
        )

try:
    if save_button:
        char = Character(
            name=character_name,
            race=race,
            classe=character_class,
            background=background,
            hp=int(hp),
            ca=int(armor_class),
            stats=st.session_state.character_stats.model_dump(),  # type: ignore
        )

        save_path = Path("characters") / character_name
        save_path.mkdir(parents=True, exist_ok=True)

        with open(save_path / "character_sheet.json", "w") as file:
            json.dump(char.model_dump(), file, indent=4)

        st.success(body="Character saved with success!")

except ValidationError as e:
    error_msg = ""
    for err in e.errors():
        error_msg += f"**{err['loc'][0]}**: {err['msg']} \n\n"

    st.markdown(error_msg)


st.divider()
