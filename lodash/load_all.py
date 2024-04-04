import os
import pkgutil
import importlib
from .string_manipulation import snake_to_camel

def load_all(current_name, current_file, globals_map) -> list[str]:
    export = []
    current_dir = os.path.dirname(current_file)

    for _, module_name, _ in pkgutil.iter_modules([current_dir]):
        camel_case_name = snake_to_camel(module_name)
        export.append(camel_case_name)
        module = importlib.import_module(f".{module_name}", current_name)
        globals_map()[camel_case_name] = module

    return export
