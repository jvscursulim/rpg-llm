import time
import torch

import google.generativeai as genai

from diffusers import DiffusionPipeline
from PIL import Image


def response_generator(chat_session: genai.ChatSession,
                       message: dict,
                       images_descriptions: list):
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
    try:
        images_descriptions.append(response.text.split("*")[1])
    except:
        pass

    for word in response.text.split("*")[0].split():
        yield word + " "
        time.sleep(0.05)

def generate_image(model: str, device: str, prompt: str) -> Image:

    pipeline = DiffusionPipeline.from_pretrained(
                model, torch_dtype=torch.float16, use_safetensors=True
            )
    pipeline.to(device)
    img = pipeline(prompt).images[0]

    return img
