import bentoml
from bentoml.io import JSON
import torch
import re

arabic_llm = bentoml.transformers.get("arabic_llm_scenario_generator:latest")
runner = arabic_llm.to_runner()
svc = bentoml.Service("arabic_paragraph_generator", runners=[runner])

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove special characters and numbers, but keep punctuation
    text = re.sub(r'[^\u0600-\u06FF\s\.\،\؟\!]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@svc.api(input=JSON(), output=JSON())
async def generate_paragraph_with_questions(input_data: dict) -> dict:
    topic = input_data.get("topic", "الطبيعة في فصل الربيع")
    max_length = input_data.get("max_length", 1050)

    prompt = f"""اكتب فقرة موجزة ودقيقة باللغة العربية الفصحى عن الموضوع التالي: {topic}
    بعد كتابة الفقرة، قم بإنشاء ثلاثة أسئلة موجزة ومختلفة حول محتوى الفقرة. تأكد من أن الأسئلة متنوعة وتغطي جوانب مختلفة من الموضوع.

    الفقرة:"""

    tokenizer = arabic_llm.custom_objects["tokenizer"]
    inputs = tokenizer(prompt, return_tensors="pt")
    
    outputs = await runner.generate.async_run(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=3,
        do_sample=True,
        top_k=50,
        top_p=0.92,
        temperature=0.7,
        repetition_penalty=1.2,
        early_stopping=True
    )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove the prompt from the generated text
    generated_text = generated_text.replace(prompt, "", 1).strip()
    
    # Clean the generated text
    cleaned_text = clean_text(generated_text)
    
    # Split the text into paragraph and questions
    parts = cleaned_text.split("الأسئلة:")
    paragraph = parts[0].strip()
    
    questions = []
    if len(parts) > 1:
        question_text = parts[1]
        questions = [q.strip() for q in re.split(r'\d+[\-\.\)]\s*', question_text) if q.strip()]
        questions = questions[:3]  # Ensure we have at most 3 questions
    
    # If we don't have 3 questions, generate generic ones
    while len(questions) < 3:
        questions.append(f"ما هي إحدى النقاط الرئيسية في الفقرة عن {topic}؟")
    
    # Ensure questions are unique
    questions = list(dict.fromkeys(questions))
    while len(questions) < 3:
        questions.append(f"كيف يمكن تطبيق المعلومات الواردة في الفقرة عن {topic} في الحياة اليومية؟")
    
    # Format as Markdown
    markdown_output = f"""# {topic}

{paragraph}

## الأسئلة

1. {questions[0]}
2. {questions[1]}
3. {questions[2]}
"""
    
    return {
        "markdown_content": markdown_output,
        "topic": topic
    }

# To start the service, run:
# bentoml serve service:svc --reload