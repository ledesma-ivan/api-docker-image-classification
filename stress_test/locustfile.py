from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 10)

    @task(1)
    def index(self):
        self.client.get("http://localhost/")
    
    @task(3)
    def press_page(self):
        test = [("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg"))]
        self.client.post("/predict", files = test)
