import ollama
import os
import torch

import datetime as dt
import numpy as np
import streamlit as st

from diffusers import DiffusionPipeline
from utils import response_generator

TEXT_MODEL = "llama3"
IMAGE_MODEL = "runwayml/stable-diffusion-v1-5"

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
    initial_prompt = """You must only behave like a RPG master and you are very creative.
    The RPG adventure must follow Dungeons and Dragons rules
    and for some actions you must require that the player roll a d20."""
    st.session_state.messages.append({"role": "user", "content": initial_prompt})
    _ = ollama.chat(model=TEXT_MODEL, messages=[st.session_state.messages[-1]])

for idx, message in enumerate(st.session_state.messages):
    if idx > 0:
        with st.chat_message(message["role"]):
            if message["content"][-3:] == "png":
                st.image(f"img/tmp/{message['content']}")
            else:
                st.markdown(message["content"])

col1, col2 = st.columns(2)

with col1:
    if prompt := st.chat_input("I'm going on an adventure!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(
                response_generator(
                    text_model=TEXT_MODEL, messages=[st.session_state.messages[-1]]
                )
            )
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    button_roll_d20 = st.button(label="Roll d20")

with col1:
    if button_roll_d20:
        d20_result = np.random.randint(low=1, high=21)
        prompt = f"The result of my d20 was {d20_result}"
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(
                response_generator(
                    text_model=TEXT_MODEL, messages=[st.session_state.messages[-1]]
                )
            )
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    img_prompt = st.text_area(label="Describe the image that you want to see:")
    generate_image_button = st.button(label="Generate image")

with col1:
    if generate_image_button:
        pipeline = DiffusionPipeline.from_pretrained(
            IMAGE_MODEL, torch_dtype=torch.float16, use_safetensors=True
        )
        pipeline.to(device)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": img_prompt})
        with st.chat_message("user"):
            # Display user message in chat message container
            st.markdown(img_prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            img = pipeline(img_prompt).images[0]
            timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            img.save(f"img/tmp/{timestamp}.png")
            st.image(np.array(img))
        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": timestamp + ".png"}
        )
