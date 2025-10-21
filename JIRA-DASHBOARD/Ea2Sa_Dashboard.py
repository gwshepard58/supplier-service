import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import threading
import datetime
import json
import os
import requests

from jira_auth import (
    get_valid_access_token,
    get_projects,
    get_issues,
    get_jira_credentials,
)

API_URL = "https://api.atlassian.com"
TOKENS_FILE = "tokens.json"

# ---------------------------
# Load credentials once
# ---------------------------
CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES = get_jira_credentials()


# ---------------------------
# Utility functions
# ---------------------------
def get_token_expiry():
    """Return expiry timestamp and datetime if available."""
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE) as f:
            tokens = json.load(f)
        expires_at = tokens.get("expires_at")
        if expires_at:
            return expires_at, datetime.datetime.fromtimestamp(expires_at)
    return None, None


def get_all_accessible_sites(access_token):
    """Return all Jira sites the user can access."""
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(f"{API_URL}/oauth/token/accessible-resources", headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Error getting accessible sites: {resp.status_code} {resp.text}")
    return resp.json()


# ---------------------------
# Tkinter Dashboard class
# ---------------------------
class JiraDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ea2Sa Jira Dashboard")
        self.geometry("950x650")

        # Context variables
        self.cloud_id = None
        self.sites = []
        self.projects = []

        # ---- Menu Bar ----
        self.build_menu()

        # ---- Header ----
        tk.Label(
            self, text="Ea2Sa Jira Dashboard",
            font=("Arial", 16, "bold"), fg="#0b36ad"
        ).pack(pady=10)

        # ---- Status ----
        self.status_label = tk.Label(self, text="Not Authorized ❌", font=("Arial", 12), fg="red")
        self.status_label.pack(pady=5)

        # ---- Expiry ----
        self.expiry_label = tk.Label(self, text="", font=("Arial", 10), fg="blue")
        self.expiry_label.pack(pady=5)

        # ---- Project list ----
        self.project_listbox = tk.Listbox(self, width=80, height=10)
        self.project_listbox.pack(pady=10)
        self.project_listbox.bind("<<ListboxSelect>>", self.on_project_select)

        # ---- Output area ----
        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=110, height=20)
        self.output.pack(padx=10, pady=10)

        # ---- Auto-check tokens ----
        self.after(500, self.check_existing_tokens)

    # ---------------------------
    # Menu setup
    # ---------------------------
    def build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Authorize / Refresh", command=self.handle_authorization)
        file_menu.add_command(label="Select Site & List Projects", command=self.list_projects)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Clear Output", command=lambda: self.output.delete("1.0", tk.END))
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label="About Ea2Sa Jira Dashboard",
            command=lambda: messagebox.showinfo(
                "About",
                "Ea2Sa Jira Dashboard\n\nA lightweight Jira client\n"
                "with OAuth, multi-site project listing, and issue viewer.\n\n© Ea2Sa Technology Research"
            )
        )
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    # ---------------------------
    # Token Management
    # ---------------------------
    def check_existing_tokens(self):
        """Try to refresh tokens automatically on startup."""
        def check():
            try:
                access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
                if access_token:
                    self.status_label.config(text="Authorized ✅", fg="green")
                    expires_at, expiry_dt = get_token_expiry()
                    if expiry_dt:
                        self.expiry_label.config(text=f"Token expires at {expiry_dt}")
                        self.update_countdown(expires_at)
            except Exception as e:
                self.output.insert(tk.END, f"⚠️ No valid tokens yet: {e}\n")
        threading.Thread(target=check, daemon=True).start()

    def update_countdown(self, expires_at):
        """Show a live countdown for token expiration."""
        if not expires_at:
            return
        now = datetime.datetime.now().timestamp()
        remaining = int(expires_at - now)
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            hours, mins = divmod(mins, 60)
            self.expiry_label.config(text=f"Token expires in {hours}h {mins}m {secs}s")
            self.after(1000, lambda: self.update_countdown(expires_at))
        else:
            self.expiry_label.config(text="⚠️ Token expired, attempting refresh...")
            self.auto_refresh()

    def auto_refresh(self):
        """Try to refresh automatically when expired."""
        def do_refresh():
            try:
                access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
                if access_token:
                    self.status_label.config(text="Authorized ✅ (auto-refresh)", fg="green")
                    expires_at, expiry_dt = get_token_expiry()
                    if expiry_dt:
                        self.expiry_label.config(text=f"Token refreshed, new expiry: {expiry_dt}")
                        self.update_countdown(expires_at)
                else:
                    self.status_label.config(text="Not Authorized ❌", fg="red")
                    self.expiry_label.config(text="⚠️ Auto-refresh failed")
            except Exception as e:
                self.status_label.config(text="Not Authorized ❌", fg="red")
                self.expiry_label.config(text=f"⚠️ Auto-refresh failed: {e}")
        threading.Thread(target=do_refresh, daemon=True).start()

    def handle_authorization(self):
        """Manual reauthorization."""
        def run_auth():
            try:
                access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
                if access_token:
                    self.status_label.config(text="Authorized ✅", fg="green")
                    messagebox.showinfo("Success", "You are authorized and tokens are refreshed!")
                    expires_at, expiry_dt = get_token_expiry()
                    if expiry_dt:
                        self.expiry_label.config(text=f"Token expires at {expiry_dt}")
                        self.update_countdown(expires_at)
                else:
                    messagebox.showerror("Error", "Failed to authorize Jira.")
            except Exception as e:
                messagebox.showerror("Error", f"Authorization failed: {e}")
        threading.Thread(target=run_auth, daemon=True).start()

    # ---------------------------
    # Project listing with safe site selection
    # ---------------------------
    def list_projects(self):
        """Fetch accessible sites, then prompt site selection safely."""
        def fetch_sites():
            try:
                access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
                sites = get_all_accessible_sites(access_token)
                if not sites:
                    self.after(0, lambda: messagebox.showwarning("No Sites", "No accessible Jira sites found."))
                    return
                self.after(0, lambda: self.select_and_fetch_projects(access_token, sites))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch sites: {e}"))
        threading.Thread(target=fetch_sites, daemon=True).start()

    def select_and_fetch_projects(self, access_token, sites):
        """Show site selection popup on main thread, then load projects."""
        try:
            if len(sites) > 1:
                site_names = [f"{s['name']} ({s['url']})" for s in sites]
                choice_str = "\n".join([f"{i+1}. {n}" for i, n in enumerate(site_names)])
                selected = simpledialog.askstring(
                    "Select Jira Site",
                    f"Available sites:\n{choice_str}\n\nEnter site number:"
                )
                try:
                    idx = int(selected) - 1 if selected else 0
                    if idx < 0 or idx >= len(sites):
                        idx = 0
                except Exception:
                    idx = 0
                self.cloud_id = sites[idx]["id"]
            else:
                self.cloud_id = sites[0]["id"]

            threading.Thread(
                target=lambda: self.load_projects(access_token),
                daemon=True
            ).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select site: {e}")

    def load_projects(self, access_token):
        """Fetch and display projects after site selection."""
        try:
            projects = get_projects(access_token, self.cloud_id)
            self.projects = projects
            self.after(0, self.display_projects)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch projects: {e}"))

    def display_projects(self):
        """Populate the listbox with projects."""
        self.project_listbox.delete(0, tk.END)
        for proj in self.projects:
            self.project_listbox.insert(tk.END, f"{proj['key']} :: {proj['name']}")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"📋 Found {len(self.projects)} project(s) in selected site.\n")

    # ---------------------------
    # Project & issue handling
    # ---------------------------
    def on_project_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        project_key = self.projects[index]["key"]
        threading.Thread(target=lambda: self.fetch_issues(project_key), daemon=True).start()

    def fetch_issues(self, project_key):
        """Fetch and display issues for the selected project."""
        def run():
            try:
                access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
                issues = get_issues(access_token, self.cloud_id, project_key)

                text = f"🐞 Issues in {project_key}:\n\n"
                if not issues:
                    text += "No issues found.\n"

                for issue in issues:
                    key = issue.get("key", "<no key>")
                    fields = issue.get("fields", {})
                    summary = fields.get("summary", "(no summary)")
                    status = fields.get("status", {}).get("name", "(no status)")
                    text += f"- {key}: {summary} (Status: {status})\n"

                self.after(0, lambda: self.output_display(text))
            except Exception as e:
                err_msg = str(e)
                self.after(
                    0,
                    lambda msg=err_msg: messagebox.showerror(
                        "Error", f"Failed to fetch issues: {msg}"
                    ),
                )
        threading.Thread(target=run, daemon=True).start()

    def output_display(self, text):
        """Thread-safe text update."""
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)


# ---------------------------
# Main entry
# ---------------------------
if __name__ == "__main__":
    app = JiraDashboard()
    app.mainloop()
