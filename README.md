# 🥗🔥 ProperFood — Built So My Friend Can Flex in Front of His Girlfriend

> **Hacktoberfest Week 0 ("Build for a Friend") Submission: An autonomous, parallel 3-agent AI culinary wingman powered by Google Gemini / Gemma and FastAPI.**

---

## 💡 The Story: Operation "Chef Boyfriend"

My best friend recently started dating someone awesome and wanted to pull off the ultimate flex: **cooking her a restaurant-quality meal from scratch at his apartment** instead of ordering Zomato/Swiggy again.

There were just two tiny problems:
1. **His Cooking Skills:** His culinary repertoire begins and ends with boiling water and making Maggi.
2. **Her Severe Food Allergies:** His girlfriend has strict food allergies (peanuts, tree nuts, lactose/dairy, and shellfish)—meaning one wrong sauce or hidden ingredient turns a romantic date night into an emergency room visit.

He was panicking, staring at 8 random ingredients in his fridge on a student budget. So, being a good bro, **I built ProperFood for him.** 

Now, he types in whatever ingredients he has in his kitchen, locks in her exact allergies, and in **6 seconds**, ProperFood's 3 AI agents hand him a 3-course allergy-safe menu, a clinical food-safety cheat sheet so he sounds like a pro nutritionist, and a smart grocery/prep list. **Result: Maximum chef flex, 0% allergic reactions.**

---

## 🧠 Parallel 3-Agent "Wingman" Architecture

ProperFood uses Python's `ThreadPoolExecutor` to run three specialized AI agents simultaneously:

1. **🍲 Agent 01 — The Date-Night Personal Chef (`agent_safe_recipes`)**
   * Turns random apartment/hostel pantry leftovers into 3 impressive, step-by-step meals (Quick Bite, Power Lunch, and Comfort Dinner) while guaranteeing **0% use of any listed allergen**.
2. **🛡️ Agent 02 — Clinical Allergen & Macro Auditor (`agent_safety_nutrition_audit`)**
   * Outputs strict JSON rendered into visual safety cards so he can casually flex his nutrition knowledge:
     * `safety_verdict`: Instant CLEAR / CAUTION verification.
     * `allergens_blocked`: Excluded allergens + sneaky packaging names to avoid at the store.
     * `safe_substitutions`: 1-to-1 safe chef swaps (e.g., swapping heavy cream for coconut cream or oat milk).
     * `cross_contamination_warnings`: Kitchen prep rules (like wiping down cutting boards) so he keeps her 100% safe.
     * `estimated_macros_per_serving`: Full Calorie, Protein, Carb, and Healthy Fat breakdown.
3. **🛒 Agent 03 — Smart Grocery & 60-Min Prep Coach (`agent_smart_grocery_prep`)**
   * Generates a budget-friendly categorized grocery list (only what he doesn't already have), a 3-point label-reading cheat sheet, and a **60-minute batch-prep timeline** so the kitchen is spotless before she arrives.

---

## 🛠️ Tech Stack

* **AI Engine:** Google Generative Language API (supports open-weight `gemma-3-27b-it` and `gemini-2.5-flash` via `.env`)
* **Backend & Concurrency:** Python 3, FastAPI, Uvicorn, Pydantic, `concurrent.futures.ThreadPoolExecutor`, `requests.Session` connection pooling
* **Frontend UI:** HTML5, Tailwind CSS, Culinary Emerald Glassmorphism, 1-click allergen chips, and a zero-dependency Markdown renderer

---

## ⚡ Quick Start Guide

### 1. Clone & Install Dependencies
```bash
git clone [https://github.com/YOUR_USERNAME/properfood.git](https://github.com/YOUR_USERNAME/properfood.git)
cd properfood
pip install -r requirements.txt
