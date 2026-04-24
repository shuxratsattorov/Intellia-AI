import json


class Serializer:
    @staticmethod
    def dumps(value):
        return json.dumps(value)

    @staticmethod
    def loads(value):
        return json.loads(value) if value else None