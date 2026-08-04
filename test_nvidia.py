import requests


API_KEY = "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"


url = "https://integrate.api.nvidia.com/v1/chat/completions"


headers = {
    "Authorization": f"Bearer {API_KEY}",
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

    "stream": False

}



response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=60
)


print(response.status_code)
print(response.text)