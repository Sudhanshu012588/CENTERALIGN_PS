from Agent.state import State
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
import json

from rich.console import Console


console = Console()

def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    text_parts.append(
                        part.get("text", "")
                    )
                elif "text" in part:
                    text_parts.append(
                        part["text"]
                    )
            elif isinstance(part, str):
                text_parts.append(part)
        return "".join(text_parts)
    return str(content)


def FinalResponseNode(state: State, llm):
    PromptPath = Path("Prompts/FinalResponse.txt")
    SystemPrompt = load_prompt(PromptPath)
    state_summary = {
        "user_request": state.get("user_request"),
        "plan": state.get("plan", []),
        "execution_history": state.get("execution_history", []),
        "verification": state.get("verification", {}),
        "status": state.get("status"),
        "error": state.get("error")
    }

    DynamicPrompt = f"""
                USER REQUEST:
                {state["user_request"]}

                COMPLETE EXECUTION INFORMATION:
                {json.dumps(state_summary, indent=2, default=str)}
            """

    messages = [
        {
            "role": "system",
            "content": SystemPrompt
        },
        {
            "role": "user",
            "content": DynamicPrompt
        }
    ]
    response_text = ""

    for chunk in llm.stream(messages):
        content = extract_text(chunk.content)
        if content:
            console.print(content,end="",soft_wrap=True)
            response_text += content
            
    console.print()
    return {
        "final_response": response_text
    }