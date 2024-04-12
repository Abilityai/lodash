from genson import SchemaBuilder


def data_schema_parser(*data):
    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})
    for item in data:
        builder.add_object(item)
    return builder.to_schema()
