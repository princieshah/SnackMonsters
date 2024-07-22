from fastapi import FastAPI, Request
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from uuid import uuid4
import secrets

# Configure the Gemma API key
os.environ["GEMMA_API_KEY"] = "<API_KEY>"
genai.configure(api_key=os.environ['GEMMA_API_KEY'])

model = genai.GenerativeModel()

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

secret_key = secrets.token_hex(24)

# Add session middleware with a strong secret key
app.add_middleware(SessionMiddleware, secret_key=secret_key)

# In-memory session store
session_store = {}


# Define the Pydantic model for the request body
class UserInput(BaseModel):
    prompt: str


# Define the function to preprocess the user input
def preprocess_input(user_input, session_id):
    context = ("The following texts are just pre-information for you. "
               "When I say 'only reply to texts after this', then after that reply to it."
               "You are Gemma for now, an AI language model to help people with Shampoos, conditioner, hair care, "
               "hair products."
               "You are made by a team 'Snack Monsters'."
               "We are discussing about hair care. You need to give detailed information for the shampoo, "
               "hair care and its ingredients, its benefits and drawbacks, and stuffs related to it like that when "
               "user asks for it. If people ask you for details of ingredients, make sure you do it properly."
               "For general texts such as greetings or something like that, talk normally. "
               "When they ask related to shampoos, hair care and stuffs related to it, please be precise and helpful. "
               "But remember you are only there to help for shampoos. "
               "Be nice, gentle, polite and interactive and use emojis if you can. "
               "All these contexts doesn't mean be very strictly bounded by it, okay? "
               "Make sure to remember the conversations. "
               "To remember the previous conversations, look at the text with 'User:' "
               "which are the information that the user sent to you so that you will know what they are talking about"
               "Moreover, to look at the text with 'Gemma:', which are the information you sent to the user."
               "You don't have to type 'Gemma:' in your response."
               "Only reply to texts after this: "
               )

    if session_id not in session_store:
        session_store[session_id] = [context]

    # Append the new user input to the session history
    session_store[session_id].append(f"User: {user_input}")

    # Keep only the last 10 messages in the conversation history
    if len(session_store[session_id]) > 11:  # 10 user messages + context
        session_store[session_id] = session_store[session_id][-11:]

    # Join the session history into a single string
    conversation_history = " ".join(session_store[session_id])

    return conversation_history


@app.post("/generate")
async def generate_response(user_input: UserInput, request: Request):
    # Retrieve or create a session ID
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        request.session["session_id"] = session_id

    # Preprocess the input
    preprocessed_text = preprocess_input(user_input.prompt, session_id)

    # Generate a response using the model
    response = model.generate_content(preprocessed_text)
    response_text = response.text

    # Store the response in the session history
    session_store[session_id].append(f"Gemma: {response_text}")

    print(session_store[session_id])
    # Keep only the last 10 messages in the conversation history
    if len(session_store[session_id]) > 11:  # 10 messages + context
        session_store[session_id] = session_store[session_id][-11:]

    # Return the response
    return {"response": response_text}
