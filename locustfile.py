from locust import HttpUser, task, between

class GudlftUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def voir_accueil(self):
        self.client.get("/")

    @task
    def voir_tableau_points(self):
        self.client.get("/pointsboard")

    @task
    def connexion(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})