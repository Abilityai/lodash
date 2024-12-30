import uuid
from lodash.dict_manipulation import dig, dig_json_schema
import jsonschema
import copy


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

    # Update reference type definition
    if "reference" not in schema["$defs"]:
        schema["$defs"]["reference"] = {
            "oneOf": [
                {
                    "type": "object",
                    "properties": {
                        "$ref": {
                            "type": "string",
                        }
                    },
                    "required": ["$ref"]
                },
                {
                    "type": "null"
                }
            ]
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

    def check_value(value):
        if isinstance(value, dict) and "$ref" in value:
            ref_uid = value["$ref"]
            ref_path = find_path_by_uid(full_data, ref_uid)
            if ref_path and check_for_circular_reference(ref_path, source_path, full_data, visited):
                return True
        elif isinstance(value, dict):
            for v in value.values():
                if check_value(v):
                    return True
        elif isinstance(value, list):
            for item in value:
                if check_value(item):
                    return True
        return False

    # Check the target_data recursively
    if isinstance(target_data, dict):
        for value in target_data.values():
            if check_value(value):
                return True
    elif isinstance(target_data, list):
        for value in target_data:
            if check_value(value):
                return True

    visited.remove(target_path)
    return False


def resolve_references(obj, *, path_data, all_data, current_path="", _first_occurrence_paths=None):
    """Resolves references in a data structure by replacing $ref UIDs with paths.

    Args:
        obj: The object to resolve references in
        path_data: The data from the current path context
        all_data: The complete data structure
        current_path: The current path being processed
        _first_occurrence_paths: Dictionary tracking first occurrences of references

    Returns:
        The object with resolved references, with references in string format "$ref:path"
    """
    if _first_occurrence_paths is None:
        _first_occurrence_paths = {}

    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_uid = obj["$ref"]
            if ref_uid in _first_occurrence_paths:
                return f"$ref:{_first_occurrence_paths[ref_uid]}"

            target_path = find_path_by_uid(all_data, ref_uid)
            read_from_data = dig(path_data, target_path)
            read_from_all_data = dig(all_data, target_path)

            if read_from_data is not None and read_from_data == read_from_all_data:
                _first_occurrence_paths[ref_uid] = target_path
                return f"$ref:{_first_occurrence_paths[ref_uid]}"
            else:
                _first_occurrence_paths[ref_uid] = current_path
                read_from_all_data_copy = copy.deepcopy(read_from_all_data)
                result = resolve_references(
                    read_from_all_data_copy,
                    path_data=path_data,
                    all_data=all_data,
                    current_path=current_path,
                    _first_occurrence_paths=_first_occurrence_paths
                )
                return result
        else:
            for key, value in obj.items():
                obj[key] = resolve_references(
                    value,
                    path_data=path_data,
                    all_data=all_data,
                    current_path=f"{current_path}.{key}" if current_path else key,
                    _first_occurrence_paths=_first_occurrence_paths
                )

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = resolve_references(
                item,
                path_data=path_data,
                all_data=all_data,
                current_path=f"{current_path}[{i}]" if current_path else f"[{i}]",
                _first_occurrence_paths=_first_occurrence_paths
            )

    return obj



def validate_and_clean_references(all_data, data):
    """Recursively checks all references and nullifies those pointing to non-existent objects."""
    if isinstance(data, dict):
        for key, value in list(data.items()):  # Use list to avoid dictionary size change during iteration
            if isinstance(value, dict) and "$ref" in value:
                ref_uid = value["$ref"]
                ref_path = find_path_by_uid(all_data, ref_uid)
                if ref_path is None:
                    data[key] = None
            else:
                validate_and_clean_references(all_data=all_data, data=value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict) and "$ref" in item:
                ref_uid = item["$ref"]
                ref_path = find_path_by_uid(all_data, ref_uid)
                if ref_path is None:
                    data[i] = None
            else:
                validate_and_clean_references(all_data=all_data, data=item)
    return data



def validate_against_schema(data: dict | list, schema: dict) -> tuple[bool, str]:
    """Validates data against JSON schema.

    Args:
        data: The data to validate
        schema: The JSON schema to validate against

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    ok_message = "validation is passed"
    try:
        jsonschema.validate(data, schema)
        return True, ok_message
    except jsonschema.ValidationError as e:
        return False, str(e)
    except jsonschema.SchemaError as e:  # seems like an internal exception of jsonschema
        return True, ok_message


def extract_references(data) -> list[dict]:
    """
    Recursively extracts all references from the data.

    Args:
        data: The data to extract references from (can be dict, list, or primitive)

    Returns:
        list[dict]: List of reference objects (dicts with $ref key)
    """
    references = []

    if isinstance(data, dict):
        # If this is a reference, add it to the list
        if "$ref" in data:
            references.append(data)
        # Recursively check all values
        for value in data.values():
            references.extend(extract_references(value))

    elif isinstance(data, list):
        # Recursively check all items in the list
        for item in data:
            references.extend(extract_references(item))

    return references


def validate_json_schema_with_references(
    keypath: str,
    global_schema: dict,
    all_data: dict
) -> tuple[bool, str]:
    """
    Validates references and other data against the schema.

    Args:
        keypath (str): Path to the data to validate.
        global_schema (dict): The complete JSON schema used to validate objects.
        all_data (dict): Complete data object containing all possible reference targets.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    # Get schema and data for the keypath
    schema = dig_json_schema(global_schema, keypath)
    if schema is None:
        return False, f"Schema not found for path '{keypath}'"
    data = dig(all_data, keypath)
    if data is None:
        return False, f"Data not found at path '{keypath}'"

    # Extract all references from the data
    references = extract_references(data)
    if not references:
        schema = add_types_to_json_schema(schema)
        res = validate_against_schema(data, schema)
        return res
    else:
        for ref in references:
            ref_path = find_path_by_uid(all_data, ref["$ref"])
            is_valid, message = validate_json_schema_with_references(keypath=ref_path, global_schema=global_schema, all_data=all_data)
            if not is_valid:
                return False, message
    schema = add_types_to_json_schema(schema)
    return validate_against_schema(data, schema)
