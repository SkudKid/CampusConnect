import requests
import json

BASE_URL = "http://localhost:5000"

def show(title, resp):
    print(f"\n=== {title} ===")
    print("Status:", resp.status_code)
    try:
        print("JSON:", resp.json())
    except Exception:
        print("Raw:", resp.text)

def main():
    # ---------- Register (ok if 409 already exists) ----------
    register_data = {"username": "miguel", "email": "miguel@example.com", "password": "1234"}
    r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    show("Register", r)

    # ---------- Login ----------
    login_data = {"email": "miguel@example.com", "password": "1234"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    show("Login", r)

    # Pull token
    try:
        token = r.json().get("token")
    except Exception:
        print("Could not parse login JSON. Aborting.")
        return
    if not token:
        print("No token returned. Aborting.")
        return

    headers = {"Authorization": token}

    # ========== TASKS ==========
    # ---------- Create Task ----------
    task_payload = {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": "2025-08-07",
        "priority": 2
    }
    r = requests.post(f"{BASE_URL}/api/tasks", json=task_payload, headers=headers)
    show("Create Task", r)

    # ---------- List Tasks ----------
    r = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    show("Get Tasks", r)

    # grab an id for update/delete
    try:
        tasks = r.json()
        task_id = tasks[0]["id"] if tasks else None
    except Exception:
        task_id = None

    # ---------- Update Task (partial PUT) ----------
    if task_id:
        # Only update one field to confirm partial update works
        update_payload = {"priority": 1}
        r = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_payload, headers=headers)
        show(f"Update Task {task_id} (partial)", r)

        # ---------- Delete Task ----------
        r = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
        show(f"Delete Task {task_id}", r)
    else:
        print("\n(No tasks to update/delete)")

    # ========== EVENTS ==========
    # ---------- Create Event ----------
    event_payload = {
        "title": "Midterm Exam",
        "description": "CIS375 midterm in room 204",
        "event_date": "2025-08-20",
        "location": "Building A",
        "shared_with": "teammate@example.com"
    }
    r = requests.post(f"{BASE_URL}/api/events", json=event_payload, headers=headers)
    show("Create Event", r)

    # ---------- List Events ----------
    r = requests.get(f"{BASE_URL}/api/events", headers=headers)
    show("Get Events", r)

    # grab an event id
    try:
        events = r.json()
        event_id = events[0]["id"] if events else None
    except Exception:
        event_id = None

    # ---------- Get Single Event ----------
    if event_id:
        r = requests.get(f"{BASE_URL}/api/events/{event_id}", headers=headers)
        show(f"Get Event {event_id}", r)

        # ---------- Delete Event ----------
        r = requests.delete(f"{BASE_URL}/api/events/{event_id}", headers=headers)
        show(f"Delete Event {event_id}", r)
    else:
        print("\n(No events to fetch/delete)")

if __name__ == "__main__":
    main()
