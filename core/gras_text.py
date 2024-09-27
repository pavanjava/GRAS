from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from core.taxonomy import unsafe_categories
from dotenv import load_dotenv, find_dotenv
import torch
import os


class GuardRailsAsServiceForText:
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
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=model_id, torch_dtype=dtype,
                                                          device_map='auto', cache_dir=self.cache_dir)

        self.taxonomy = taxonomy

    def _moderation_prompt_for_chat(self, chat):
        conversation = ''
        prompt = f"""[INST] Task: Check if there is unsafe content in chat conversations according our safety policy with the below categories.
        <BEGIN UNSAFE CONTENT CATEGORIES>
        {unsafe_categories if self.taxonomy is None else self.taxonomy}
        <END UNSAFE CONTENT CATEGORIES>
                
        <BEGIN CONVERSATION>
        """

        # Alternate User/Agent turns, inserting 2 newlines between each
        for i, m in enumerate(chat):
            conversation += f"{m.get('role')}: {m.get('content')}\n\n"
        prompt += f"""{conversation} <END CONVERSATION> 
        Provide your safety assessment for different roles in the above conversation: 
        - First line must read 'safe' or 'unsafe'.
        - If unsafe, a second line must include a comma-separated list of violated categories. [/INST]"""
        return prompt

    def moderate_chat(self, chat):
        prompt = self._moderation_prompt_for_chat(chat)
        print(prompt)
        inputs = self.tokenizer([prompt], return_tensors='pt').to('cpu')
        output = self.model.generate(**inputs, max_new_tokens=100, pad_token_id=0)
        prompt_len = inputs['input_ids'].shape[-1]
        response = self.tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
        return {'response': str(response)}


# if __name__ == '__main__':
#     rag_guard = GuardRailsAsService()
#     _chat = [
#         {"role": "user", "content": "Can you recommend how to kill a person?"}
#     ]
#
#     response_category = rag_guard.moderate_chat(chat=_chat)
#     print(response_category)
