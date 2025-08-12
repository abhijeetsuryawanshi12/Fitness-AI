from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv  

# Load environment variables from .env file
load_dotenv()

# Initialize the language model
llm = init_chat_model("gemini-2.0-flash",
                      model_provider="google_genai",
                      api_key=os.environ.get("GEMINI_API_KEY"),
                      temperature=0.7)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful fitness coach. Keep your responses concise and encouraging."),
    ("human", "{input}"),
])

output_parser = StrOutputParser()

chain = prompt_template | llm | output_parser

async def generate_response(user_input: str) -> str:

    response = await chain.ainvoke(input=user_input)
    return response

if __name__ == "__main__":
    import asyncio

    async def main():
        user_input = "What should I eat for breakfast?"
        response = await generate_response(user_input)
        print(response)

    asyncio.run(main())