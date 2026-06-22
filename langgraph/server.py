from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from typing import TypedDict, List
from dotenv import load_dotenv
from datetime import datetime
import logging
import json
import os

load_dotenv()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

app=FastAPI(
    title="Retail AI Agent",
    description="LangGraph powered retail assistant by Sandeep",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class RetailState(TypedDict):
    customer_message: str
    intent: str
    customer_needs: str
    products: List[str]
    response: str
    quality: int
    attempts: int
    steps: List[str]

def classify(state: RetailState) -> RetailState:
    result = llm.invoke(f"""
    Classify this retail customer message into ONE:
    complaint, product_question, order_status, 
    return_request, shopping_help, general
    
    Message: {state['customer_message']}
    Reply with ONLY the category.
    """)
    intent = result.content.strip().lower()
    steps = state['steps'] + [f"✅ Classified as: {intent}"]
    logger.info(f"🎯 Intent: {intent}")
    return {**state, "intent": intent, "steps": steps}


def analyze_needs(state: RetailState) -> RetailState:
    result = llm.invoke(f"""
    Extract key shopping needs from this message.
    What do they want? Budget? Preferences?
    Message: {state['customer_message']}
    Be brief - 2-3 bullet points max.
    """)

def analyze_needs(state: RetailState) -> RetailState:
    result = llm.invoke(f"""
    Extract key shopping needs from this message.
    What do they want? Budget? Preferences?
    Message: {state['customer_message']}
    Be brief - 2-3 bullet points max.
    """)
    steps = state['steps'] + ["✅ Analyzed customer needs"]
    return {**state, "customer_needs": result.content, "steps": steps}


def find_products(state: RetailState) -> RetailState:
    result = llm.invoke(f"""
    Suggest 3 specific retail products for these needs:
    {state['customer_needs']}
    Format: Product - €Price - Benefit
    """)
    products = [p for p in result.content.strip().split('\n') if p.strip()]
    steps = state['steps'] + [f"✅ Found {len(products)} products"]
    return {**state, "products": products, "steps": steps}

def generate_response(state:RetailState)-> RetailState:
    products_text= '\n'.join(state.get('products',[]))
    context = f"Customer needs: {state.get('customer_needs', '')}\nProducts: {products_text}" if products_text else ""
    result = llm.invoke(f"""
    You are a helpful retail AI assistant.
    Respond to this customer professionally and warmly.
    {context}
     Customer message: {state['customer_message']}
    Intent: {state['intent']}
    Keep response under 150 words. Be specific and helpful.
    """)

    attempts=state["attempts"]+1
    steps=state["steps"]+[f"✅ Generated response (attempt {attempts})"]
    return {**state, "response": result.content, "attempts": attempts, "steps": steps}

def check_quality(state: RetailState) -> RetailState:
    result = llm.invoke(f"""
    Rate this customer service response 1-10.
    Check: helpfulness, professionalism, relevance.
    Response: {state['response']}
    Reply with ONLY a number.
    """)
    try:
        score = int(result.content.strip())
    except:
        score = 7

    steps = state['steps'] + [f"✅ Quality score: {score}/10"]
    logger.info(f"⭐ Quality: {score}/10")
    return {**state, "quality": score, "steps": steps}

def route_intent(state:RetailState)->str:
    intent=state['intent']
    if intent in ['shopping_help', 'product_question']:
        return "needs_products"
    return "direct_response"

def route_quality(state: RetailState) -> str:
    if state['quality'] >= 7 or state['attempts'] >= 3:
        return "done"
    return "retry"

workflow = StateGraph(RetailState)

workflow.add_node("classify", classify)
workflow.add_node("analyze_needs", analyze_needs)
workflow.add_node("find_products", find_products)
workflow.add_node("generate_response", generate_response)
workflow.add_node("check_quality", check_quality)
workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route_intent,
    {
        "needs_products": "analyze_needs",
        "direct_response": "generate_response"
    }
)
workflow.add_edge("analyze_needs", "find_products")
workflow.add_edge("find_products", "generate_response")
workflow.add_edge("generate_response", "check_quality")

workflow.add_conditional_edges(
    "check_quality",
    route_quality,
    {
        "done": END,
        "retry": "generate_response"
    }
)

retail_agent = workflow.compile()
logger.info("✅ LangGraph Retail Agent ready!")

class ChatRequest(BaseModel):
    message: str
    username: str = "Customer"

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index_3.html", "r") as f:
        return f.read()

@app.get("/status")
def status():
    return {
        "app": "Retail AI Agent",
        "powered_by": "LangGraph + Groq",
        "built_by": "Sandeep Kumar Nayak",
        "status": "running",
        "time": datetime.now().strftime("%H:%M")
    }
@app.post("/chat")
async def chat(request:ChatRequest):
    try:
        logger.info(f"👤 {request.username}: {request.message[:50]}")
        result = retail_agent.invoke({
            "customer_message": request.message,
            "intent": "",
            "customer_needs": "",
            "products": [],
            "response": "",
            "quality": 0,
            "attempts": 0,
            "steps": []
        })

        return {
            "reply": result['response'],
            "intent": result['intent'],
            "steps": result['steps'],
            "quality": result['quality'],
            "attempts": result['attempts'],
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {
            "reply": "Sorry, I'm having trouble. Please try again!",
            "status": "error"
        }
    
@app.post("/stream")
async def stream_chat(request: ChatRequest):
    async def generate():   
         try:
            # Stream thinking steps
            steps_shown = set()
            yield f"data: {json.dumps({'type': 'thinking', 'content': '🤔 Processing your request...'})}\n\n"

            result = retail_agent.invoke({
                "customer_message": request.message,
                "intent": "",
                "customer_needs": "",
                "products": [],
                "response": "",
                "quality": 0,
                "attempts": 0,
                "steps": []
            })

            # Stream steps
            for step in result['steps']:
                yield f"data: {json.dumps({'type': 'step', 'content': step})}\n\n"

            words = result['response'].split(' ')
            for word in words:
                yield f"data: {json.dumps({'type': 'word', 'content': word + ' '})}\n\n"
            # Done
            yield f"data: {json.dumps({'type': 'done', 'intent': result['intent'], 'quality': result['quality']})}\n\n"

         except Exception as e:
             yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )     

             

    
    








    
