import os, json, time
from dotenv import load_dotenv
import tkinter as tk
from tkinter import simpledialog
import requests

CONFIG_FILE = ".jenv"
TOKENS_FILE = "tokens.json"

AUTH_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
API_URL = "https://api.atlassian.com"


# ---------------------------
# Load Jira credentials (.jenv) or prompt user
# ---------------------------
def get_jira_credentials():
    env_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    load_dotenv(env_path)

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8080/callback")
    scopes = os.getenv("SCOPES", "read:jira-work write:jira-work manage:jira-project")

    if not client_id or not client_secret:
        print("⚠️ Missing CLIENT_ID or CLIENT_SECRET. Opening Tkinter prompt...")

        root = tk.Tk()
        root.withdraw()

        if not client_id:
            client_id = simpledialog.askstring("Jira OAuth Setup", "Enter Atlassian CLIENT_ID:")
        if not client_secret:
            client_secret = simpledialog.askstring("Jira OAuth Setup", "Enter Atlassian CLIENT_SECRET:", show="*")

        with open(env_path, "w") as f:
            f.write(f"CLIENT_ID={client_id}\n")
            f.write(f"CLIENT_SECRET={client_secret}\n")
            f.write(f"REDIRECT_URI={redirect_uri}\n")
            f.write(f"SCOPES={scopes}\n")

        print(f"💾 Saved Jira credentials into {env_path}")

    return client_id, client_secret, redirect_uri, scopes


# ---------------------------
# Token utilities
# ---------------------------
def save_tokens(tokens):
    # add expires_at field for convenience
    if "expires_in" in tokens:
        tokens["expires_at"] = int(time.time()) + tokens["expires_in"]
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print("💾 Tokens saved to", TOKENS_FILE)


def load_tokens():
    if os.path.exists(TOKENS_FILE):
        return json.load(open(TOKENS_FILE))
    return None


def refresh_access_token(client_id, client_secret, refresh_token):
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    resp = requests.post(TOKEN_URL, json=data)
    if resp.status_code == 200:
        tokens = resp.json()
        save_tokens(tokens)
        print("✅ Access token refreshed")
        return tokens
    print("❌ Token refresh failed:", resp.text)
    return None


def get_valid_access_token(client_id, client_secret):
    """Return a valid access token, refreshing if needed."""
    tokens = load_tokens()
    if not tokens:
        raise Exception("❌ No tokens found. Run the Flask login flow first.")

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_at = tokens.get("expires_at", 0)

    # refresh if expired (or near expiry)
    if time.time() >= expires_at - 30:
        print("⚠️ Access token expired or near expiry. Refreshing...")
        tokens = refresh_access_token(client_id, client_secret, refresh_token)
        if not tokens:
            raise Exception("❌ Could not refresh access token.")
        access_token = tokens["access_token"]

    return access_token


# ---------------------------
# Jira API utilities
# ---------------------------
def get_cloud_id(access_token):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(f"{API_URL}/oauth/token/accessible-resources", headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Error getting cloudid: {resp.status_code} {resp.text}")

    resources = resp.json()
    if not resources:
        raise Exception("No accessible Jira resources found")

    if len(resources) == 1:
        return resources[0]["id"]

    print("\nAccessible Jira Sites:")
    for i, r in enumerate(resources):
        print(f"[{i}] {r['name']} ({r['url']}) :: ID = {r['id']}")

    # Try interactive console selection
    try:
        choice = int(input("\nSelect a Jira site index: "))
        if 0 <= choice < len(resources):
            return resources[choice]["id"]
    except Exception:
        pass

    # Default to the first if user skips input
    print("Defaulting to first site.")
    return resources[0]["id"]

    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(f"{API_URL}/oauth/token/accessible-resources", headers=headers)
    resources = resp.json()
    print("Accessible Jira Sites:")
    for r in resources:
        print(f"- {r['name']} ({r['url']}) :: ID = {r['id']}")
    return resources[0]["id"]  # or prompt for selection


def get_projects(access_token, cloudid):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(f"{API_URL}/ex/jira/{cloudid}/rest/api/3/project", headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Error fetching projects: {resp.status_code} {resp.text}")
    return resp.json()

def get_issues(access_token, cloudid, project_key, jql="ORDER BY created DESC"):
    """
    Fetch issues using Jira Cloud's /rest/api/3/search endpoint with POST body.
    Compatible with Atlassian API Gateway.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    url = f"{API_URL}/ex/jira/{cloudid}/rest/api/3/search"

    # POST body — standard JQL syntax
    data = {
        "jql": f"project = {project_key} {jql}",
        "maxResults": 20,
        "fields": ["summary", "status", "assignee", "created"]
    }

    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        raise Exception(f"Error fetching issues: {resp.status_code} {resp.text}")

    return resp.json().get("issues", [])
