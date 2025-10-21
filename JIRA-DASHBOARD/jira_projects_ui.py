import tkinter as tk
from tkinter import ttk, messagebox
from jira_auth import (
    get_jira_credentials,
    get_valid_access_token,
    get_cloud_id,
    get_projects,
    get_issues,
)

# ---------------------------
# Setup
# ---------------------------
CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPES = get_jira_credentials()

# Always get a valid access token (auto-refresh if expired)
access_token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
cloudid = get_cloud_id(access_token)

# ---------------------------
# Tkinter UI
# ---------------------------
root = tk.Tk()
root.title("Jira Projects & Issues")
root.geometry("950x600")

# Projects frame
projects_frame = ttk.LabelFrame(root, text="Projects")
projects_frame.pack(fill="x", padx=10, pady=5)

projects_tree = ttk.Treeview(projects_frame, columns=("Key", "Name"), show="headings", height=8)
projects_tree.heading("Key", text="Project Key")
projects_tree.heading("Name", text="Project Name")
projects_tree.column("Key", width=150, anchor="w")
projects_tree.column("Name", width=600, anchor="w")
projects_tree.pack(fill="x", padx=5, pady=5)

# Issues frame
issues_frame = ttk.LabelFrame(root, text="Issues")
issues_frame.pack(fill="both", expand=True, padx=10, pady=5)

issues_tree = ttk.Treeview(issues_frame, columns=("Key", "Summary", "Status"), show="headings", height=15)
issues_tree.heading("Key", text="Issue Key")
issues_tree.heading("Summary", text="Summary")
issues_tree.heading("Status", text="Status")
issues_tree.column("Key", width=150, anchor="w")
issues_tree.column("Summary", width=600, anchor="w")
issues_tree.column("Status", width=150, anchor="w")
issues_tree.pack(fill="both", expand=True, padx=5, pady=5)


# ---------------------------
# Functions
# ---------------------------
def load_projects():
    """Load Jira projects into the Treeview"""
    for row in projects_tree.get_children():
        projects_tree.delete(row)

    try:
        token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
        projects = get_projects(token, cloudid)
        for p in projects:
            projects_tree.insert("", "end", values=(p["key"], p["name"]))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load projects:\n{e}")


def load_issues(event):
    """Load issues when a project is selected"""
    for row in issues_tree.get_children():
        issues_tree.delete(row)

    selected_item = projects_tree.selection()
    if not selected_item:
        return

    project_key = projects_tree.item(selected_item[0], "values")[0]

    try:
        token = get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
        issues = get_issues(token, cloudid, project_key)
        for issue in issues:
            issues_tree.insert(
                "",
                "end",
                values=(
                    issue["key"],
                    issue["fields"]["summary"],
                    issue["fields"]["status"]["name"],
                ),
            )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load issues:\n{e}")


# ---------------------------
# Event binding
# ---------------------------
projects_tree.bind("<<TreeviewSelect>>", load_issues)

# Load initial data
load_projects()

# ---------------------------
root.mainloop()
