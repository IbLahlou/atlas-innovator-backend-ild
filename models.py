import bentoml
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the Arabic LLM (you can choose any model from Hugging Face)
model_name = "aubmindlab/aragpt2-medium"  # Example Arabic model from Hugging Face

# Load the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Save the model into BentoML's model store (this will automatically version it)
bentoml.transformers.save_model(
    "arabic_llm_scenario_generator",  # The name for the model in BentoML's model store
    model,  # The loaded model
    signatures={"generate": {"batchable": False}},  # Define the model signature
    labels={"framework": "transformers", "task": "causal-language-modeling"},
    custom_objects={"tokenizer": tokenizer}  # Save tokenizer alongside the model
)

print("Model saved successfully!")