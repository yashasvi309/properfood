from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

import allergy_planner as planner

app = FastAPI(title="ProperFood | Gemini AI Allergy-Safe Meal Planner")

templates = Jinja2Templates(directory="templates")


class MealPlanRequest(BaseModel):
    friend_name: str = "My Friend"
    allergies: str
    dietary_goals: str
    pantry_items: str
    budget_level: str = "Student / Budget-Friendly"


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/plan")
def generate_meal_plan(request: MealPlanRequest):
    """
    Executes the 3-agent ProperFood pipeline on Google Gemini and returns
    structured outputs for Recipes, Safety/Macro Audit, and Smart Grocery List.
    """
    try:
        if not planner.validate_environment():
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY is missing in your .env file. Add your key from Google AI Studio.",
            )

        results = planner.run_allergy_pipeline(
            friend_name=request.friend_name,
            allergies=request.allergies,
            dietary_goals=request.dietary_goals,
            pantry_items=request.pantry_items,
            budget_level=request.budget_level,
        )

        if not results:
            raise HTTPException(
                status_code=500,
                detail="Gemini pipeline returned an empty response.",
            )

        return {
            "status": "success",
            "model": planner.GEMINI_MODEL,
            "data": results,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)