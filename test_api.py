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
