import os
import asyncio
from typing import TypedDict, Annotated, List, Dict, Any
from pydantic import BaseModel, Field
import operator

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
    trial: int
    current_round: int
    history: Annotated[List[Dict[str, Any]], operator.add] 
    final_report: Dict[str, Any]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1).with_structured_output(JudgeOutput)
init_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7).with_structured_output(InitOutput)

async def init_node(state: DebateState) -> Dict:    
    meta_prompt = """You are a top-tier AI prompt engineer. Your task is to generate System Prompts for two AI Agents in a debate.
        Based on the provided debate topic, background information, and character profiles of both sides, tailor the most suitable System Prompts.

        Requirements:
            1. The System Prompt must instruct the Agent to strictly adhere to its character profile.
            2. The System Prompt must instruct the Agent to limit each statement to 150 characters or less.
            3. The opposing side's prompt must emphasize "absolutely not agreeing with the affirmative side's core arguments and constantly finding fault."
            4. The affirmative side's prompt must emphasize 'maintaining a firm stance and counterattacking the opposing side's weaknesses.'"""

    user_msg = f"""
            Debate Topic: {state['prompt']}
            Supplementary Background Information: {state.get('context', 'None')}
            Affirmative Persona (My Persona): {state.get('my_persona', 'A staunch defender')}
            Negative Persona (Opponent Persona): {state['opponent_persona']}
        """

    messages = [
        SystemMessage(content=meta_prompt),
        HumanMessage(content=user_msg)
    ]

    structured_response = await init_llm.ainvoke(messages)
    
    return {
        "pro_sys_prompt": structured_response.pro_system_prompt,
        "con_sys_prompt": structured_response.con_system_prompt
    }

async def pro_node(state: DebateState) -> Dict:
    messages = [SystemMessage(content=state["pro_sys_prompt"])]
    for msg in state["history"]:
        prefix = "Aff: " if msg["speaker"] == "agent_pro" else "Neg (Opponent): "
        messages.append(HumanMessage(content=f"{prefix}{msg['content']}"))

    response = await llm.ainvoke(messages)
    
    return {
        "history": [{
            "speaker": "agent_pro",
            "content": response.content,
            "round": state["current_round"],
            "trial": state["trial"]
        }]
    }

async def con_node(state: DebateState) -> Dict:
    messages = [SystemMessage(content=state["con_sys_prompt"])]
    for msg in state["history"]:
        prefix = "Aff(Opponent):" if msg["speaker"] == "agent_pro" else "Neg: "
        messages.append(HumanMessage(content=f"{prefix}{msg['content']}"))

    response = await llm.ainvoke(messages)
    
    return {
        "current_round": state["current_round"] + 1,
        "history": [{
            "speaker": "agent_con",
            "content": response.content,
            "round": state["current_round"], 
            "trial": state["trial"]
        }]
    }

async def judge_node(state: DebateState) -> Dict:
    
    sys_prompt = """You are an objective reviewer. 
        Please read the entire debate's history, analyze the strengths and weaknesses of the affirmative (user's) arguments, 
        and provide specific suggestions for improvement.
        Please strictly adhere to the specified JSON format for output."""

    history_text = "\n".join([f"{m['speaker']} (Round {m['round']}): {m['content']}" for m in state["history"]])
    messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"Debate history: \n{history_text}")
    ]

    structured_response = await judge_llm.ainvoke(messages)
    
    return {
        "final_report": structured_response.model_dump()
    }


def should_continue(state: DebateState) -> str:
    if state["current_round"] < state["max_rounds"]:
        return "continue"
    return "end"


builder = StateGraph(DebateState)

builder.add_node("init", init_node)
builder.add_node("agent_pro", pro_node)
builder.add_node("agent_con", con_node)
builder.add_node("agent_judge", judge_node)

builder.add_edge(START, "agent_pro")
builder.add_edge("agent_pro", "agent_con")
builder.add_conditional_edges(
    "agent_con",
    should_continue,
    {
        "continue": "agent_pro",
        "end": "agent_judge"
    }
)
builder.add_edge("agent_judge", END)

graph = builder.compile()


async def run_debate(config: dict):
    initial_state = {
        "session_id": config["session_id"],
        "context": config.get("context", ""),
        "prompt": config["prompt"],
        "opponent_persona": config["opponent_persona"],
        "my_persona": config.get("my_persona", "A staunch defender"),
        "pro_sys_prompt": "",
        "con_sys_prompt": "", 
        "max_rounds": config["max_rounds"],
        "trial": config["trial"],
        "current_round": 1,
        "history": [],
        "final_report": {}
    }

    async for event in graph.astream(initial_state):
        for node_name, node_update in event.items():
            if node_name in ["agent_pro", "agent_con"]:
                latest_message = node_update["history"][0]
                yield {
                    "type": "conversation",
                    "speaker": latest_message["speaker"],
                    "round": latest_message["round"],
                    "trial": latest_message["trial"],
                    "content": latest_message["content"]
                }
            
            elif node_name == "agent_judge":
                report = node_update["final_report"]
                yield {
                    "type": "summary",
                    "speaker": "agent_judge",
                    "pros": report["pros"],
                    "cons": report["cons"],
                    "improvement_tips": report["improvement_tips"]
                }