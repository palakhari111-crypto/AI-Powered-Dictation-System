import os
import requests
import streamlit as st

BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

def request(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token: headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(method, BASE + path, headers=headers, timeout=30, **kwargs)
    except requests.RequestException as exc:
        raise RuntimeError("Cannot connect to FastAPI. Start the backend first.") from exc
    if not response.ok:
        try: message = response.json().get("detail", response.text)
        except Exception: message = response.text
        raise RuntimeError(str(message))
    return response

def api(method, path, token=None, **kwargs):
    return request(method, path, token, **kwargs).json()
