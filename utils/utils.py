import time
import torch

import datetime as dt
import google.generativeai as genai
import numpy as np
import streamlit as st

from diffusers import DiffusionPipeline

def response_generator(chat_session: genai.ChatSession,
                       message: dict):
    """Creates a stream effect in the responde of
    the LLM.

    Args:
        text_model (str): The name of the LLM model.
        messages (dict): A dictionary with the message sent
        to the LLM.

    Yields:
        str: Generate the characteres of the LLM response.
    """
    
    response = chat_session.send_message(message)

    for word in response.text.split(" "):
        yield word + " "
        time.sleep(0.05)

def generate_image(model: str, prompt: str, show_user_prompt: bool=False) -> None:
    """Generates an image from a user prompt.

    Args:
        model (str): The name of the image model.
        prompt (str): A sequence of tokens that describe
        the image to be genereted
        show_user_prompt (bool): . Defaults to False.

    """

    pipeline = DiffusionPipeline.from_pretrained(
                model, torch_dtype=torch.float16, use_safetensors=True
            )
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    
    pipeline.to(device)
    if show_user_prompt:
        st.session_state.messages.append({"role": "user", "parts": prompt})
    img = pipeline(prompt).images[0]

    # Display user message in chat message container
    if show_user_prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("model", avatar="ai"):
        timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        img.save(f"img/tmp/{timestamp}.png")
        st.image(np.array(img))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "model", "parts": timestamp + ".png"})

def process_user_input(chat_session, prompt: str) -> None:
    """Processes user input

    Args:
        chat_session: A Gemini chat session.
        prompt (str): A sequence of tokens that
        represents user command.
    """

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
            )
        )
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "model", "parts": [response]})
