import json
from typing import Any
import tiktoken
import json5 as json


def __get_encoding(model: str) -> tiktoken.core.Encoding:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return encoding

def __additional_tokens(model: str) -> tuple[int, int]:
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-1106",
        "gpt-4-1106-preview",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 4
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return __additional_tokens(model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return __additional_tokens(model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}. "
            "See https://github.com/openai/openai-python/blob/main/chatml.md for "
            "information on how messages are converted to tokens."
        )

    return tokens_per_message, tokens_per_name

def maximum_context_tokens(model: str) -> int:
    if model in {
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-1106"
    }:
        return 4096
    elif model in {
        "gpt-4-1106-preview"
    }:
        return 50000
    elif model == "gpt-4-32k-0613":
        return 31000
    else:
        return 4000

def calculate_tokens_for_string(value: str | None, model: str) -> int:
    if value is None:
        return 0

    if value == '':
        return 1

    encoding = __get_encoding(model)
    return len(encoding.encode(value))

def calculate_tokens_for(value: Any, model: str, with_name: bool = False) -> int:
    encoding = __get_encoding(model)
    tokens_per_message, tokens_per_name = __additional_tokens(model)

    num_tokens = 0
    num_tokens += tokens_per_message
    if with_name:
        num_tokens += tokens_per_name

    if isinstance(value, dict) or isinstance(value, list):
        value = json.dumps(value)

    num_tokens += len(encoding.encode(str(value))) if value else 0
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def _try_extract_usage_from_stream(stream_items: list[str]):
    try:
        res = json.loads(stream_items[-2])
        usage = res["usage"]
        return usage["prompt_tokens"], usage["completion_tokens"], usage["total_tokens"]
    except Exception:
        return None


def count_streaming_tokens(input_messages, response_string: str, model: str) -> tuple[int, int, int]:

    stream_items = response_string.split("data: ")

    stream_results = []
    for item in stream_items:
        if item and item.strip() != "[DONE]":
            stream_results.append(json.loads(item))
    text_for_count_completion = "".join(
        [item["choices"][0]["delta"].get("content", "") for item in stream_results if
         item.get("choices", [])])
    res = _try_extract_usage_from_stream(stream_items)
    if res is not None:
        prompt_tokens, completion_tokens, total_tokens = res
        return prompt_tokens, completion_tokens, total_tokens
    else:
        res = []
        for item in stream_items:
            if item and item.strip() != "[DONE]":
                res.append(json.loads(item))
        stream_items = res
        text_for_count_completion = "".join(
            [item["choices"][0]["delta"].get("content", "") for item in stream_items if
             item.get("choices", [])])
        prompt_tokens = calculate_tokens_for(input_messages, model)
        completion_tokens = calculate_tokens_for_string(text_for_count_completion, model)
        total_tokens = prompt_tokens + completion_tokens
        return prompt_tokens, completion_tokens, total_tokens
