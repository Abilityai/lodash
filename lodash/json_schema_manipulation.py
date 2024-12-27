import uuid
from lodash.dict_manipulation import dig

def add_types_to_json_schema(schema: dict) -> dict:
    """Adds image, document, and reference type definitions to a JSON schema."""

    # Add the type definitions if they don't exist
    if "$defs" not in schema:
        schema["$defs"] = {}

    # Add image type definition
    if "image" not in schema["$defs"]:
        schema["$defs"]["image"] = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["image"]
                },
                "url": {
                    "type": "string",
                    "format": "uri"
                }
            },
            "required": ["type", "url"]
        }

    # Add document type definition
    if "document" not in schema["$defs"]:
        schema["$defs"]["document"] = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["document"]
                },
                "contents": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "images": {
                    "type": "array",
                    "items": {
                        "$ref": "#/$defs/image"
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "required": ["type", "contents"]
        }

    # Add reference type definition
    if "reference" not in schema["$defs"]:
        schema["$defs"]["reference"] = {
            "type": "object",
            "properties": {
                "$ref": {
                    "type": "string",
                }
            },
            "required": ["$ref"]
        }

    def replace_types(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "image":
                return {"$ref": "#/$defs/image"}
            elif obj.get("type") == "document":
                return {"$ref": "#/$defs/document"}
            elif obj.get("type") == "reference":
                return {"$ref": "#/$defs/reference"}
            return {k: replace_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_types(item) for item in obj]
        return obj

    return replace_types(schema)

def add_uid_to_dict(obj):
    """Recursively adds a $uid field with a random UUID to all dictionaries."""
    if isinstance(obj, dict):
        if "$uid" not in obj:
            obj["$uid"] = str(uuid.uuid4())
        for k, v in obj.items():
            add_uid_to_dict(v)
    elif isinstance(obj, list):
        for item in obj:
            add_uid_to_dict(item)
    return obj


def find_path_by_uid(obj, target_uid, current_path=""):
    """Recursively searches for a specific $uid and returns its keypath.

    Args:
        obj: The dictionary or list to search through
        target_uid: The $uid value to find
        current_path: The accumulated path (used in recursion)

    Returns:
        str: The keypath to the object with the matching $uid, or None if not found
    """
    if isinstance(obj, dict):
        if obj.get("$uid") == target_uid:
            return current_path

        for key, value in obj.items():
            # Build the new path segment
            new_path = f"{current_path}.{key}" if current_path else key
            # Skip the $uid key itself to avoid unnecessary recursion
            if key != "$uid":
                result = find_path_by_uid(value, target_uid, new_path)
                if result is not None:
                    return result

    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            # For lists, use array notation [index]
            new_path = f"{current_path}[{index}]" if current_path else f"[{index}]"
            result = find_path_by_uid(item, target_uid, new_path)
            if result is not None:
                return result
    return None


def remove_uids(obj):
    if isinstance(obj, dict):
        obj = {k: v for k, v in obj.items() if k != "$uid"}
        return {k: remove_uids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [remove_uids(item) for item in obj]
    return obj

def clean_uids(func):
    """Decorator that removes $uid keys from the returned dictionary."""

    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        res = remove_uids(result)
        return res

    return wrapper


def check_for_circular_reference(target_path: str, source_path: str, full_data: dict, visited=None) -> bool:
    """
    Check if adding a reference would create a circular dependency.
    Returns True if a circular reference is detected.

    Args:
        target_path: Path to check for references
        source_path: Original path where new reference will be added
        full_data: Complete data structure to check against
        visited: Set of already visited paths (internal use for recursion)
    """
    if visited is None:
        visited = set()

    # Split paths into components for more accurate checking
    target_parts = target_path.split('.')
    source_parts = source_path.split('.')

    # Check if the target path is a parent or equal to the source path
    if len(target_parts) <= len(source_parts):
        if all(t == s for t, s in zip(target_parts, source_parts)):
            return True

    if target_path in visited:
        return True

    visited.add(target_path)

    # Use dig to get target data from the provided full_data
    target_data = dig(full_data, target_path)
    if not target_data:
        return False

    # Recursively check all references in the target
    if isinstance(target_data, dict):
        for value in target_data.values():
            if isinstance(value, str) and value.startswith("$ref:"):
                ref_uid = value.removeprefix("$ref:")
                # Find the actual keypath for this UUID using the provided full data
                ref_path = find_path_by_uid(full_data, ref_uid)
                if ref_path and check_for_circular_reference(ref_path, source_path, full_data, visited):
                    return True

    visited.remove(target_path)
    return False

