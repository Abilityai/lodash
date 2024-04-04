import re
from colorist import BrightColor, Effect
from .string_manipulation import indent as string_indent


def print_debug_start(logger, before_msg: str = 'Calling GPT', **kwargs):
    def ss(s):
        regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        s1 = regex.sub('', s)
        return len(regex.sub('', s1))

    def q(i=1, s='·'):
        return f'{BrightColor.BLACK}{s}{BrightColor.OFF}'

    logger.info(f' {BrightColor.BLACK}⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯ {before_msg} ⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯{BrightColor.OFF}')
    def print_recursive(d, indent=''):
        i = 0

        if isinstance(d, dict):
            iterator = d.items()
        elif isinstance(d, (list, tuple)):
            iterator = enumerate(d)
        else:
            logger.info(string_indent(d, indent))
            return

        for key, value in iterator:
            if isinstance(value, dict):
                if len(value) > 0:
                    logger.info(f"{indent}{BrightColor.GREEN}{key}{BrightColor.OFF}:")
                    print_recursive(value, indent + q(2))
            elif isinstance(value, (list, tuple)):
                if len(value) > 0:
                    if all(isinstance(x, str) for x in value):
                        logger.info(f"{indent}{BrightColor.GREEN}{key}{BrightColor.OFF}: {', '.join(value)}")
                    else:
                        logger.info(
                            f"{indent}{BrightColor.GREEN}{key}{BrightColor.OFF}")
                        for i, item in enumerate(value):
                            prfx = f"{indent}{str(i).rjust(3, ' ')}:"
                            logger.info(q(1, prfx))
                            print_recursive(item, indent + (q(1) * (ss(prfx) // 2)))
            elif isinstance(value, str) and f'\n' in value:
                logger.info(f"{indent}{BrightColor.GREEN}{key}{BrightColor.OFF}:")
                logger.info(string_indent(value, indent + q(2)))
            else:
                logger.info(f"{indent}{BrightColor.GREEN}{key}{BrightColor.OFF}: {value}")
            i += 1

    sorted_keys = []
    if 'messages' in kwargs:
        sorted_keys.append('messages')
    if 'tools' in kwargs:
        sorted_keys.append('tools')
    sorted_keys += [k for k in kwargs.keys() if k not in ('messages', 'tools')]

    sorted_dict = {k: kwargs[k] for k in sorted_keys}
    print_recursive(sorted_dict, indent=f"{BrightColor.BLACK} ∣{BrightColor.OFF}" + q(1))
    logger.info(f'{BrightColor.BLACK}  ⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯{BrightColor.OFF}')


def print_debug_end(logger, result):
    if hasattr(result, 'usage'):
        usage = result.usage
        logger.info(string_indent(
            f"tokens: "
            f"{BrightColor.BLACK}completion={Effect.BOLD}{getattr(usage, 'completion_tokens', 0)}{Effect.BOLD_OFF},{BrightColor.OFF} "
            f"{BrightColor.BLACK}prompt={Effect.BOLD}{getattr(usage, 'prompt_tokens', 0)}{Effect.BOLD_OFF},{BrightColor.OFF} "
            f"{BrightColor.BLACK}total={Effect.BOLD}{getattr(usage, 'total_tokens', 0)}{Effect.BOLD_OFF}{BrightColor.OFF}",
            f'{BrightColor.BLACK} ∣·{BrightColor.OFF}'
        ))

    logger.info(f'{BrightColor.BLACK}  ⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯{BrightColor.OFF}')

    if hasattr(result, 'choices'):
        logger.info(string_indent(str(result.choices[0].message), f'{BrightColor.BLACK} ∣·{BrightColor.OFF}'))
    else:
        logger.info(string_indent(str(result), f'{BrightColor.BLACK} ∣·{BrightColor.OFF}'))

    logger.info(f'{BrightColor.BLACK} ∟⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯{BrightColor.OFF}')
