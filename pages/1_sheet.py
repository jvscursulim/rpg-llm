import json
import os
import numpy as np
import streamlit as st

st.set_page_config(page_title="RPG GPT", page_icon=":game_die:", layout="wide")
if "character_stats" not in st.session_state:
    st.session_state.character_stats = character_stats = {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0,
    }

st.title(":pencil: RPG Sheet :game_die:")
st.divider()

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
        st.success(body="Character saved with success!")

st.divider()
