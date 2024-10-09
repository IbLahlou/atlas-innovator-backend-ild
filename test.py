import bentoml
import torch

# Load the saved model
arabic_llm = bentoml.transformers.get("arabic_llm_scenario_generator:latest")
model_runner = arabic_llm.to_runner()
model_runner.init_local()

# Get the tokenizer
tokenizer = arabic_llm.custom_objects["tokenizer"]

def generate_text(prompt, max_length=100):
    # Tokenize the input
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    # Generate
    with torch.no_grad():
        output = model_runner.run(
            input_ids,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2
        )

    # Decode the output
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text

# Example usage
prompt = "مرحبا، كيف حالك؟"  # "Hello, how are you?" in Arabic
generated_text = generate_text(prompt)
print(generated_text)