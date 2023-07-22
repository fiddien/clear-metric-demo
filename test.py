import requests

sents = {
    'sent': "I have a dream"
}

url = "http://localhost:9696/inference"
r = requests.post(url, json=sents)
print(r.text.strip())