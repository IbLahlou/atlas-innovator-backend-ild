# 🌐 Atlas Innovator ALLAM LLM - Arabic Language Intelligence API

## 🧠 Project Overview
This project provides an API using **BentoML** to serve an Arabic **Language Learning Model (LLM)**. The API generates child-friendly content in Arabic based on input topic, age, preferences, and language level. The model output is in Markdown format, which is then returned as part of a JSON response.

---

## 📁 Repository Structure
```
atlas-innovator-allam-llm/
├── bentofile.yaml         # BentoML configuration for building the service
├── service.py             # API definition using BentoML
├── requirements.txt       # Python dependencies
├── models.py              # Model loading and saving to BentoML
└── README.md              # Project documentation
```

---

## 🚀 API Overview

### Endpoint: `/generate_content`
- **Method**: `POST`
- **Input**: JSON
- **Output**: JSON (Content in Arabic with Markdown formatting)
- **Description**: Generates Arabic content based on topic, child's age, preferences, and language level.

### Example Input:
```json
{
  "topic": "الطبيعة في فصل الربيع",
  "age": 10,
  "preference": "القصص الخيالية",
  "level": "متوسط"
}
```

### Example Output:
```json
{
  "markdown_content": "# الطبيعة في فصل الربيع\n\n[Generated content in Arabic...]\n\n## الأسئلة\n\n1. [First question...]\n2. [Second question...]\n3. [Third question...]\n\n---\n- نوع المحتوى: قصة قصيرة\n- الفئة العمرية: 10 سنوات\n- التفضيل: القصص الخيالية\n- المستوى اللغوي: متوسط",
  "metadata": {
    "topic": "الطبيعة في فصل الربيع",
    "age": 10,
    "preference": "القصص الخيالية",
    "level": "متوسط",
    "content_type": "قصة قصيرة"
  }
}
```

---

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Save the model to BentoML's model store**:
   ```bash
   python models.py
   ```

3. **Run the BentoML service**:
   ```bash
   bentoml serve service.py:svc --reload
   ```

4. **Test the service**:
   ```bash
   curl -X POST "http://127.0.0.1:3000/generate_content" \
   -H "Content-Type: application/json" \
   -d '{"topic": "الطبيعة في فصل الربيع", "age": 10, "preference": "القصص الخيالية", "level": "متوسط"}'
   ```

---

## 🧑‍💻 API Input/Output Details

### Input (JSON):
- **topic**: The main subject of the content (e.g., "الطبيعة في فصل الربيع").
- **age**: Child's age (e.g., 10).
- **preference**: Child's content preference (e.g., "القصص الخيالية").
- **level**: Child's Arabic language level (e.g., "متوسط").

### Output (JSON):
- **markdown_content**: Generated content in Arabic with Markdown formatting.
- **metadata**: Information about the generated content, including the input parameters and the type of content generated.

---

## 🎨 Content Types

The API can generate various types of content, including:
- Short stories
- Factual information
- Dialogues
- Imaginative descriptions

The content type is randomly selected for each request to provide variety.

---

## 📚 Educational Features

- **Age-appropriate content**: The generated content is tailored to suit the specified age group.
- **Preference-aligned**: Content aligns with the child's stated preferences.
- **Language level adaptation**: The complexity of the language adjusts based on the specified Arabic language level.
- **Engaging questions**: Each piece of content includes three thought-provoking questions to encourage engagement and comprehension.

