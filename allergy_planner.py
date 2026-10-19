import os
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def query_gemini(system_instruction: str, user_prompt: str, force_json: bool = False) -> Optional[str]:
    """Helper function to execute prompt requests using official Google GenAI SDK."""
    if not client:
        print("[ERROR] GEMINI_API_KEY is missing or invalid in your .env file.")
        return None

    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
        )
        if force_json:
            config.response_mime_type = "application/json"

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config=config
        )
        return response.text.strip() if response.text else None
    except Exception as e:
        print(f"[Gemini API Error] {e}")
        return None


def parse_json(raw_text: str) -> Dict[str, Any]:
    """Extracts and parses JSON from Gemini responses."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Failed to parse valid JSON", "raw_output": raw_text}


# --- AGENT 1: Safety & Meal Plan Architect ---
def agent_meal_plan(friend_name: str, allergies: str, ingredients: str) -> str:
    system_prompt = (
        "You are a clinical dietitian and meal planning expert specializing in severe food allergies. "
        "Your top priority is ABSOLUTE ALLERGEN SAFETY. Never include any ingredients or derivatives "
        "that violate the specified allergies.\n\n"
        "Design a 3-Day Meal Plan (Day 1, Day 2, Day 3) containing Breakfast, Lunch, and Dinner. "
        "Maximize the use of available ingredients, but feel free to suggest safe additional ingredients. "
        "Explicitly list allergen warnings for each meal."
    )
    user_prompt = f"Friend/Roommate Name: {friend_name}\nSevere Allergies/Restrictions: {allergies}\nAvailable Fridge Ingredients: {ingredients}"
    return query_gemini(system_prompt, user_prompt) or "Agent 1 failed to generate meal plan."


# --- AGENT 2: Recipe Detailer ---
def agent_recipes(meal_plan_summary: str, allergies: str) -> str:
    system_prompt = (
        "You are a professional chef specializing in allergy-safe cooking. "
        "Take the 3-day meal plan and provide detailed step-by-step recipes for each meal. "
        "For every recipe, include:\n"
        "1. Prep & Cook time\n"
        "2. Exact ingredients with safe allergy substitutes\n"
        "3. Step-by-step instructions\n"
        "4. Cross-contamination prevention tip"
    )
    user_prompt = f"Meal Plan Summary:\n{meal_plan_summary}\n\nStrict Allergies to avoid: {allergies}"
    return query_gemini(system_prompt, user_prompt) or "Agent 2 failed to generate recipes."


# --- AGENT 3: Grocery List Categorizer ---
def agent_grocery_list(meal_plan_text: str, available_ingredients: str, allergies: str) -> Dict[str, Any]:
    system_prompt = (
        "You are a smart grocery shopping assistant. Compare the required ingredients in the meal plan "
        "against the user's available fridge items. Identify missing items needed to complete the meals. "
        "You MUST respond in valid JSON format with this exact structure:\n"
        "{\n"
        '  "safe_items_to_buy": {\n'
        '     "produce": ["item1", "item2"],\n'
        '     "pantry_and_grains": ["item1"],\n'
        '     "proteins_and_dairy_alt": ["item1"]\n'
        '  },\n'
        '  "allergen_warning_notes": "Specific label-reading instructions for buying packaged goods safe from specified allergies"\n'
        "}"
    )
    user_prompt = f"Meal Plan:\n{meal_plan_text}\n\nAvailable Ingredients:\n{available_ingredients}\n\nAllergies:\n{allergies}"
    raw = query_gemini(system_prompt, user_prompt, force_json=True)
    return parse_json(raw) if raw else {"error": "Agent 3 failed."}


# --- Pipeline Orchestrator ---
def run_planner_pipeline(friend_name: str, allergies: str, ingredients: str) -> Dict[str, Any]:
    print(f"🚀 Running SafeBite Studio (Powered by Gemini) for {friend_name}...")
    
    # Step 1
    meal_plan = agent_meal_plan(friend_name, allergies, ingredients)
    time.sleep(1)
    
    # Step 2
    recipes = agent_recipes(meal_plan, allergies)
    time.sleep(1)
    
    # Step 3
    grocery_data = agent_grocery_list(meal_plan, ingredients, allergies)
    
    return {
        "friend_name": friend_name,
        "allergies": allergies,
        "meal_plan": meal_plan,
        "recipes": recipes,
        "grocery_list": grocery_data
    }