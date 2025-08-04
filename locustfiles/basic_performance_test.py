from locust import HttpUser, task, between

# NOTE: Update these credentials for your test environment
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # Login and store JWT token
        response = self.client.post("/api/login/", json={"username": "user", "password": "user"})
        if response.status_code == 200 and "access" in response.json():
            self.token = response.json()["access"]
        else:
            self.token = None

    @task
    def get_roles(self):
        if self.token:
            self.client.get("/api/roles/", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def get_school_list(self):
        if self.token:
            self.client.get("/api/schools/", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def get_notifications(self):
        if self.token:
            self.client.get("/api/notifications/", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def get_timetable(self):
        if self.token:
            self.client.get("/api/class-timetable/", headers={"Authorization": f"Bearer {self.token}"})

# Add more tasks as needed for other endpoints
