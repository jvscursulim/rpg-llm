import json

from pydantic import ValidationError

from schemas.character import Character
from pathlib import Path
import numpy as np
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

        messages = st.container(border=True)

        for idx, message in enumerate(st.session_state.chat_history):
            if idx > 0:
                if message["role"] == "user":
                    role = "user"
                else:
                    role = "ai"
                messages.chat_message(role).write(message["parts"][0])

        st.write("Interact with Gemini")
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
    character_name = st.text_input(label="Name: ")
    race = st.text_input(label="Race: ")
    gender = st.text_input(label="Gender: ")
    character_class = st.text_input(label="Class: ")
    background = st.text_area(label="Background: ")
    save_button = st.button(label="Save character")

with col2:
    stats_options = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    ]
    option = st.selectbox(label="Stats", options=stats_options)
    number = st.number_input(label="Points", min_value=8, max_value=15, step=1)
    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            label="Points available on budget:", value=st.session_state.points_budget
        )
    with col4:
        with st.expander("Cost table"):
            for p, cp in st.session_state.cost_table.items():
                st.write(f"{p}: {cp} points")

    assigment_button = st.button(label="Assign stats value")

    if assigment_button:
        if option == "Strength":
            st.session_state.character_stats.strength = number
        elif option == "Dexterity":
            st.session_state.character_stats.dexterity = number
        elif option == "Constitution":
            st.session_state.character_stats.constitution = number
        elif option == "Intelligence":
            st.session_state.character_stats.intelligence = number
        elif option == "Wisdom":
            st.session_state.character_stats.wisdom = number
        elif option == "Charisma":
            st.session_state.character_stats.charisma = number
        if st.session_state.points_budget - st.session_state.cost_table[number] < 0:
            st.warning("You spent more points than you have in the budget!")
        else:
            st.session_state.points_budget = (
                st.session_state.points_budget - st.session_state.cost_table[number]
            )

    col5, col6 = st.columns(2)

    with col5:
        strength = st.metric(
            label=":mechanical_arm: Strength (STR): ",
            value=st.session_state.character_stats.strength,
            delta=(
                np.floor((st.session_state.character_stats.strength - 10) / 2)
                if st.session_state.character_stats.strength > 0
                else 0
            ),
        )
        dexterity = st.metric(
            label=":running: Dexterity (DEX): ",
            value=st.session_state.character_stats.dexterity,
            delta=(
                np.floor((st.session_state.character_stats.dexterity - 10) / 2)
                if st.session_state.character_stats.dexterity > 0
                else 0
            ),
        )
        constitution = st.metric(
            label=":blue_heart: Constitution (CON): ",
            value=st.session_state.character_stats.constitution,
            delta=(
                np.floor((st.session_state.character_stats.constitution - 10) / 2)
                if st.session_state.character_stats.constitution > 0
                else 0
            ),
        )
    with col6:
        intelligence = st.metric(
            label=":brain: Intelligence (INT): ",
            value=st.session_state.character_stats.intelligence,
            delta=(
                np.floor((st.session_state.character_stats.intelligence - 10) / 2)
                if st.session_state.character_stats.intelligence > 0
                else 0
            ),
        )
        wisdom = st.metric(
            label=":book: Wisdom (WIS): ",
            value=st.session_state.character_stats.wisdom,
            delta=(
                np.floor((st.session_state.character_stats.wisdom - 10) / 2)
                if st.session_state.character_stats.wisdom > 0
                else 0
            ),
        )
        charisma = st.metric(
            label=":performing_arts: Charisma (CHA): ",
            value=st.session_state.character_stats.charisma,
            delta=(
                np.floor((st.session_state.character_stats.charisma - 10) / 2)
                if st.session_state.character_stats.charisma > 0
                else 0
            ),
        )

try:
    if save_button:
        if st.session_state.points_budget >= 0:

            st.session_state.character_stats.calculate_stats_modifiers()
            hp = 10 + st.session_state.character_stats.constitution_modifier
            armor_class = 10 + st.session_state.character_stats.dexterity_modifier
            char = Character(
                name=character_name,
                race=race,
                gender=gender,
                classe=character_class,
                background=background,
                hp=hp,
                ca=armor_class,
                stats=st.session_state.character_stats.model_dump(),  # type: ignore
            )

            save_path = Path("characters") / character_name
            save_path.mkdir(parents=True, exist_ok=True)

            with open(save_path / "character_sheet.json", "w") as file:
                json.dump(char.model_dump(), file, indent=4)

            st.success(body="Character saved with success!")
        else:
            st.warning(
                body="You can't save the character! That's because your stats assignment overcome the budget."
            )

except ValidationError as e:
    error_msg = ""
    for err in e.errors():
        error_msg += f"**{err['loc'][0]}**: {err['msg']} \n\n"

    st.markdown(error_msg)


st.divider()
