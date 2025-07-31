import json

def format_response(data):
    try:
        json.dumps(data)
        return data
    except Exception:
        return str(data)
