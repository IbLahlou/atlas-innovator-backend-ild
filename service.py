import bentoml
from bentoml.io import JSON
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

# Load the saved model
arabic_llm = bentoml.transformers.get("arabic_llm_scenario_generator:latest")
model = arabic_llm.load_model()
tokenizer = arabic_llm.custom_objects["tokenizer"]

# Create a BentoML service
svc = bentoml.Service("arabic_scenario_generator", runners=[])

@svc.api(input=JSON(), output=JSON())
def generate_scenario(input_data: dict) -> dict:
    preference = input_data.get("preference", "")
    level = input_data.get("level", "")
    age = input_data.get("age", "")

    # Create a prompt based on the input
    prompt = f"اكتب سيناريو قصير باللغة العربية لطفل عمره {age} سنوات، مستواه {level}، ويفضل {preference}."

    # Tokenize the input
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    # Generate
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=200,
            num_return_sequences=1,
            no_repeat_ngram_size=2
        )

    # Decode the output
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Create the response JSON
    response = {
        "input": {
            "preference": preference,
            "level": level,
            "age": age
        },
        "scenario": generated_text
    }

    return json.dumps(response, ensure_ascii=False)