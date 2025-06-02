import os
import requests

def get_api_host():
    return os.getenv("API_HOST", "http://localhost:8000")

def get_headers(token):
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_get(path, token=None, params=None):
    url = f"{get_api_host()}{path}"
    return requests.get(url, headers=get_headers(token), params=params)

def api_post(path, token=None, params=None, json=None):
    url = f"{get_api_host()}{path}"
    return requests.post(url, headers=get_headers(token), params=params, json=json)

def api_put(path, token=None, json=None):
    url = f"{get_api_host()}{path}"
    return requests.put(url, headers=get_headers(token), json=json)

def api_delete(path, token=None, params=None):
    url = f"{get_api_host()}{path}"
    return requests.delete(url, headers=get_headers(token), params=params)
