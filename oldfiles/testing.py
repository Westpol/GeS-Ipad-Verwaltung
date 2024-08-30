import requests
import os
import time
import sys

time.sleep(5)
url = "https://api.github.com/repos/Westpol/GeS-Ipad-Verwaltung/releases/latest"

response = requests.get(url)

print(response.json()["name"])

print(os.path.exists(""))