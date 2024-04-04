from typing import List, Tuple

import os
import glob


def __get_relative_path(root_dir: str, path: str) -> str:
    """
    Creates a new folder in the specified root directory.
    """
    if ".." in path:
        raise ValueError(
            f"'{path}' should not contain '..' to not be able to create a folder outside the root directory")

    root_dir = os.path.abspath(root_dir)

    full_path = os.path.join(root_dir, path)

    if not full_path.startswith(root_dir):
        raise ValueError("folder_path should not go beyond root_dir")

    return full_path


def read_file(root_dir: str, file_path: str) -> str | None:
    """
    Reads the content of the specified file.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=file_path)

    try:
        with open(full_path, 'r') as file:
            content = file.read()

        return content
    except FileNotFoundError:
        pass

def write_file(root_dir: str, file_path: str, content: str) -> str:
    """
    Writes the specified content to the specified file.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=file_path)

    with open(full_path, 'w') as file:
        file.write(content)

    return full_path

def delete_file(root_dir: str, file_path: str) -> str:
    """
    Deletes the specified file.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=file_path)
    try:
        os.rmdir(full_path) if os.path.isdir(full_path) else os.remove(full_path)
    except FileNotFoundError:
        return f"File '{full_path}' not found"
    except OSError as error:
        return f"File '{full_path}' can not be removed"

    return f"File '{full_path}' has been deleted"

def list_directory(root_dir: str, dir_path: str) -> list:
    """
    Lists all files and subdirectories in the specified directory.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=dir_path)
    return os.listdir(full_path)

def file_exists(root_dir: str, file_path: str) -> bool:
    """
    Searches for the specified file in the given directory.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=file_path)

    return os.path.exists(full_path)

def create_folder(root_dir: str, folder_path: str) -> str:
    """
    Creates a new folder in the specified root directory.
    """
    full_path = __get_relative_path(root_dir=root_dir, path=folder_path)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def search_content(root_dir: str, content: str, folder_path: str, page: int) -> List[Tuple[str, List[str]]]:
    """
    Searches for the specified content in the given directory.
    Returns the dictionary with file_path and text around the specified found content +/- 5 lines.
    Found 5 matches scoped by the page number.
    """
    root_dir = __get_relative_path(
        root_dir=root_dir, path=folder_path)
    all_files = [f for f in glob.glob(root_dir + '/**', recursive=True)
                  if not any(part.startswith(('.', '__')) for part in f.split(os.sep))]

    matches = []
    for file_path in all_files:
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for index, line in enumerate(lines):
                    if content in line:
                        matches.append((
                            file_path,
                            f"\n".join(lines[max(0, index - 5):index + 6])
                        ))

    start = page * 5
    end = (page + 1) * 5
    return matches[start:end]
