class LLMService:
    def __init__(self):
        self.models = {
            1: {"name": "model1", "description": "Description of Model 1"},
            2: {"name": "model2", "description": "Description of Model 2"},
        }

    def get_model_list(self):
        return [{"id": model_id, **model} for model_id, model in self.models.items()]

    def send_context_to_model(self, context: str, model_id: int):

        # TODO

        if model_id not in self.models:
            raise ValueError("Model ID not found")
