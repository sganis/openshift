import os
import sys
from locust import HttpUser, task, between

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)  # Random wait time between requests

    @task
    def load_test(self):
        self.client.get("/") 

    # @task
    # def load_test2(self):
    #     self.client.get("/logs/10")  # Adjust API calls as needed

    # @task(2)  # Run this task twice as often
    # def another_test(self):
    #     self.client.post("/api/data", json={"key": "value"})  # Adjust API calls as needed

if __name__ == "__main__":

    os.system(f"locust -f traffic.py --headless -u 1000 -r 100 --host {sys.argv[1]} --run-time 30m") 
