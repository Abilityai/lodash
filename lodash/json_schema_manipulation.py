

def add_types_to_json_schema(schema: dict) -> dict:
    """Adds image and document type definitions to a JSON schema."""

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

    def replace_types(obj):
        if isinstance(obj, dict):
            if obj.get("type") == "image":
                return {"$ref": "#/$defs/image"}
            elif obj.get("type") == "document":
                return {"$ref": "#/$defs/document"}
            return {k: replace_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_types(item) for item in obj]
        return obj

    return replace_types(schema)
