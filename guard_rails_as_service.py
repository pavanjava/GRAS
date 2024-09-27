import litserve as ls
from core.gras_text import GuardRailsAsServiceForText
from core.gras_vision import GuardRailsAsServiceForVision


class GuardRailsLitAPI(ls.LitAPI):
    def __init__(self):
        # Specify the variables
        self.text_guard: GuardRailsAsServiceForText = None
        self.vision_guard: GuardRailsAsServiceForVision = None

    def setup(self, device):
        self.text_guard = GuardRailsAsServiceForText()
        self.vision_guard = GuardRailsAsServiceForVision()

    def decode_request(self, request):
        return request['chat'], request['type']

    def predict(self, options):
        if options[1] == 'text':
            return self.text_guard.moderate_chat(chat=options[0])
        elif options[1] == 'vision':
            return self.vision_guard.moderate_chat(chat=options[0])

    def encode_response(self, output):
        return {"output": output}


if __name__ == "__main__":
    api = GuardRailsLitAPI()
    server = ls.LitServer(api, accelerator="auto", workers_per_device=2, api_path='/api/v1/filter')
    server.run(port=8001)
