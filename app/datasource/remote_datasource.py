import requests

url = "https://outdev.werkdone.com/VMS_BL/rest/ChatBot/Visitation?ClientPrefix=SLEC"
data_context = ""
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Accept": "application/json"
}

params = {
    "param1": "value1",
    "param2": "value2"
}

response = requests.get(url)

if response.status_code == 200:
    data = response #check if response in json form => data = response.json()
    data_context = data
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
