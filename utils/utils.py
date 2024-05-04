import ollama
import time


def response_generator(text_model: str, messages: dict):
    """Creates a stream effect in the responde of
    the LLM.

    Args:
        text_model (str): The name of the LLM model.
        messages (dict): A dictionary with the message sent
        to the LLM.

    Yields:
        str: Generate the characteres of the LLM response.
    """

    response = ollama.chat(model=text_model, messages=messages)

    for word in response["message"]["content"].split():
        yield word + " "
        time.sleep(0.05)
