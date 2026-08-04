import requests


url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": "Bearer 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",
    "Accept": "application/json",
    "Content-Type": "application/json"
}


payload = {
    "model": "moonshotai/kimi-k2.6",
    "messages": [
        {
            "role": "user",
            "content": "Merhaba"
        }
    ],
    "max_tokens": 100,
    "temperature": 1,
    "top_p": 1,
    "seed": 0,
    "stream": False
}


r = requests.post(
    url,
    headers=headers,
    json=payload
)


print(r.status_code)
print(r.text)