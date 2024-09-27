from transformers import AutoTokenizer, AutoModelForVision2Seq, AutoProcessor
from PIL import Image
from huggingface_hub import login
from dotenv import load_dotenv, find_dotenv
import base64
from io import BytesIO
import torch
import os


class GuardRailsAsServiceForVision:
    def __init__(self, taxonomy: str = None):
        _ = load_dotenv(find_dotenv())
        login(token=os.environ.get('HF_TOKEN'))

        model_id = os.environ.get('GUARD_RAIL_MODEL')
        cached_model_name = os.environ.get('CACHED_MODEL_NAME')
        dtype = torch.bfloat16

        # Specify the cache directory (optional)
        self.cache_dir = os.path.expanduser("~/.cache/huggingface/hub")

        # Check if the model is already cached
        model_path = os.path.join(self.cache_dir, cached_model_name)
        if not os.path.exists(model_path):
            print(f"Model not found in cache, downloading {model_id}...")
        else:
            print(f"Model {model_id} is already cached. Loading from {model_path}.")

        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_id, cache_dir=self.cache_dir)
        self.model = AutoModelForVision2Seq.from_pretrained(pretrained_model_name_or_path=model_id, torch_dtype=dtype,
                                                            device_map='auto', cache_dir=self.cache_dir)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.taxonomy = taxonomy

    def moderate_chat(self, chat):
        input_prompt = self.processor.apply_chat_template(
            chat, return_tensors="pt"
        )
        print(input_prompt)
        base64_string = ''
        if 'base64,' in chat[0].get('content')[0].get('base64_str'):
            base64_string = chat[0].get('content')[0].get('base64_str').split('base64,')[1]

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)

        # Create a BytesIO object
        image_buffer = BytesIO(image_data)
        image = Image.open(image_buffer).convert("RGB")
        image.show()
        inputs = self.processor(text=input_prompt, images=image, return_tensors="pt").to(self.model.device)

        prompt_len = len(inputs['input_ids'][0])
        output = self.model.generate(
            **inputs,
            max_new_tokens=20,
            pad_token_id=0,
        )

        generated_tokens = output[:, prompt_len:]

        return self.processor.decode(generated_tokens[0])


# if __name__ == '__main__':
#     rag_guard = GuardRailsAsServiceForVision()
#     _chat = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": "classify the image given"
#                 },
#                 {
#                     "type": "image",
#                 },
#             ],
#         }
#     ]
#
#     rag_guard.moderate_chat(chat=_chat)
