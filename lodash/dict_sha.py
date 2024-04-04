import json
import hashlib


def dict_to_sha256(input_dict: dict) -> str:
    json_string = json.dumps(input_dict, sort_keys=True)  # sort keys for consistency of json strings
    sha256_hash = hashlib.sha256(json_string.encode()).hexdigest()
    return sha256_hash
