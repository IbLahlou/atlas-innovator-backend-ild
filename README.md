# 🌐 Atlas Innovator ALLAM LLM - Arabic Language Intelligence API

## 🧠 Project Overview

This project provides an API using **BentoML** to serve an Arabic **Language Learning Model (LLM)**. The API generates child-friendly scenarios in Arabic based on input preferences, level, and a phrase. The model output is in **XML format**, which is converted to **JSON** for easier consumption.

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

### Endpoint: `/generate_scenario`

- **Method**: `POST`
- **Input**: JSON
- **Output**: JSON (Scenario in Arabic)
- **Description**: Generates an Arabic scenario based on child preferences, level, and a phrase.

### Example Input:

```json
{
  "preferences": "السيارات والألوان",
  "level": "مبتدئ",
  "phrase": "سيارة حمراء تسير بسرعة"
}
```

### Example Output:

```json
{
  "scenario": {
    "background": "في يوم مشمس، كان هناك سيارة حمراء تسير بسرعة كبيرة...",
    "characters": ["طفل", "سيارة"],
    "lesson": "السائق الجيد هو الذي يحترم إشارات المرور."
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
   curl -X POST "http://127.0.0.1:3000/generate_scenario" \
   -H "Content-Type: application/json" \
   -d '{"preferences": "السيارات والألوان", "level": "مبتدئ", "phrase": "سيارة حمراء تسير بسرعة"}'
   ```

---

## 🧑‍💻 API Input/Output Details

### Input (JSON):
- **preferences**: Child's preferences (e.g., cars, colors).
- **level**: Child's learning level (e.g., beginner).
- **phrase**: A phrase in Arabic that will help generate the scenario.

### Output (JSON):
- **scenario**: A generated scenario in Arabic, converted from the model's XML output.
