from typing import Dict
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from agent import agent_graph

app = FastAPI()

class QueryInput(BaseModel):
    query: str
    thread_id: str = "default_session"

@app.post("/ask")
async def ask_question(data: QueryInput):
    try:
        state = {"query": data.query}
        config = {"configurable": {"thread_id": data.thread_id}}
        result_state: Dict = agent_graph.invoke(state, config=config)
        return {"success": True, "response": result_state.get("response")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
def root():
    return {"message": "AI Support Agent API is running."}

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
