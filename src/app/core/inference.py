import requests
from app.app_secrets.infisical import BASETEN_API_KEY
from app.core.logging import setup_logger

setup_logger()


class Baseten(object):
    def __init__(self, model_id):
        self.model_id = model_id

    def __call__(self):
        response = requests.post(
            model_url=f"https://model-{self.model_id}.api.baseten.co/production/predict",
            headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
            json={},
        )
        return response.json()
