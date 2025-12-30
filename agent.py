import os
from typing import Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from retriever import match_faq
from image_fetcher import fetch_images_by_faq



GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_LLM_MODEL = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
model = GOOGLE_LLM_MODEL

# === Steps ===
def retrieve_faq(state: Dict) -> Dict:
    user_query = state.get("query")
    faq_data = match_faq(user_query)
    state["faq_data"] = faq_data
    return state

def fetch_images(state: Dict) -> Dict:
    faq_data = state.get("faq_data")
    if not faq_data:
        state["response"] = {"error": "Sorry, I couldn’t find any answer for that."}
        return state
    faq_id = faq_data["id"]
    images = fetch_images_by_faq(faq_id)
    state["images"] = images
    return state

def generate_llm_response(state: Dict) -> Dict:
    images = state.get("images", [])
    faq_data = state.get("faq_data")
    query = state.get("query")

    if not images:
        state["response"] = {
            "question": faq_data["question"] if faq_data else query,
            "answer": faq_data["answer"] if faq_data else "",
            "images": [],
            "llm_response": "No images found."
        }
        return state

    if len(images) == 1:
        # Single image case
        image = images[0]
        prompt = f"Q: {query}\nImage description: {image['description']}\nGive a short helpful answer in 10 words clearly."
        response = model.invoke(prompt)
        answer = response.content.strip() if hasattr(response, "text") else str(response)
        state["response"] = {
            "user_query": query,
            "faq_id": image["faq_id"],
            "image_id": image["image_id"],
            "image_url": image["image_url"],
            "llm_answer": answer
        }
    else:
        # Multiple images = stepwise answer
        results = []
        for i, image in enumerate(images):
            prompt = f"Q: {query}\nStep {i+1} Description: {image['description']}\nAnswer this step in 10 words clearly."
            response = model.invoke(prompt)
            step_answer = response.content.strip() if hasattr(response, "text") else str(response)
            results.append({
                "user_query": query,
                "faq_id": image["faq_id"],
                "image_id": image["image_id"],
                "image_url": image["image_url"],
                "llm_answer": step_answer
            })
        state["response"] = results
    return state

# === LangGraph Definition ===
workflow = StateGraph(dict)
workflow.add_node("faq_search", retrieve_faq)
workflow.add_node("image_search", fetch_images)
workflow.add_node("generate_answer", generate_llm_response)

workflow.set_entry_point("faq_search")
workflow.add_edge("faq_search", "image_search")
workflow.add_edge("image_search", "generate_answer")
workflow.add_edge("generate_answer", END)

# Add memory to track state across invocations
checkpointer = MemorySaver()
agent_graph = workflow.compile(checkpointer=checkpointer)

# === CLI for Testing ===
if __name__ == "__main__":
    thread_id = "session_001"  # For memory tracking, can be dynamic
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_query = input("Ask a question: ")
        state = {"query": user_query}
        result_state = agent_graph.invoke(state, config=config)
        print("\nFinal Output:")
        print(result_state["response"])

