
import json
from langchain_community.chat_models import ChatOllama
from config import OLLAMA_MODEL

llm = ChatOllama(model=OLLAMA_MODEL)

def structure_text(text):
    prompt = f"""提取JSON:
industry, companies, resource_type, money, region
文本: {text}
只返回JSON"""
    resp = llm.invoke(prompt).content
    try:
        return json.loads(resp)
    except:
        return {}
