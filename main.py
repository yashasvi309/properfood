from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

import allergy_planner as planner

app = FastAPI(title="Allergy-Aware Meal Planner")
templates = Jinja2Templates(directory="templates")


class PlanRequest(BaseModel):
    friend_name: str
    allergies: str
    ingredients: str


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/plan")
async def create_plan(payload: PlanRequest):
    try:
        results = planner.run_planner_pipeline(
            friend_name=payload.friend_name,
            allergies=payload.allergies,
            ingredients=payload.ingredients
        )
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)