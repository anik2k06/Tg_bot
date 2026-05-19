import requests

BOT_TOKEN = input ("YOUR_BOT_TOKEN")
CHAT_ID = input("YOUR_CHAT_ID")
message = input("YOUR_PROMPT")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload)
print(response.json())

