import requests
import json
from datetime import datetime
import random

SERVICE_URL = "http://localhost:3000/generate_paragraph_with_questions"

TOPICS = [
    "الطبيعة في فصل الربيع",
    "أهمية القراءة في حياتنا اليومية",
    "فوائد ممارسة الرياضة للصحة",
    "تأثير التكنولوجيا على المجتمع الحديث",
    "أهمية الحفاظ على البيئة",
    "دور الفن في الثقافة العربية",
    "تحديات التعليم عن بعد",
    "أهمية السفر في توسيع آفاق الإنسان",
    "تأثير وسائل التواصل الاجتماعي على العلاقات الإنسانية",
    "دور الشباب في بناء المستقبل"
]

PREFERENCES = ["القصص الخيالية", "الحقائق العلمية", "القصص التاريخية", "الألعاب التعليمية", "الفنون والموسيقى"]
LEVELS = ["مبتدئ", "متوسط", "متقدم"]

def send_request(topic, age, preference, level, max_length=250):
    data = {
        "topic": topic,
        "age": age,
        "preference": preference,
        "level": level,
        "max_length": max_length
    }
    
    try:
        response = requests.post(SERVICE_URL, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def save_to_file(markdown_content, topic, age, preference, level):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_content_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    
    return filename

def main():
    topic = random.choice(TOPICS)
    age = random.randint(6, 14)
    preference = random.choice(PREFERENCES)
    level = random.choice(LEVELS)
    max_length = 250

    print(f"Selected topic: '{topic}'")
    print(f"Age: {age}")
    print(f"Preference: {preference}")
    print(f"Arabic level: {level}")
    print(f"Max length: {max_length}")
    
    response = send_request(topic, age, preference, level, max_length)

    if response:
        markdown_content = response['markdown_content']
        print("\nGenerated Markdown Content:")
        print(markdown_content)
        
        filename = save_to_file(markdown_content, topic, age, preference, level)
        print(f"\nGenerated content saved to: {filename}")
    else:
        print("Failed to get a response from the service.")

if __name__ == "__main__":
    main()