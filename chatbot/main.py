from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
import os

# Configure the Gemma API key
os.environ["GEMMA_API_KEY"] = "AIzaSyAb6wQ5hIITUe3vG2NUEZIdp59vRJpDgKk"
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


# Define the Pydantic model for the request body
class UserInput(BaseModel):
    prompt: str


# Define the function to preprocess the user input
def preprocess_input(user_input):
    context = ("The following texts are just pre-information for you. "
               "When I say 'only reply to texts after this', then after that reply to it."
               "You are personal hair care companion for now, an AI language model to help people with Shampoos, "
               "conditioner, hair care, hair products. "
               "You are made by a team 'Snack Monsters'. "
               "We are discussing about hair care. You need to give detailed information for the shampoo, "
               "hair care and its ingredients, its benefits and drawbacks, and stuffs related to it like that when "
               "user asks for it. If people ask you for details of ingredients, make sure you do it properly. "
               "For general texts such as greetings or something like that, talk normally. "
               "When they ask related to shampoos, hair care and stuffs related to it, please be precise and helpful. "
               "But remember you are only there to help for shampoos. "
               "Be nice, gentle, polite and interactive and use emojis if you can. "
               "All these contexts doesn't mean be very strictly bounded by it, okay? "
               "Only reply to texts after this: "
               )

    # Join the context and user input into a single string
    conversation_history = f"{context} User: {user_input}"

    return conversation_history


@app.post("/generate")
async def generate_response(user_input: UserInput):
    # Preprocess the input
    preprocessed_text = preprocess_input(user_input.prompt)

    # Generate a response using the model
    response = model.generate_content(preprocessed_text)
    response_text = response.text

    # Return the response
    return {"response": response_text}
