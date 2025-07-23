from fastapi import APIRouter, HTTPException, status, File, UploadFile, Form
from app.agents.food_agent import analyze_food_image
from typing import Optional

router = APIRouter(prefix="/food", tags=["Food Recognition"])

@router.post(
    "/analyze",
    summary="Analyze a food image from an upload or URL"
)
async def analyze_food(
    image_file: Optional[UploadFile] = File(None, description="An uploaded image file of the food."),
    image_url: Optional[str] = Form(None, description="A string containing the URL to an image of the food.")
):
    """
    Receives a food image either as a direct file upload or via a URL and returns
    a nutritional analysis.

    You must provide either `image_file` or `image_url`, but not both.
    """
    if not image_file and not image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either an image file or an image URL."
        )

    if image_file and image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either an image file or an image URL, not both."
        )

    try:
        analysis_result = ""
        if image_file:
            image_bytes = await image_file.read()
            if not image_bytes:
                 raise ValueError("The uploaded file is empty.")
            analysis_result = await analyze_food_image(image_bytes=image_bytes)
        else: # image_url must be present
            if not image_url or not image_url.strip():
                raise ValueError("Image URL is empty.")
            analysis_result = await analyze_food_image(image_url=image_url)
        
        return {"analysis": analysis_result}

    except ValueError as e:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during image analysis: {str(e)}"
        )