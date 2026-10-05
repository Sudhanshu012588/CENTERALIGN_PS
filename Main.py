import os
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from Agent.state import State
from Agent.planner import PromptToPlan
from dotenv import load_dotenv
from Agent.executor import Executer
from Tools.TerminalUI import (show_loading,show_header,show_user_request,show_planning,show_plan_details,show_execution,show_result,show_final_response)
from Agent.FinalResponse import FinalResponseNode
from langchain_xai import ChatXAI
from langchain_ollama import ChatOllama
from Tools.ModelSelector  import select_model, create_llm


load_dotenv()
Gemini_API = os.getenv("GEMINI_API_KEY")
XAI_API = os.getenv("XAI_API")
SandBox = os.getenv("SANDBOX_LOCATION")

print(f"\n✓ Select your model\n")
model_config, model_name = select_model()

print(f"\n✓ Using {model_name}\n")

llm = create_llm(
    model_config,
    Gemini_API,
    XAI_API
)

if not Gemini_API:
    raise ValueError("GEMINI_API_KEY is not set in the environment.")

if not SandBox:
    raise ValueError("SANDBOX_LOCATION is not set in the environment.")
# llm = ChatGoogleGenerativeAI(
#         model="gemini-3.5-flash",
#         temperature=0,
#         google_api_key=Gemini_API
#         )
# llm = ChatXAI(
#         model="grok-4.7",
#         temperature=0,
#         api_key=GROK_API
#     )
# llm = ChatOllama(
#         model="qwen3:8b",
#         temperature=0
#     )

def PlannerNode(state:State):
    Plan = PromptToPlan(llm,Prompt=state['user_request'])
    return Plan

def ExecuterRouter(state: State):
    if state["status"] == "failed":
        return "failed"
    if state["current_task"] < len(state["plan"]):
        return "continue"
    return "done"

def FinalResponseNodeWrapper(state: State):
    return FinalResponseNode(state, llm)

def BuildGraph():
    builder = StateGraph(State)

    builder.add_node("PlannerNode", PlannerNode)
    builder.add_node("Executer", Executer)
    builder.add_node("FinalResponse", FinalResponseNodeWrapper)
    builder.add_edge(START,"PlannerNode")
    builder.add_edge("PlannerNode","Executer")

    builder.add_conditional_edges(
        "Executer",
        ExecuterRouter,
        {
            "continue": "Executer",
            "done": "FinalResponse",
            "failed": "FinalResponse"
        }
    )
    builder.add_edge("FinalResponse",END)
    graph = builder.compile()
    return graph


def main():

    print("*" * 50)
    print("CentrAlign Worker")
    print("*" * 50)
    graph = BuildGraph()
    show_header()
    conversation_history = []
    while True:
        try:
            UserReq = input("\nWhat Would You Like me To do > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break
        if UserReq.lower() in ["exit", "quit", "q"]:
            print("\nGoodbye!")
            break
        if not UserReq:
            continue
        show_user_request(UserReq)
        conversation_history.append({
            "role": "user",
            "content": UserReq
        })

        initial_state: State = {
            "user_request": UserReq,
            "sandbox": SandBox,
            "conversation_history": conversation_history.copy(),
            "plan": [],
            "current_task": 0,
            "execution_history": [],
            "verification": {},
            "retry_count": 0,
            "status": "started",
            "error": None,
            "final_response": ""
        }
        with show_loading("Thinking..."):
            result = graph.invoke(initial_state)

        show_planning(result.get("plan", []))
        show_plan_details(result.get("plan", []))
        show_execution(result.get("execution_history", []))
        show_result(result)
        final_response = result.get("final_response","No final response was generated.")
        show_final_response(final_response)
        conversation_history.append({
            "role": "assistant",
            "content": final_response})

if __name__ == "__main__":
    main()