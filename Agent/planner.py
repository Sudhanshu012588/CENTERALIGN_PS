import langchain,langchain_core,langchain_google_genai
from Agent.state import State
from pathlib import Path
import json
import re


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_json(text: str):
    text = text.strip()

    # Remove markdown code fences
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    text = text.strip()

    return json.loads(text)


def PromptToPlan(llm,Prompt:str):
    """This Node will take User given prompt and understand the requirement's and convert the prompt into JSON with varous tasks needed to perform in order to complete the task"""
    PromptPath = "/Users/sudhanshujha/Documents/Projects/CentrAlign_PS/Prompts/Planner.txt"
    SystemPrompt = load_prompt(PromptPath)
    message = [
        {
            "role":"system",
            "content":SystemPrompt
        },
        {
            "role":"user",
            "content":Prompt
        }
    ]
    response = llm.invoke(message)
    content = response.content

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
                elif "text" in part:
                    text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        content = "".join(text_parts)


    try:
        Plan = extract_json(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner returned invalid JSON:\n{content}") from e
    return {
        "plan": Plan["tasks"],
        "current_task": 0,
        "status": "planned",
        "error": None
    }