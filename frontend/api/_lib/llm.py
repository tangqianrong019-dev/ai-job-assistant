"""统一 LLM 服务层"""
import os, json, re
from openai import OpenAI


def _extract_json(raw: str) -> dict:
    """从 LLM 响应中提取 JSON，兼容 markdown 代码块"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if match:
        raw = match.group(1)
    return json.loads(raw)


def call_llm(prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
    """调用 DeepSeek LLM"""
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com") + "/v1",
    )
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=temperature,
        max_tokens=2048,
    )
    return resp.choices[0].message.content or ""


def call_llm_json(prompt: str, system_prompt: str = "", temperature: float = 0.0) -> dict:
    """调用 LLM 并返回解析后的 JSON"""
    raw = call_llm(prompt, system_prompt, temperature)
    try:
        return _extract_json(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "error": "JSON parse failed"}
