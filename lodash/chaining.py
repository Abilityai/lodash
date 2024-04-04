from typing import Callable
import logging


def chaining(item, logger: logging.Logger | None = None) -> Callable:
    logger = logger or logging.getLogger(__name__)

    def f(ff, *args, **kwargs) -> tuple[list, dict]:
        l = []
        d = {}

        result = ff(*args, **kwargs)

        if isinstance(result, dict):
            d = result
        else:
            l = [result]

        return l, d

    def chained_function(*x, **xx):
        r_args = [*x]
        r_kwargs = {**xx}

        if isinstance(item, str) or isinstance(item, int) or isinstance(item, float) or isinstance(item, bool):
            r_args = [item]
            r_kwargs = {}
        elif isinstance(item, dict):
            r_args = []
            r_kwargs = {**item}
        elif isinstance(item, Callable):
            local_args, local_kwargs = f(item, *r_args, **r_kwargs)
            r_args = local_args
            r_kwargs = {**local_kwargs}
        elif isinstance(item, tuple):
            local_args = []
            local_kwargs = {}

            for i in item:
                l_args, l_kwargs = f(chaining(i), *local_args, **local_kwargs)
                local_args = l_args
                local_kwargs = {**local_kwargs, **l_kwargs}

            r_args = local_args
            r_kwargs = {**local_kwargs}
        elif isinstance(item, list):
            local_args = []
            local_kwargs = {}

            for i in item:
                l_args, l_kwargs = f(chaining(i), *local_args, **local_kwargs)
                local_args = l_args
                local_kwargs = {**l_kwargs}

            r_args = local_args
            r_kwargs = {**local_kwargs}


        if len(r_args) == 1:
            return r_args[0]
        elif len(r_args) > 1:
            return r_args
        else:
            return r_kwargs

    return chained_function
