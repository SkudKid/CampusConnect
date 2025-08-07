import requests

BASE_URL = "http://localhost:5000"

# ---------- Register User ----------
register_data = {
    "username": "miguel",
    "email": "miguel@example.com",
    "password": "1234"
}
r = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Register:", r.status_code, r.json())

# ---------- Login User ----------
login_data = {
    "email": "miguel@example.com",
    "password": "1234"
}
r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print("Login:", r.status_code, r.json())

# Save token
token = r.json().get("token")
headers = {"Authorization": token}

# ---------- Create Task ----------
task_data = {
    "title": "Test Task",
    "description": "This is a test task",
    "due_date": "2025-08-07",
    "priority": 2
}
r = requests.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
print("Create Task:", r.status_code, r.json())

# ---------- Get Tasks ----------
r = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
print("Get Tasks:", r.status_code, r.json())

# ---------- Edit Tasks ----------
task_id_to_edit = 1
updated_data = {
    "title": "Updated Task Title",
    "description": "New description here",
    "due_date": "2025-08-10",
    "priority": 1
}

r = requests.put(f"{BASE_URL}/api/tasks/{task_id_to_edit}", json=updated_data, headers=headers)
print("Edit Task:", r.status_code, r.json())


# ---------- Delete Tasks ----------
task_id_to_delete = 1
r = requests.delete(f"{BASE_URL}/api/tasks/{task_id_to_delete}", headers=headers)
print("Delete Task:", r.status_code, r.json())

# ---------- Create Event ----------
event_data = {
    "title": "Midterm Exam",
    "description": "CIS375 midterm in room 204",
    "event_date": "2025-08-20",
    "location": "Building A",
    "shared_with": "teammate@example.com"
}

r = requests.post(f"{BASE_URL}/api/events", json=event_data, headers=headers)
print("Create Event:", r.status_code, r.json())
