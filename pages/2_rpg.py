import os
from pathlib import Path

try:
    import torch

except ImportError as _:
    torch_not_present = True

import google.generativeai as genai
import numpy as np
import streamlit as st

from streamlit_mic_recorder import speech_to_text
from utils import (
    generate_image,
    process_user_input,
    GENERATION_CONFIG,
    SAFETY_SETTINGS,
    TEXT_MODEL,
    IMAGE_MODEL,
)

_ = Path("img/tmp").mkdir(parents=True, exist_ok=True)

if not torch_not_present:
    if not torch.cuda.is_available():
        st.warning(
            body="""A GPU was not detected by Pytorch! This implies that your PC will 
            take more time to produce images through stable diffusion model. 
            We recommend that users without NVIDIA GPU don't use image generation."""
        )

st.set_page_config(page_title="Role Play Gemini", page_icon=":game_die:", layout="wide")

if "api_key" not in st.session_state:
    st.session_state.api_key = None

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

if st.session_state.api_key:
    chat_session = model.start_chat(history=st.session_state.messages)

    with st.sidebar:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.write("Record your voice message: ")
            text_from_voice = speech_to_text(
                language="en",
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=False,
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
        enable_img_generation = st.toggle(label="Activate image generation", value=True)
        if enable_img_generation:
            img_prompt = st.text_area(label="Describe the image that you want to see:")
            generate_image_button = st.button(label="Generate image")

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

        if prompt:
            process_user_input(chat_session=chat_session, prompt=prompt)
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )

        if text_from_voice:
            process_user_input(chat_session=chat_session, prompt=text_from_voice)
            if enable_img_generation:
                prompt_summary = f"""Summary the following text using 77 tokens at maximum: {st.session_state.messages[-1]["parts"][0]}"""
                response = chat_session.send_message(prompt_summary)
                generate_image(
                    model=IMAGE_MODEL, prompt=response.text, show_user_prompt=False
                )

        if button_roll_d20:
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
