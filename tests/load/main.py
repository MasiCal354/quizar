from locust import HttpUser, task, between

class LoadUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def healthcheck(self):
        self.client.get("/api/v1/health")

    @task
    def servertime(self):
        self.client.get("/api/v1/time")
