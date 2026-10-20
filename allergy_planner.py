import os
import json
import time
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# =====================================================================
# 1. ARCHITECTURE & GEMINI ENVIRONMENT SETUP
# =====================================================================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
COOLDOWN_SECONDS = float(os.getenv("AGENT_COOLDOWN_SECONDS", "1"))

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)


# =====================================================================
# CORE GOOGLE GEMINI CLIENT & UTILITIES
# =====================================================================
def validate_environment() -> bool:
    """
    Verifies that GEMINI_API_KEY is present and not set to the placeholder value.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyYourActualGeminiApiKeyHere":
        return False
    return True


def query_gemini(
    system_instruction: str,
    user_prompt: str,
    temperature: float = 0.6,
    force_json: bool = False
) -> Optional[str]:
    """
    Sends a structured prompt to the Google Gemini API.

    Args:
        system_instruction (str): System persona and behavioral constraints.
        user_prompt (str): The task-specific input data.
        temperature (float): Sampling temperature for creativity vs. determinism.
        force_json (bool): Enforces application/json responseMimeType on Gemini.

    Returns:
        Optional[str]: The text response from Gemini, or None if the request fails.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    generation_config: Dict[str, Any] = {
        "temperature": temperature,
        "topP": 0.95,
    }

    # Native JSON mode for Gemini models
    if force_json and GEMINI_MODEL.startswith("gemini"):
        generation_config["responseMimeType"] = "application/json"

    payload: Dict[str, Any] = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}]
            }
        ],
        "generationConfig": generation_config,
    }

    try:
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()

        print(f"\n[ERROR] Unexpected Gemini response structure: {data}")
        return None

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Network connection failed while reaching Google Gemini API.")
        return None
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if http_err.response is not None else "Unknown"
        error_body = http_err.response.text if http_err.response is not None else str(http_err)
        print(f"\n[ERROR] Gemini API HTTP {status_code} Error: {error_body}")
        return None
    except Exception as e:
        print(f"\n[ERROR] Unexpected error querying Gemini: {e}")
        return None


def parse_llm_json(raw_output: str) -> Dict[str, Any]:
    """
    Robustly extracts and parses JSON from Gemini output, stripping Markdown
    code fences if present.
    """
    cleaned = raw_output.strip()

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
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON from Gemini safety auditor.",
            "details": str(e),
            "raw_response": raw_output
        }


# =====================================================================
# 2. SPECIALIZED AGENT IMPLEMENTATIONS
# =====================================================================

def agent_safe_recipes(
    friend_name: str,
    allergies: str,
    dietary_goals: str,
    pantry_items: str
) -> str:
    """
    Agent 1: Allergy-Safe Personal Chef.
    Designs 3 creative, 100% allergen-free meals tailored to the friend's
    available ingredients and dietary goals.
    """
    system_prompt = (
        "You are an expert Clinical Culinary Chef specializing in allergy-safe cooking. "
        "Your top priority is 100% strict allergen avoidance while creating delicious, "
        "practical meals.\n\n"
        "Create 3 distinct, mouth-watering recipes (Breakfast/Quick Bite, Power Lunch, and Comfort Dinner). "
        "For each recipe, include:\n"
        "- **Recipe Name & Prep Time**\n"
        "- **Why It's Safe:** Explicit note confirming zero use of the user's allergens.\n"
        "- **Ingredients List** (prioritizing their available pantry items).\n"
        "- **Step-by-Step Cooking Instructions**."
    )

    user_prompt = (
        f"Friend's Name: {friend_name}\n"
        f"STRICT ALLERGIES / INTOLERANCES (NEVER USE THESE): {allergies}\n"
        f"Dietary Goals & Preferences: {dietary_goals}\n"
        f"Available Fridge/Pantry Ingredients: {pantry_items}\n\n"
        "Generate the 3 allergy-safe recipes in clean Markdown now."
    )

    result = query_gemini(system_prompt, user_prompt, temperature=0.65)
    return result or "Agent 1 failed to generate allergy-safe recipes."


def agent_safety_nutrition_audit(
    allergies: str,
    dietary_goals: str,
    pantry_items: str
) -> Dict[str, Any]:
    """
    Agent 2: Clinical Allergen & Macro Auditor (JSON Output).
    Audits the ingredients for hidden allergen risks, cross-contamination,
    smart substitutions, and target macro breakdowns.
    """
    system_prompt = (
        "You are a Clinical Food Safety Auditor and Registered Dietitian. "
        "Analyze the user's allergies, dietary goals, and pantry items to produce "
        "a structured safety and nutrition audit.\n\n"
        "You MUST respond strictly in valid JSON format with these exact keys:\n"
        "{\n"
        '  "safety_verdict": "CLEAR / CAUTION status with a 1-sentence summary",\n'
        '  "allergens_blocked": "List of all excluded allergens and hidden derivatives to watch out for on labels",\n'
        '  "safe_substitutions": "Specific 1-to-1 safe swaps for the restricted ingredients",\n'
        '  "cross_contamination_warnings": "Practical kitchen & grocery label warnings for these specific allergies",\n'
        '  "estimated_macros_per_serving": "Target daily/per-meal Calorie, Protein, Carb, and Healthy Fat breakdown"\n'
        "}\n"
        "Return ONLY the raw JSON object."
    )

    user_prompt = (
        f"Strict Allergies: {allergies}\n"
        f"Dietary Goals: {dietary_goals}\n"
        f"Pantry Items: {pantry_items}\n\n"
        "Output the JSON safety and nutrition audit:"
    )

    raw_response = query_gemini(
        system_prompt,
        user_prompt,
        temperature=0.3,
        force_json=True
    )

    if not raw_response:
        return {"error": "Agent 2 failed to get a response from Gemini."}

    return parse_llm_json(raw_response)


def agent_smart_grocery_prep(
    friend_name: str,
    allergies: str,
    dietary_goals: str,
    pantry_items: str,
    budget_level: str
) -> str:
    """
    Agent 3: Smart Grocery & Sunday Meal-Prep Strategist.
    Builds a categorized, allergy-safe shopping list and a 60-minute batch prep guide.
    """
    system_prompt = (
        "You are a Smart Grocery & Meal-Prep Coach. Given a person's allergies, "
        "existing pantry items, and budget tier, generate:\n\n"
        "1. **🛒 Categorized Allergy-Safe Grocery List:** Organized by Produce, Proteins, "
        "Grains/Pantry, and Safe Snacks (only listing items they don't already have).\n"
        "2. **🏷️ Label-Reading Cheat Sheet:** 3 sneaky ingredient names to avoid on store packaging "
        "for their specific allergies.\n"
        "3. **⏱️ 60-Minute Sunday Batch-Prep Timeline:** A chronological step-by-step plan to prep "
        "containers for the week in one hour."
    )

    user_prompt = (
        f"Friend's Name: {friend_name}\n"
        f"Strict Allergies: {allergies}\n"
        f"Dietary Goals: {dietary_goals}\n"
        f"Already in Pantry: {pantry_items}\n"
        f"Weekly Budget Tier: {budget_level}\n\n"
        "Generate the Smart Grocery List and Meal-Prep Guide now."
    )

    result = query_gemini(system_prompt, user_prompt, temperature=0.6)
    return result or "Agent 3 failed to generate the grocery and meal-prep plan."


# =====================================================================
# 3. CENTRAL PIPELINE ORCHESTRATOR
# =====================================================================
def run_allergy_pipeline(
    friend_name: str,
    allergies: str,
    dietary_goals: str,
    pantry_items: str,
    budget_level: str = "Student / Budget-Friendly"
) -> Dict[str, Any]:
    """
    Runs all 3 ProperFood agents sequentially via Google Gemini and returns
    the structured results dictionary.
    """
    print("=" * 72)
    print(f"🥗 PROPERFOOD: 3-AGENT ALLERGY-SAFE MEAL PLANNER (FOR {friend_name.upper()})")
    print(f"🤖 Engine : Google Gemini ({GEMINI_MODEL})")
    print(f"🚫 Avoid  : {allergies}")
    print("=" * 72)

    if not validate_environment():
        raise RuntimeError(
            "GEMINI_API_KEY is missing or invalid in .env. "
            "Get a key from [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) and set GEMINI_API_KEY in your .env file."
        )

    results: Dict[str, Any] = {}

    print("▶️ [Agent 1/3] Crafting Allergy-Safe Recipes with Gemini...")
    results["safe_recipes"] = agent_safe_recipes(
        friend_name, allergies, dietary_goals, pantry_items
    )

    if COOLDOWN_SECONDS > 0:
        time.sleep(COOLDOWN_SECONDS)

    print("▶️ [Agent 2/3] Running Clinical Allergen & Nutrition Audit with Gemini...")
    results["safety_audit"] = agent_safety_nutrition_audit(
        allergies, dietary_goals, pantry_items
    )

    if COOLDOWN_SECONDS > 0:
        time.sleep(COOLDOWN_SECONDS)

    print("▶️ [Agent 3/3] Building Smart Grocery List & Prep Timeline with Gemini...")
    results["grocery_prep"] = agent_smart_grocery_prep(
        friend_name, allergies, dietary_goals, pantry_items, budget_level
    )

    print("🎉 PROPERFOOD GEMINI PIPELINE COMPLETE!")
    return results


if __name__ == "__main__":
    sample_output = run_allergy_pipeline(
        friend_name="Aarav",
        allergies="Peanuts, Tree Nuts, Dairy (Lactose), Shellfish",
        dietary_goals="High-protein (~120g/day), quick 20-minute hostel/apartment meals",
        pantry_items="Rice, eggs, canned chickpeas, spinach, garlic, olive oil, oats, tomatoes",
        budget_level="Student / Budget-Friendly"
    )
    print(json.dumps(sample_output, indent=2))