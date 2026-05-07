"""
Mini LangGraph Research Agent

This script builds a simple agentic workflow using LangGraph nodes.
It takes a user prompt, searches the web using SerpAPI, summarizes the results,
and then returns a concise answer.

Requirements:
- SERPAPI_API_KEY set in your environment
- Either Ollama + llama2 installed locally, or OPENAI_API_KEY set

Usage:
  python main.py
"""

import os
from typing import TypedDict

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import SerpAPIWrapper
from langgraph.graph.state import StateGraph

# Ensure Ollama is accessible even if its install directory is not on PATH yet.
ollama_dir = os.getenv(
    "OLLAMA_PATH",
    r"C:\Users\ASUS\AppData\Local\Programs\Ollama",
)
if os.path.isdir(ollama_dir):
    os.environ["PATH"] = os.pathsep.join([ollama_dir, os.environ.get("PATH", "")])

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
if not SERPAPI_API_KEY:
    raise ValueError("Please set SERPAPI_API_KEY in your environment.")

USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").strip().lower() not in ("false", "0", "no")


def get_llm():
    if USE_LOCAL_LLM:
        try:
            from langchain_ollama import ChatOllama

            print("Using local Ollama (llama2)...")
            return ChatOllama(model="llama2", temperature=0.2)
        except Exception as e:
            print(f"Warning: Ollama not available ({e}). Falling back to OpenAI.")

    try:
        from langchain_openai import ChatOpenAI

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        print("Using OpenAI...")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, api_key=openai_key)
    except Exception as e:
        raise ValueError(
            f"Cannot initialize LLM: {e}. "
            "Install Ollama with 'ollama pull llama2' or set OPENAI_API_KEY."
        )


llm = get_llm()
search = SerpAPIWrapper(serpapi_api_key=SERPAPI_API_KEY)


class ResearchState(TypedDict, total=False):
    query: str
    search_results: str
    summary: str
    final_answer: str


def web_search_tool(query: str) -> str:
    print(f"[search] Searching for: {query}")
    results = search.run(query)
    if isinstance(results, dict):
        return str(results)
    return results


def summarize_tool(text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "You are an intelligent research assistant. Summarize the key points "
            "from the following web search results in a short paragraph.\n\n{text}"
        ),
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text})


def answer_tool(query: str, summary: str) -> str:
    prompt = PromptTemplate(
        input_variables=["query", "summary"],
        template=(
            "A user asked: {query}\n\nHere are the summarized results from the search:\n{summary}\n\n"
            "Using the summary, answer the user's question clearly and concisely."
        ),
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"query": query, "summary": summary})


def ask_handler(state: ResearchState) -> ResearchState:
    if not state.get("query"):
        state["query"] = input("Enter your prompt for the LangGraph agent: ").strip()
    return state


def search_handler(state: ResearchState) -> ResearchState:
    query = state.get("query", "")
    state["search_results"] = web_search_tool(query)
    return state


def summarize_handler(state: ResearchState) -> ResearchState:
    state["summary"] = summarize_tool(state.get("search_results", ""))
    return state


def answer_handler(state: ResearchState) -> ResearchState:
    state["final_answer"] = answer_tool(state.get("query", ""), state.get("summary", ""))
    return state


def build_agent_graph() -> StateGraph:
    graph = StateGraph(state_schema=ResearchState)
    graph.add_node("ask", ask_handler)
    graph.add_node("search", search_handler)
    graph.add_node("summarize", summarize_handler)
    graph.add_node("answer", answer_handler)
    graph.add_edge("ask", "search")
    graph.add_edge("search", "summarize")
    graph.add_edge("summarize", "answer")
    graph.set_entry_point("ask")
    return graph


def run_agent(prompt: str | None = None) -> str:
    graph = build_agent_graph()
    state: ResearchState = {}
    if prompt:
        state["query"] = prompt
    final_state = graph.compile().invoke(state)
    return final_state.get("final_answer", "No answer generated.")


if __name__ == "__main__":
    import sys
    
    print("=== LangGraph Research Agent ===")
    
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Type a research prompt or question: ").strip()
    
    if not user_prompt:
        print("No prompt provided.")
        sys.exit(1)
    
    print("\nRunning LangGraph workflow...\n")
    
    try:
        output = run_agent(user_prompt)
        print("=== Agent Output ===\n")
        print(output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
