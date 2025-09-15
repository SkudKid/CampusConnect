import gradio as gr
import requests
import os

# Allow override via environment variable, default to local HTTP dev server
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000").rstrip("/")

# Use a session that ignores system proxy settings (avoids corporate/VPN proxy SSL issues)
_session = requests.Session()
_session.trust_env = False  # don't use HTTP(S)_PROXY env vars

def api_post(path, json=None, token=None):
    headers = {"Authorization": token} if token else {}
    return _session.post(f"{BASE_URL}{path}", json=json, headers=headers)

def api_get(path, token=None):
    headers = {"Authorization": token} if token else {}
    return _session.get(f"{BASE_URL}{path}", headers=headers)

def api_put(path, json=None, token=None):
    headers = {"Authorization": token} if token else {}
    return _session.put(f"{BASE_URL}{path}", json=json, headers=headers)

def api_delete(path, token=None):
    headers = {"Authorization": token} if token else {}
    return _session.delete(f"{BASE_URL}{path}", headers=headers)

#JSON parser
def parse_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}

#Auth Actions
def do_register(username, email, password):
    r = api_post("/auth/register", {"username": username, "email": email, "password": password})
    data = parse_json(r)
    ok = 200 <= r.status_code < 300
    return ("✅ Registered" if ok else f"❌ {data}"), ""

def do_login(email, password):
    r = api_post("/auth/login", {"email": email, "password": password})
    data = parse_json(r)
    # accept either {"token": "..."} or {"message": "..."} just in case
    token = data.get("token") or data.get("message")
    if token and r.status_code == 200:
        return f"✅ Logged in", token
    return f"❌ {data}", ""

#Task Actions
def refresh_tasks(token):
    r = api_get("/api/tasks", token=token)
    data = parse_json(r)

    if isinstance(data, list):
        # choose a consistent column order that matches your DB
        cols = ["id", "user_id", "title", "description", "due_date", "priority"]
        rows = []
        for row in data:
            # ensure dict and convert None -> ""
            if isinstance(row, dict):
                rows.append([(row.get(c) if row.get(c) is not None else "") for c in cols])
        return rows, f"Loaded {len(rows)} tasks."
    return [], f"❌ {data}"


def create_task(title, description, due_date, priority, token):
    if not title:
        return "❌ Title is required"
    payload = {
        "title": title,
        "description": description or "",
        "due_date": due_date or "",
        "priority": int(priority) if priority not in (None, "") else 0
    }
    r = api_post("/api/tasks", payload, token=token)
    data = parse_json(r)
    return "✅ Task created" if r.status_code == 201 else f"❌ {data}"

def update_task(task_id, title, description, due_date, priority, token):
    if not task_id:
        return "❌ Task ID required"
    payload = {}
    if title: payload["title"] = title
    if description is not None and description != "": payload["description"] = description
    if due_date is not None and due_date != "": payload["due_date"] = due_date
    if priority not in (None, ""):
        try:
            payload["priority"] = int(priority)
        except:
            return "❌ Priority must be an integer"
    if not payload:
        return "ℹ️ Nothing to update"
    r = api_put(f"/api/tasks/{int(task_id)}", payload, token=token)
    data = parse_json(r)
    return "✅ Task updated" if 200 <= r.status_code < 300 else f"❌ {data}"

def delete_task(task_id, token):
    if not task_id:
        return "❌ Task ID required"
    r = api_delete(f"/api/tasks/{int(task_id)}", token=token)
    data = parse_json(r)
    return "✅ Task deleted" if 200 <= r.status_code < 300 else f"❌ {data}"

#Events actions
def refresh_events(token):
    r = api_get("/api/events", token=token)
    data = parse_json(r)

    if isinstance(data, list):
        cols = ["id", "user_id", "title", "description", "event_date", "location", "shared_with"]
        rows = []
        for row in data:
            if isinstance(row, dict):
                rows.append([(row.get(c) if row.get(c) is not None else "") for c in cols])
        return rows, f"Loaded {len(rows)} events."
    return [], f"❌ {data}"


def create_event(title, description, event_date, location, shared_with, token):
    if not title:
        return "❌ Title is required"
    payload = {
        "title": title,
        "description": description or "",
        "event_date": event_date or "",
        "location": location or "",
        "shared_with": shared_with or ""
    }
    r = api_post("/api/events", payload, token=token)
    data = parse_json(r)
    return "✅ Event created" if r.status_code == 201 else f"❌ {data}"

def get_event(event_id, token):
    if not event_id:
        return {}, "❌ Event ID required"
    r = api_get(f"/api/events/{int(event_id)}", token=token)
    data = parse_json(r)
    if isinstance(data, dict) and "id" in data:
        return data, "✅ Event fetched"
    return {}, f"❌ {data}"

def delete_event(event_id, token):
    if not event_id:
        return "❌ Event ID required"
    r = api_delete(f"/api/events/{int(event_id)}", token=token)
    data = parse_json(r)
    return "✅ Event deleted" if 200 <= r.status_code < 300 else f"❌ {data}"

###########GRADIO###########
with gr.Blocks(title="CampusConnect") as demo:
    gr.Markdown("## CampusConnect - Demo UI")

    token_state = gr.State("") #Stores JWT after login

    with gr.Tab("Auth"):
        gr.Markdown("### Register")
        reg_user = gr.Textbox(label="Username")
        reg_email = gr.Textbox(label="Email")
        reg_pass = gr.Textbox(label="Password", type="password")
        reg_btn = gr.Button("Register")
        reg_out = gr.Textbox(label="Register Result", interactive=False)

        gr.Markdown("### Login")
        login_email = gr.Textbox(label="Email")
        login_pass = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        login_out = gr.Textbox(label="Login Result", interactive=False)
        token_box = gr.Textbox(label="JWT (read-only)", interactive=False)

        reg_btn.click(do_register, [reg_user, reg_email, reg_pass], [reg_out])
        login_btn.click(do_login, [login_email, login_pass], [login_out, token_state]).then(
            fn=lambda t: t, inputs=token_state, outputs=token_box
        )

    with gr.Tab("Tasks"):
        gr.Markdown("### Create Task")
        t_title = gr.Textbox(label="Title")
        t_desc = gr.Textbox(label="Description")
        t_due = gr.Textbox(label="Due Date (YYYY-MM-DD)")
        t_priority = gr.Number(label="Priority (int)", value=0, precision=0)
        t_create_btn = gr.Button("Create Task")
        t_create_out = gr.Textbox(label="Create Result", interactive=False)

        gr.Markdown("### Your Tasks")
        t_refresh = gr.Button("Refresh Tasks")
        t_table = gr.Dataframe(
            headers=["id", "user_id", "title", "description", "due_date", "priority"],
            row_count=5,
            interactive=False
        )
        t_status = gr.Textbox(label="Status", interactive=False)

        gr.Markdown("### Edit / Delete Task")
        t_id = gr.Number(label="Task ID", precision=0)
        t_new_title = gr.Textbox(label="New Title (optional)")
        t_new_desc = gr.Textbox(label="New Description (optional)")
        t_new_due = gr.Textbox(label="New Due Date (YYYY-MM-DD) (optional)")
        t_new_pri = gr.Number(label="New Priority (int, optional)", precision=0)
        t_update_btn = gr.Button("Update Task (Partial)")
        t_update_out = gr.Textbox(label="Update Result", interactive=False)

        t_delete_btn = gr.Button("Delete Task")
        t_delete_out = gr.Textbox(label="Delete Result", interactive=False)

        t_create_btn.click(create_task, [t_title, t_desc, t_due, t_priority, token_state], [t_create_out])
        t_refresh.click(refresh_tasks, [token_state], [t_table, t_status])
        t_update_btn.click(update_task, [t_id, t_new_title, t_new_desc, t_new_due, t_new_pri, token_state],
                           [t_update_out])
        t_delete_btn.click(delete_task, [t_id, token_state], [t_delete_out])

    with gr.Tab("Events"):
        gr.Markdown("### Create Event")
        e_title = gr.Textbox(label="Title")
        e_desc = gr.Textbox(label="Description")
        e_date = gr.Textbox(label="Event Date (YYYY-MM-DD)")
        e_loc = gr.Textbox(label="Location")
        e_share = gr.Textbox(label="Shared With (email or text)")
        e_create_btn = gr.Button("Create Event")
        e_create_out = gr.Textbox(label="Create Result", interactive=False)

        gr.Markdown("### Your Events")
        e_refresh = gr.Button("Refresh Events")
        e_table = gr.Dataframe(
            headers=["id", "user_id", "title", "description", "event_date", "location", "shared_with"],
            row_count=5,
            interactive=False
        )
        e_status = gr.Textbox(label="Status", interactive=False)

        gr.Markdown("### View / Delete Event")
        e_id = gr.Number(label="Event ID", precision=0)
        e_get_btn = gr.Button("Get Event")
        e_detail = gr.JSON(label="Event Detail")
        e_delete_btn = gr.Button("Delete Event")
        e_delete_out = gr.Textbox(label="Delete Result", interactive=False)

        e_create_btn.click(create_event, [e_title, e_desc, e_date, e_loc, e_share, token_state], [e_create_out])
        e_refresh.click(refresh_events, [token_state], [e_table, e_status])
        e_get_btn.click(get_event, [e_id, token_state], [e_detail, e_status])
        e_delete_btn.click(delete_event, [e_id, token_state], [e_delete_out])

    gr.Markdown("Login first, then use Tasks/Events tabs. Keep the server running in another terminal.")

if __name__ == "__main__":
    demo.queue().launch()