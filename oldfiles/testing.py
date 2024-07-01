import requests

url = "https://api.github.com/repos/Westpol/GeS-Ipad-Verwaltung/releases/latest"

response = requests.get(url)

print(response.json())
