from typing import Any, Callable
from colorist import BrightColor, bright_blue, bright_red
import random


def __counter(options):
    n = len(options)
    if n == 1:
        return f"{BrightColor.MAGENTA}1{BrightColor.OFF}"
    elif n in [2, 3]:
        return f"{BrightColor.MAGENTA}{', '.join(str(i) for i in range(1, n+1))}{BrightColor.OFF}"
    else:
        return f"{BrightColor.MAGENTA}1-{n}{BrightColor.OFF}"


def get_user_choice(options: list[str] | dict[str, Any] | str | None, msg: str | None = None, inpt: Callable = input) -> str:
    """
    Prompts the user to make a choice from a list of options.

    Args:
        options (list): A list of options from which the user can choose.
        msg (str, optional): The message to display before the list of options. Defaults to "Make your choice: ".

    Returns:
        str: The user's chosen option.

    Raises:
        IndexError: If the user enters an invalid choice.

    Examples:
        >>> options = ["apple", "banana", "orange"]
        >>> get_user_choice(options, msg="Choose an option:")
        Choose an option:
         1. apple
         2. banana
         3. orange
        Enter the number of your choice (leave empty for random choice) (3): 2
        'banana'
    """
    if isinstance(options, str) or (options is None and isinstance(msg, str)):
        return inpt(options or msg)

    opts: list = []
    vals: list = []
    if isinstance(options, dict):
        opts = list(options.keys())
        vals = list(options.values()) # type: ignore
    elif isinstance(options, list):
        opts = list(options)
        vals = list(options)

    if len(vals) == 1:
        return vals[0]

    if msg is not None:
        msg = msg.strip()
        msg = f"{msg}: " if not msg.endswith(':') else msg
        bright_blue(msg.strip())

    for i, option in enumerate(opts, start=1):
        print(f" {BrightColor.MAGENTA}{i}{BrightColor.OFF}. {option}")

    choice = str(inpt(f"{BrightColor.BLUE}Enter the number of your choice (leave empty for random choice){BrightColor.OFF} ({__counter(opts)}): ")).strip()

    if not choice:
        return random.choice(vals)
    else:
        try:
            return vals[int(choice) - 1]
        except ValueError:
            if choice in opts:
                return vals[opts.index(choice)]
            else:
                bright_red("Wrong option.")
                return get_user_choice(options=options, msg=msg)
