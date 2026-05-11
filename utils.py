import ollama
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from config import config

def get_llm(model_name: str = None, temperature: float = 0.7):
    """Return LLM (Cloud API if API_KEY is set, otherwise Ollama)"""
    if model_name is None:
        model_name = config.MAIN_MODEL
    
    if config.API_KEY:
        return ChatOpenAI(
            model=model_name, 
            temperature=temperature,
            api_key=config.API_KEY,
            base_url=config.BASE_URL
        )
    return OllamaLLM(model=model_name, temperature=temperature)

def get_fast_llm(temperature: float = 0.5):
    """Fast model for mutation and judging"""
    return get_llm(model_name=config.FAST_MODEL, temperature=temperature)

def call_llm(prompt: str, model: str = None, temperature: float = 0.7) -> str:
    """Universal LLM call: Uses Cloud API if key exists, otherwise Ollama"""
    if config.API_KEY:
        llm = ChatOpenAI(
            model=model or config.MAIN_MODEL,
            temperature=temperature,
            api_key=config.API_KEY,
            base_url=config.BASE_URL
        )
        return llm.invoke(prompt).content
    
    # Fallback to local Ollama
    if model is None:
        model = config.MAIN_MODEL
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

def save_best_prompt(name: str, prompt: str, score: float):
    """Save successful evolved prompts"""
    import json
    from datetime import datetime
    import os
    
    data = {
        "name": name,
        "prompt": prompt,
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    filepath = os.path.join(config.BEST_PROMPTS_DIR, f"{name.replace(' ', '_')}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"[DISK] Saved best prompt: {name} (Score: {score:.2f})")