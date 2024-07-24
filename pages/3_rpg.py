from pathlib import Path

try:
    import torch

    torch_not_present = False

except ImportError as _:
    torch_not_present = True

import json
import numpy as np
import streamlit as st

from streamlit_mic_recorder import speech_to_text
from utils import (
    configure_model,
    generate_image,
    process_user_input,
    IMAGE_MODEL,
    set_api_key,
)

_ = Path("img/tmp").mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Role Play Gemini", page_icon=":game_die:", layout="wide")

if not torch_not_present:
    if not torch.cuda.is_available():
        st.warning(
            body="""A GPU was not detected by Pytorch! This implies that your PC will 
            take more time to produce images through stable diffusion model. 
            We recommend that users without NVIDIA GPU don't use image generation."""
        )

if "api_key" not in st.session_state:
    st.session_state.api_key = None

with st.sidebar:
    set_api_key(st.session_state)

model = configure_model(st.session_state)

if "messages" not in st.session_state:
    st.session_state.messages = []
    setup_prompt = """Hi Gemini, I would like that you behave like a RPG master, 
    you should to follow Dungeons and Dragons rules. When the user says something 
    that sounds like an action you must to request that the user rolls a d20 and 
    you only have to tell the result of the action after that you receive the dice result.
    You have to be very creative and you need to describe very well the story."""
    st.session_state.messages.append({"role": "user", "parts": [setup_prompt]})
    initial_message = """Hello adventurer, I'm Gemini and I'll be your RPG master!
    Tell me, what kind of adventure do you want to play today?"""
    st.session_state.messages.append({"role": "model", "parts": [initial_message]})

if "images_paths" not in st.session_state:
    st.session_state.images_paths = []

st.title(":crossed_swords: :male_mage: Role Play Gemini :elf: :game_die:")

if model:
    chat_session = model.start_chat(history=st.session_state.messages)

    with st.sidebar:
        with st.expander(label="Save or load adventures:"):
            filename = st.text_input(label="Filename:")
            save_button = st.button(label="Save")
            try:
                options_list = [
                    str(path)
                    for path in Path("adventures").glob("*.json")
                    if path.is_file()
                ]
                adv_option = st.selectbox(
                    label="Choose an adventure", options=options_list
                )
            except:
                st.warning("There is no adventure saved!")
            load_button = st.button(label="Load")
            if save_button:
                save_path = Path("adventures")
                save_path.mkdir(parents=True, exist_ok=True)

                with open(save_path / f"{filename}.json", "w") as file:
                    json.dump(st.session_state.messages, file, indent=4)

                st.success(body="Adventure saved with success!")
            if load_button:
                with open(file=f"{adv_option}", mode="r") as f:
                    adventure = json.load(f)

                st.session_state.messages = adventure
                st.success(body="Adventure loaded with success!")
        with st.expander(label="Choose a character:"):
            try:
                options = [
                    str(path) for path in Path("characters").glob("*") if path.is_dir()
                ]

                character = st.selectbox(label="Character", options=options)

                with open(file=f"{character}/character_sheet.json", mode="r") as f:
                    character_sheet = json.load(f)

                prompt_character = f"""My character name is {character_sheet['name']}. My character is a {character_sheet['gender']} {character_sheet['race']} {character_sheet['classe']}.\n
                Character stats:\n
                HP: {character_sheet['hp']}\n
                Armor class: {character_sheet['ca']}\n
                Strength: {character_sheet['stats']['strength']} (modifier {character_sheet['stats']['strength_modifier']})\n
                Dexterity: {character_sheet['stats']['dexterity']} (modifier {character_sheet['stats']['dexterity_modifier']})\n
                Constitution: {character_sheet['stats']['constitution']} (modifier {character_sheet['stats']['constitution_modifier']})\n
                Intelligence: {character_sheet['stats']['intelligence']} (modifier {character_sheet['stats']['intelligence_modifier']})\n
                Wisdom: {character_sheet['stats']['wisdom']} (modifier {character_sheet['stats']['wisdom_modifier']})\n
                Charisma: {character_sheet['stats']['charisma']} (modifier {character_sheet['stats']['charisma_modifier']})\n
                Background story: {character_sheet['background']}
                """
            except:
                st.warning("There is no character created!")
            char_button = st.button(label="Use this character")
        with st.expander(label="AI companion"):
            try:
                options_chars = [
                    str(path) for path in Path("characters").glob("*") if path.is_dir()
                ]

                ai_character = st.selectbox(label="AI Character", options=options_chars)

                with open(file=f"{ai_character}/character_sheet.json", mode="r") as f:
                    character_sheet = json.load(f)

                prompt_ai_character = f"""You must act like a RPG companion, so your messages should be interactions with the human player and the other LLM that is the RPG Master.
                Your name is {character_sheet['name']} and you are a {character_sheet['gender']} {character_sheet['race']} {character_sheet['classe']}.\n
                Character stats:\n
                HP: {character_sheet['hp']}\n
                Armor class: {character_sheet['ca']}\n
                Strength: {character_sheet['stats']['strength']} (modifier {character_sheet['stats']['strength_modifier']})\n
                Dexterity: {character_sheet['stats']['dexterity']} (modifier {character_sheet['stats']['dexterity_modifier']})\n
                Constitution: {character_sheet['stats']['constitution']} (modifier {character_sheet['stats']['constitution_modifier']})\n
                Intelligence: {character_sheet['stats']['intelligence']} (modifier {character_sheet['stats']['intelligence_modifier']})\n
                Wisdom: {character_sheet['stats']['wisdom']} (modifier {character_sheet['stats']['wisdom_modifier']})\n
                Charisma: {character_sheet['stats']['charisma']} (modifier {character_sheet['stats']['charisma_modifier']})\n
                Background story: {character_sheet['background']}
                """
            except:
                st.warning("There is no character created!")
            ai_companion_action_button = st.button(label="AI companion action")
        enable_img_generation = st.toggle(
            label="Activate image generation", value=False
        )
        if enable_img_generation:
            with st.expander(label="Image generation"):
                img_prompt = st.text_area(
                    label="Describe the image that you want to generate:"
                )
                generate_image_button = st.button(label="Generate image")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Voice input: ")
            text_from_voice = speech_to_text(
                language="en",
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=True,
                use_container_width=False,
                callback=None,
                args=(),
                kwargs={},
                key=None,
            )
        with col2:
            st.write("Roll a d20")
            button_roll_d20 = st.button(label=":game_die:")

        prompt = st.chat_input(placeholder="What do you want to do adventurer?")

    with st.container(border=True):

        for idx, message in enumerate(st.session_state.messages):
            if idx > 0:
                if message["role"] == "user":
                    role = "user"
                else:
                    role = "ai"
                with st.chat_message(role):
                    if message["parts"][-3:] == "png":
                        st.image(f"img/tmp/{message['parts']}")
                    else:
                        st.markdown(message["parts"][0])

        if prompt or text_from_voice:
            if prompt:
                process_user_input(chat_session=chat_session, prompt=prompt)
            elif text_from_voice:
                process_user_input(chat_session=chat_session, prompt=text_from_voice)
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )

        if char_button:
            process_user_input(chat_session=chat_session, prompt=prompt_character)
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )

        if button_roll_d20:
            with st.chat_message("user"):
                st.audio(
                    "audio/dice_roll_sound.m4a",
                    format="audio/mpeg",
                    loop=False,
                    autoplay=True,
                )
            d20_result = np.random.randint(low=1, high=21)
            prompt = f"The result of my d20 was {d20_result}"
            process_user_input(chat_session=chat_session, prompt=prompt)
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )

        if enable_img_generation:
            if generate_image_button:
                generate_image(
                    model=IMAGE_MODEL, prompt=img_prompt, show_user_prompt=True
                )

        if ai_companion_action_button:
            model_companion = configure_model(st.session_state)
            chat_companion_session = model_companion.start_chat(
                history=[{"role": "user", "parts": [prompt_ai_character]}]
            )
            prompt_ai_companion = f"""Take an action based on the following messages:
                                    '{st.session_state.messages[-2]['parts'][0]}'\n

                                    '{st.session_state.messages[-1]['parts'][0]}'
                                    """
            process_user_input(
                chat_session=chat_companion_session,
                prompt=prompt_ai_companion,
                ai_companion=True,
            )
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )
