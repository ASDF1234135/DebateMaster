import os
import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END



class Point(BaseModel):
    point: str
    severity: str = Field(description="high, mid, or low")
    description: str


class JudgeOutput(BaseModel):
    pros: List[Point]
    cons: List[Point]
    improvement_tips: List[str]


class InitOutput(BaseModel):
    pro_system_prompt: str = Field(description="Affirmative AI's Dedicated System Prompt")
    con_system_prompt: str = Field(description="Negative AI's Dedicated System Prompt")


class DebateState(TypedDict):
    session_id: str
    context: str
    prompt: str
    my_persona: str
    opponent_persona: str
    pro_sys_prompt: str
    con_sys_prompt: str
    max_rounds: int
    max_trials: int
    current_trial: int
    current_round: int
    history: Annotated[List[Dict[str, Any]], operator.add]
    final_report: Dict[str, Any]


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

judge_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    api_key=OPENAI_API_KEY
).with_structured_output(JudgeOutput)

init_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=OPENAI_API_KEY
).with_structured_output(InitOutput)


async def init_node(state: DebateState) -> Dict[str, Any]:
    meta_prompt = """You are a top-tier AI prompt engineer. Your task is to generate System Prompts for two AI Agents in a debate.
Based on the provided debate topic, background information, and character profiles of both sides, tailor the most suitable System Prompts.

Requirements:
1. The System Prompt must instruct the Agent to strictly adhere to its character profile. Includes "Context", "Argument" and "Profile & Persona" for each side.
2. The System Prompt must instruct the Agent to limit each statement to 150 words or less in English.
3. The opposing side's prompt must emphasize "absolutely not agreeing with the affirmative side's core arguments and constantly finding fault."
4. The affirmative side's prompt must emphasize "maintaining a firm stance and counterattacking the opposing side's weaknesses."
5. You must output the result in JSON format with exactly these two keys: "pro_system_prompt" and "con_system_prompt".
6. You need to ensure that both sides fully understand the context and prompts, as well as their core arguments.
7. You should encourage both sides to omit polite language and focus on the debate itself.
"""

    user_msg = f"""
Debate Topic: {state['prompt']}
Supplementary Background Information: {state.get('context', 'None')}
Affirmative Persona (My Persona): {state.get('my_persona', 'A staunch defender')}
Negative Persona (Opponent Persona): {state.get('opponent_persona', 'A sharp questioner')}
"""

    messages = [
        SystemMessage(content=meta_prompt),
        HumanMessage(content=user_msg),
    ]

    structured_response = await init_llm.ainvoke(messages)

    return {
        "pro_sys_prompt": structured_response.pro_system_prompt,
        "con_sys_prompt": structured_response.con_system_prompt,
    }


async def pro_node(state: DebateState) -> Dict[str, Any]:
    full_sys_prompt = (
        f"{state['pro_sys_prompt']}\n\n"
        f"=== DEBATE TOPIC ===\n{state['prompt']}\n\n"
        f"=== BACKGROUND CONTEXT ===\n{state.get('context', 'None')}"
    )
    messages = [SystemMessage(content=full_sys_prompt)]

    current_trial = state["current_trial"]
    trial_history = [msg for msg in state["history"] if msg.get("trial") == current_trial]

    for msg in trial_history:
        prefix = "Aff: " if msg["speaker"] == "agent_pro" else "Neg (Opponent): "
        messages.append(HumanMessage(content=f"{prefix}{msg['content']}"))

    response = await llm.ainvoke(messages)

    return {
        "history": [{
            "speaker": "agent_pro",
            "content": response.content,
            "round": state["current_round"],
            "trial": current_trial,
        }]
    }


async def con_node(state: DebateState) -> Dict[str, Any]:
    full_sys_prompt = (
        f"{state['con_sys_prompt']}\n\n"
        f"=== DEBATE TOPIC ===\n{state['prompt']}\n\n"
        f"=== BACKGROUND CONTEXT ===\n{state.get('context', 'None')}"
    )
    
    messages = [SystemMessage(content=full_sys_prompt)]
    current_trial = state["current_trial"]
    trial_history = [msg for msg in state["history"] if msg.get("trial") == current_trial]

    for msg in trial_history:
        prefix = "Aff(Opponent): " if msg["speaker"] == "agent_pro" else "Neg: "
        messages.append(HumanMessage(content=f"{prefix}{msg['content']}"))

    response = await llm.ainvoke(messages)

    return {
        "current_round": state["current_round"] + 1,
        "history": [{
            "speaker": "agent_con",
            "content": response.content,
            "round": state["current_round"],
            "trial": current_trial,
        }]
    }


async def judge_node(state: DebateState) -> Dict[str, Any]:
    sys_prompt = """
        You are an objective reviewer.
        Please read the entire debate's history (which may contain multiple trials/parallel universes).
        Analyze the overall strengths and weaknesses of the affirmative (user's) arguments across all trials,
        and provide comprehensive and specific suggestions for improving the affirmative side's initial arguments.

        In the strengths section, you should explain the user's key arguments and why they are strong. 
        In the weaknesses section, you should explain the potential flaws in the user's arguments,
        the reasons behind them, and how the opposing side might attack or challenge them.
        
        Please strictly adhere to the specified JSON format for output.
        """

    history_text = ""
    for t in range(1, state["current_trial"] + 1):
        history_text += f"\n--- Trial {t} ---\n"
        t_hist = [m for m in state["history"] if m.get("trial") == t]
        history_text += "\n".join(
            [f"{m['speaker']} (Round {m['round']}): {m['content']}" for m in t_hist]
        )

    initial_arguments = f"{state['prompt']}\n\n{state.get('context', 'None')}"

    messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"Debate history:\n{history_text}"),
        HumanMessage(content=f"Initial Arguments:\n{initial_arguments}"),
    ]

    structured_response = await judge_llm.ainvoke(messages)

    return {
        "final_report": structured_response.model_dump()
    }


async def next_trial_node(state: DebateState) -> Dict[str, Any]:
    return {
        "current_trial": state["current_trial"] + 1,
        "current_round": 1,
    }


def should_continue(state: DebateState) -> str:
    if state["current_round"] <= state["max_rounds"]:
        return "continue"
    elif state["current_trial"] < state["max_trials"]:
        return "next_trial"
    return "end"


builder = StateGraph(DebateState)

builder.add_node("init", init_node)
builder.add_node("agent_pro", pro_node)
builder.add_node("agent_con", con_node)
builder.add_node("next_trial_node", next_trial_node)
builder.add_node("agent_judge", judge_node)

builder.add_edge(START, "init")
builder.add_edge("init", "agent_pro")
builder.add_edge("agent_pro", "agent_con")

builder.add_conditional_edges(
    "agent_con",
    should_continue,
    {
        "continue": "agent_pro",
        "next_trial": "next_trial_node",
        "end": "agent_judge",
    }
)

builder.add_edge("next_trial_node", "agent_pro")
builder.add_edge("agent_judge", END)

graph = builder.compile()


async def run_debate(config: dict):

    initial_state: DebateState = {
        "session_id": config["session_id"],
        "context": config.get("context", ""),
        "prompt": config["prompt"],
        "opponent_persona": config.get("opponent_persona", "A sharp questioner"),
        "my_persona": config.get("my_persona", "A staunch defender"),
        "pro_sys_prompt": "",
        "con_sys_prompt": "",
        "max_rounds": config["max_rounds"],
        "max_trials": config.get("trial", 1),
        "current_trial": 1,
        "current_round": 1,
        "history": [],
        "final_report": {},
    }


    try:
        async for event in graph.astream(initial_state):
            for node_name, node_update in event.items():

                if node_name == "init":
                    event_data = {
                        "type": "init",
                        "pro_sys_prompt": node_update["pro_sys_prompt"],
                        "con_sys_prompt": node_update["con_sys_prompt"],
                    }
                    yield event_data

                elif node_name in ["agent_pro", "agent_con"]:
                    latest_message = node_update["history"][-1]

                    event_data = {
                        "type": "conversation",
                        "speaker": latest_message["speaker"],
                        "round": latest_message["round"],
                        "trial": latest_message["trial"],
                        "content": latest_message["content"],
                    }

                    yield event_data

                elif node_name == "agent_judge":
                    report = node_update["final_report"]

                    event_data = {
                        "type": "summary",
                        "speaker": "agent_judge",
                        "pros": report["pros"],
                        "cons": report["cons"],
                        "improvement_tips": report["improvement_tips"],
                    }


                    yield event_data

    except Exception:
        raise
