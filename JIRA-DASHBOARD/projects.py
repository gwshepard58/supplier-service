import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load credentials from .jevn
load_dotenv(".jenv")

JIRA_SERVER = os.getenv("JIRA_SERVER")
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_TOKEN")

url = f"{JIRA_SERVER}/rest/api/3/project/search"

response = requests.get(
    url,
    auth=HTTPBasicAuth(EMAIL, API_TOKEN),
    headers={"Accept": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    print("Total projects:", data.get("total"))
    for proj in data.get("values", []):
        print(f"{proj['key']} - {proj['name']}")
else:
    print("Error:", response.status_code, response.text)
