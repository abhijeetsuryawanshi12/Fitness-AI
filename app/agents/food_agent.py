from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
load_dotenv()

# Use a model that is explicitly designed for multi-modal inputs.
# gemini-1.5-flash-latest is a great, fast, and cost-effective choice for this task.
llm = init_chat_model(
        "gemini-2.0-flash", model_provider="google_genai",
        api_key=os.environ.get("GEMINI_API_KEY"), temperature=0.7
    )

output_parser = StrOutputParser()

async def analyze_food_image(image_bytes: bytes = None, image_url: str = None) -> str:
    """
    Analyzes a food image using a multimodal AI agent to identify the dish,
    its ingredients, and estimate its nutritional value.

    Args:
        image_bytes: The image data in bytes (for file uploads).
        image_url: The URL of the image.

    Returns:
        A string containing the food analysis.
    """
    if not image_bytes and not image_url:
        raise ValueError("Either image_bytes or image_url must be provided.")

    prompt_text = """You are an expert nutritionist and food recognition specialist. Analyze the provided image of a meal.

Based on the image, please provide the following information in a clear, easy-to-read markdown format:

1.  **Dish Name:** Identify the most likely name of the dish.
2.  **Key Ingredients:** List the primary ingredients you can identify.
3.  **Nutritional Assessment (Estimated per serving):**
    *   **Calories:** (e.g., 450-550 kcal)
    *   **Protein:** (e.g., 25-30g)
    *   **Carbohydrates:** (e.g., 40-50g)
    *   **Fat:** (e.g., 15-20g)
    *   **Fiber:** (e.g., 5-8g)
    *   **Key Vitamins & Minerals:** Briefly list any significant vitamins or minerals present (e.g., Vitamin C, Iron, Potassium).

**Disclaimer:** Please remember, this is an AI-generated estimation. For precise nutritional information, consult with a certified nutritionist or use a verified food database.

Respond ONLY with the analysis. Do not add any conversational text before or after the structured response.
"""

    image_message_part = {}
    if image_url:
        image_message_part = {
            "type": "image_url",
            "image_url": {"url": image_url}
        }
    else: # image_bytes
        # The Gemini API via LangChain can accept base64 encoded images.
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_message_part = {
            "type": "image_url",
            # The data URI format is `data:[<media type>][;base64],<data>`
            "image_url": f"data:image/jpeg;base64,{base64_image}"
        }

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_text},
            image_message_part
        ]
    )

    chain = llm | output_parser
    
    response = await chain.ainvoke([message])
    
    return response