from .string_manipulation import snake_to_camel, camel_to_snake, indent, snake_to_human, truncate_string, extract_domain, convert_links_in_text_to_html
from .array_manipulation import arguments_to_string, colorized_arguments_to_string, compact, compact_blank, uniq, flatten, fetch_element, get_element, split_options, wrap
from .dict_manipulation import dig, digwrite
from .load_all import load_all
from .get_user_choice import get_user_choice
from .chaining import chaining
from .remove_duplication import remove_duplication
from .mute_method import mute_method_unless
from .typing_ext import is_method, isnt_method, is_subclass, is_instance, type_to_str
from .tokens import calculate_tokens_for, calculate_tokens_for_string, maximum_context_tokens
from .cache import ttl_cache
from .lang import language_detect
from .llm_args import print_debug_start, print_debug_end
from .dict_sha import dict_to_sha256
from .data_schema_parser import data_schema_parser
from .gremlin_error_messages import GREMLIN_ERROR_MESSAGES, get_random_gremlin_error_message


def pprint(*args, **kwargs):
    print(arguments_to_string(*args, **kwargs))

__all__ = [
    "pprint",
    "compact",
    "get_element",
    "is_subclass",
    "is_instance",
    "ttl_cache",
    "compact_blank",
    "type_to_str",
    "uniq",
    "flatten",
    "remove_duplication",
    "arguments_to_string",
    "colorized_arguments_to_string",
    "snake_to_camel",
    "snake_to_human",
    "indent",
    "camel_to_snake",
    "load_all",
    "fetch_element",
    "split_options",
    "wrap",
    "get_user_choice",
    "chaining",
    "mute_method_unless",
    "is_method",
    "isnt_method",
    "calculate_tokens_for",
    "calculate_tokens_for_string",
    "truncate_string",
    "maximum_context_tokens",
    "language_detect",
    "print_debug_start",
    "print_debug_end",
    "dig",
    "digwrite",
    "dict_to_sha256",
    "data_schema_parser",
    "GREMLIN_ERROR_MESSAGES",
    "get_random_gremlin_error_message",
]
