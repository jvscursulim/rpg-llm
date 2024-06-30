from pathlib import Path

import json
import streamlit as st

st.set_page_config(page_title="Role Play Gemini", page_icon=":game_die:", layout="wide")

st.title(":male_mage: Characters :female_elf:")
st.divider()


try:
    options = [str(path) for path in Path("characters").glob("*") if path.is_dir()]

    character = st.selectbox(label="Character", options=options)

    with open(file=f"{character}/character_sheet.json", mode="r") as f:
        character_sheet = json.load(f)

    st.divider()

    st.header(":information_source: Character info")
    col1, col2 = st.columns([0.3, 0.7])

    with col1:
        st.write(f"Name: {character_sheet['name']}")
        st.write(f"Race: {character_sheet['race']}")
        st.write(f"Class: {character_sheet['classe']}")
        st.write(f"Background: {character_sheet['background']}")

    with col2:
        col3, col4 = st.columns([0.2, 0.8])
        with col3:
                strength = st.metric(
                    label=":mechanical_arm: Strength (STR): ",
                    value=character_sheet['stats']['strength'],
                    delta=character_sheet['stats']['strength_modifier'],
                )
                dexterity = st.metric(
                    label=":running: Dexterity (DEX): ",
                    value=character_sheet['stats']['dexterity'],
                    delta=character_sheet['stats']['dexterity_modifier'],
                )
                constitution = st.metric(
                    label=":blue_heart: Constitution (CON): ",
                    value=character_sheet['stats']['constitution'],
                    delta=character_sheet['stats']['constitution_modifier'],
                )
        with col4:
            intelligence = st.metric(
                label=":brain: Intelligence (INT): ",
                value=character_sheet['stats']['intelligence'],
                delta=character_sheet['stats']['intelligence_modifier'],
            )
            wisdom = st.metric(
                label=":book: Wisdom (WIS): ",
                value=character_sheet['stats']['wisdom'],
                delta=character_sheet['stats']['wisdom_modifier'],
            )
            charisma = st.metric(
                label=":performing_arts: Charisma (CHA): ",
                value=character_sheet['stats']['charisma'],
                delta=character_sheet['stats']['charisma_modifier'],
            )
except:
     st.warning("There is no character created!")

