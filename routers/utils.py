import os
import random
import base64
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import tempfile
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import aiohttp
import asyncio

load_dotenv()

class IBMWatsonXAIWrapper:
    def __init__(self, api_key, project_id, url, model_id="sdaia/allam-1-13b-instruct", max_new_tokens=400, decoding_method="greedy", temperature=0.7, top_p=1, repetition_penalty=1.0):
        self.api_key = api_key
        self.project_id = project_id
        self.url = f"{url}/ml/v1/text/generation?version=2023-05-29"
        self.model_id = model_id
        self.parameters = {
            "decoding_method": decoding_method,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty
        }
        self.access_token = None
        self.headers = None

    async def get_access_token(self):
        token_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, headers=headers, data=data) as response:
                response_json = await response.json()
                return response_json["access_token"]

    async def generate_text(self, prompt):
        if not self.access_token:
            self.access_token = await self.get_access_token()
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }

        body = {
            "input": f"<s> [INST] {prompt} [/INST]",
            "parameters": self.parameters,
            "model_id": self.model_id,
            "project_id": self.project_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, headers=self.headers, json=body) as response:
                if response.status != 200:
                    raise Exception(f"Non-200 response: {await response.text()}")
                data = await response.json()
                return data.get('results', [{}])[0].get('generated_text', "No text generated")

class ArabicLearningUtility:
    def __init__(self):
        self.watson_wrapper = self._init_watson_wrapper()
        self.tts = self._init_text_to_speech()
        self.templates = self._init_templates()

    def _init_watson_wrapper(self):
        api_key = os.getenv("IBM_WATSONX_API_KEY")
        project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
        url = os.getenv("IBM_WATSONX_URL", "https://eu-de.ml.cloud.ibm.com")
        return IBMWatsonXAIWrapper(api_key=api_key, project_id=project_id, url=url)

    def _init_text_to_speech(self):
        tts_api_key = os.getenv("IBM_WATSON_TTS_API_KEY")
        tts_url = os.getenv("IBM_WATSON_TTS_URL")
        authenticator = IAMAuthenticator(tts_api_key)
        tts = TextToSpeechV1(authenticator=authenticator)
        tts.set_service_url(tts_url)
        return tts

    def _init_templates(self):
        return {
            "vocabulary": PromptTemplate(
                input_variables=["category"],
                template="قم بإنشاء 5 كلمات عربية متعلقة بـ {category} مع شرح بسيط لكل كلمة باللغة العربية."
            ),
            "sentence": PromptTemplate(
                input_variables=[],
                template="قم بإنشاء جملة عربية بسيطة مناسبة للمبتدئين مع شرح لمعناها."
            ),
            "story": PromptTemplate(
                input_variables=[],
                template="احكِ قصة قصيرة جدًا (3-4 جمل) باللغة العربية للأطفال، ثم اشرح معناها ببساطة."
            ),
            "cultural_fact": PromptTemplate(
                input_variables=[],
                template="شارك معلومة مثيرة للاهتمام عن الثقافة العربية أو إحدى الدول الناطقة بالعربية."
            ),
            "quiz": PromptTemplate(
                input_variables=["quiz_type"],
                template="قم بإنشاء سؤال اختيار من متعدد حول {quiz_type} العربية مع 3 خيارات. قدم السؤال والخيارات باللغة العربية، وأشر إلى الإجابة الصحيحة."
            ),
            "pronunciation": PromptTemplate(
                input_variables=["word"],
                template="قدم نصائح للنطق الصحيح للكلمة العربية '{word}'. قم بتضمين التهجئة الصوتية وأي مقارنات مفيدة مع أصوات أخرى في اللغة العربية."
            )
        }

    async def process_pdf(self, file_content):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        documents = await asyncio.to_thread(loader.load)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = await asyncio.to_thread(text_splitter.split_documents, documents)
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        vector_store = await asyncio.to_thread(FAISS.from_documents, texts, embeddings)

        os.unlink(tmp_file_path)
        return vector_store

    async def generate_text(self, template_name, **kwargs):
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        prompt = template.format(**kwargs)
        return await self.watson_wrapper.generate_text(prompt)

    async def text_to_speech(self, text):
        try:
            audio_file = await asyncio.to_thread(
                self.tts.synthesize,
                text,
                accept='audio/mp3',
                voice='ar-MS_OmarVoice'
            )
            audio_file = audio_file.get_result().content
            audio_base64 = base64.b64encode(audio_file).decode('utf-8')
            return audio_base64
        except Exception as e:
            raise Exception(f"Error in text-to-speech conversion: {str(e)}")

    async def answer_question(self, vector_store, question):
        docs = await asyncio.to_thread(vector_store.similarity_search, question)
        context = docs[0].page_content if docs else "لم يتم العثور على معلومات ذات صلة."
        prompt = f"بناءً على المعلومات التالية: '{context}'، أجب عن هذا السؤال: {question}"
        return await self.watson_wrapper.generate_text(prompt)