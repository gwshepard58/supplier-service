from flask import Flask, redirect, request
import requests
from jira_auth import get_jira_credentials, save_tokens, load_tokens, refresh_access_token, get_cloud_id, get_projects

CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES = get_jira_credentials()

AUTH_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"

app = Flask(__name__)

def build_auth_url():
    return (
        f"{AUTH_URL}?audience=api.atlassian.com"
        f"&client_id={CLIENT_ID}"
        f"&scope={SCOPES.replace(' ', '%20')}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&prompt=consent"
    )

@app.route("/")
def login():
    url = build_auth_url()
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No code returned from Atlassian", 400

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    resp = requests.post(TOKEN_URL, json=data)
    tokens = resp.json()

    if "access_token" not in tokens:
        return f"Error fetching token: {tokens}", 400

    save_tokens(tokens)
    return "✅ Tokens saved! Go to /projects"

@app.route("/projects")
def projects():
    tokens = load_tokens()
    if not tokens:
        return "❌ No tokens found. Login at /", 400

    access_token = tokens["access_token"]
    cloudid = get_cloud_id(access_token)
    projects = get_projects(access_token, cloudid)

    html = "<h2>Jira Projects</h2><ul>"
    for p in projects:
        html += f"<li><b>{p['key']}</b>: {p['name']}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(port=8080, debug=True)
