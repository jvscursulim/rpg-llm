import json
import os
import torch

import datetime as dt
import google.generativeai as genai
import numpy as np
import streamlit as st

from streamlit_mic_recorder import speech_to_text
from utils import (
    response_generator,
    generate_image,
    GENERATION_CONFIG,
    SAFETY_SETTINGS,
    TEXT_MODEL,
    IMAGE_MODEL,
)


with open(file="secrets/google_api_key.json", mode="r") as file:
    api_key = json.load(file)["api_key"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name=TEXT_MODEL,
    safety_settings=SAFETY_SETTINGS,
    generation_config=GENERATION_CONFIG,
)

try:
    os.makedirs("img/tmp", exist_ok=True)
except ValueError as _e:
    pass

if torch.cuda.is_available():
    device = "cuda"
else:
    st.warning(
        body="A GPU was not detected by Pytorch! This implies that your PC will take more time to produce images through stable diffusion model. We recommend that users without NVIDIA GPU don't use image generation."
    )
    device = "cpu"

st.set_page_config(page_title="RPG GPT", page_icon=":game_die:", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
    initial_prompt = """Hi Gemini, I would like that behave like a RPG master, you should to follow Dungeons and Dragons rules.
    When the user says something that sounds like an action you must to request that the user rolls a d20 and you only have to tell the result of the action after that you receive the dice result.
    You have to be very creative and you need to describe very well the story.
    At the end of the paragraph you have to write a summary of what you described as a prompt to be used on a text to image model, this summary must have at maximum 77 tokens
    and also must be between *"""
    st.session_state.messages.append({"role": "user", "parts": [initial_prompt]})
    chat_session = model.start_chat(history=st.session_state.messages)
else:
    chat_session = model.start_chat(history=st.session_state.messages)

if "images_descriptions" not in st.session_state:
    st.session_state.images_descriptions = []

if "images_paths" not in st.session_state:
    st.session_state.images_paths = []

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


col1, col2 = st.columns(2)

with col1:

    if prompt := st.chat_input(placeholder="I'm going on an adventure!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            response = st.write_stream(
                response_generator(
                    chat_session=chat_session,
                    message=prompt,
                    images_descriptions=st.session_state.images_descriptions,
                )
            )
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": [response]})
        img_prompt = st.session_state.images_descriptions[-1]
        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            img = generate_image(model=IMAGE_MODEL, device=device, prompt=img_prompt)
            timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img.save(f"img/tmp/{timestamp}.png")
            st.image(np.array(img))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": timestamp + ".png"})

    st.write("Record your voice message: ")
    prompt = speech_to_text(
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
    if prompt:
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            response = st.write_stream(
                response_generator(
                    chat_session=chat_session,
                    message=prompt,
                    images_descriptions=st.session_state.images_descriptions,
                )
            )
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": [response]})
        img_prompt = st.session_state.images_descriptions[-1]
        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            img = generate_image(model=IMAGE_MODEL, device=device, prompt=img_prompt)
            timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img.save(f"img/tmp/{timestamp}.png")
            st.image(np.array(img))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": timestamp + ".png"})

with col2:
    button_roll_d20 = st.button(label="Roll d20")

with col1:
    if button_roll_d20:
        d20_result = np.random.randint(low=1, high=21)
        prompt = f"The result of my d20 was {d20_result}"
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            response = st.write_stream(
                response_generator(
                    chat_session=chat_session,
                    message=prompt,
                    images_descriptions=st.session_state.images_descriptions,
                )
            )
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": [response]})
        img_prompt = st.session_state.images_descriptions[-1]
        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            img = generate_image(model=IMAGE_MODEL, device=device, prompt=img_prompt)
            timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img.save(f"img/tmp/{timestamp}.png")
            st.image(np.array(img))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": timestamp + ".png"})

with col2:
    img_prompt = st.text_area(label="Describe the image that you want to see:")
    generate_image_button = st.button(label="Generate image")

with col1:
    if generate_image_button:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": img_prompt})
        with st.chat_message("user"):
            # Display user message in chat message container
            st.markdown(img_prompt)
        # Display assistant response in chat message container
        with st.chat_message("model", avatar="ai"):
            img = generate_image(model=IMAGE_MODEL, device=device, prompt=img_prompt)
            timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img.save(f"img/tmp/{timestamp}.png")
            st.image(np.array(img))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "model", "parts": timestamp + ".png"})
