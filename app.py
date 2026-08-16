import streamlit as st
import google.generativeai as genai
import json
import re

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(page_title="AI Diet Planner", page_icon="🥗", layout="centered")

st.title("🥗 AI Diet Planner")
st.caption("Enter your details and get a personalized daily meal plan powered by Gemini.")

# ---------------------------------------------------------
# API key handling
# Priority: st.secrets (for deployed app) -> sidebar input (for local/testing)
# ---------------------------------------------------------
try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    api_key = None

with st.sidebar:
    st.header("Settings")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password",
                                 help="Get one free at https://aistudio.google.com/apikey")
    else:
        st.success("API key loaded from secrets ✅")
    model_name = st.selectbox(
    "Model",
    ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"],
    index=0
)

# ---------------------------------------------------------
# Input form
# ---------------------------------------------------------
with st.form("diet_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=10, max_value=100, value=18)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=68.0, step=0.5)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=170.0, step=0.5)
    with col2:
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        goal = st.selectbox("Goal", ["Bulk", "Weight Gain", "Weight Loss"])
        activity = st.selectbox(
            "Activity Level",
            ["Sedentary (little no exercise)", "Light (1-3 days per week)",
             "Moderate (3-5 days per week)", "Active (6-7 days per week)", "Very Active (athlete)"],
            index=2
        )

    restrictions = st.text_input(
        "Dietary restrictions / allergies (optional)",
        placeholder="e.g. vegetarian, no dairy, peanut allergy"
    )

    submitted = st.form_submit_button("Generate Plan", use_container_width=True)

# ---------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------
SYSTEM_PROMPT = """You are a certified nutrition and fitness assistant. Your job is to generate a safe, practical, and personalized daily diet plan based on the user's inputs.

Instructions:
1. Estimate the user's approximate daily calorie needs using their age, weight, height, sex, and activity level (use a standard BMR formula such as Mifflin-St Jeor, then apply an activity multiplier). State the assumption you used.
2. Adjust calories appropriately for the goal:
   - Bulk: calorie surplus + high protein for muscle gain
   - Weight Gain: moderate calorie surplus, balanced macros
   - Weight Loss: calorie deficit, higher protein to preserve muscle
3. Respect any stated dietary restrictions or allergies completely — never include excluded ingredients.
4. Create a full-day meal plan with: Breakfast, Mid-morning snack, Lunch, Evening snack, Dinner.
5. For each meal, include: food items, approximate portion size, and estimated calories.
6. Add a summary showing total daily calories and approximate protein/carbs/fats split (in grams).
7. Keep the plan realistic, affordable, and easy to prepare (no exotic ingredients).

Output ONLY valid JSON (no markdown fences, no extra text) matching exactly this schema:
{
  "calorie_estimate_note": "string explaining the BMR/TDEE assumption",
  "daily_calories": number,
  "macros": {"protein_g": number, "carbs_g": number, "fats_g": number},
  "meals": [
    {"name": "Breakfast", "items": [{"food": "string", "portion": "string", "calories": number}]},
    {"name": "Mid-morning snack", "items": [...]},
    {"name": "Lunch", "items": [...]},
    {"name": "Evening snack", "items": [...]},
    {"name": "Dinner", "items": [...]}
  ]
}
"""

def build_user_prompt():
    return f"""
Age: {age}
Weight: {weight} kg
Height: {height} cm
Sex: {sex}
Goal: {goal}
Activity Level: {activity}
Dietary restrictions: {restrictions if restrictions.strip() else "None"}
"""

def extract_json(text):
    """Strip markdown fences if the model adds them despite instructions."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return json.loads(text)

# ---------------------------------------------------------
# Call Gemini + render
# ---------------------------------------------------------
if submitted:
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    genai.configure(api_key=api_key)

    with st.spinner("Generating your plan..."):
        try:
            model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(build_user_prompt())
            plan = extract_json(response.text)
        except json.JSONDecodeError:
            st.error("The model returned an unexpected format. Please try again.")
            st.text(response.text if 'response' in locals() else "No response")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    st.success("Here's your personalized plan 👇")

    st.info(plan.get("calorie_estimate_note", ""))

    m1, m2 = st.columns(2)
    m1.metric("Daily Calories", f"{plan['daily_calories']} kcal")
    macros = plan.get("macros", {})
    m2.write(
        f"**Protein:** {macros.get('protein_g', '-')} g  \n"
        f"**Carbs:** {macros.get('carbs_g', '-')} g  \n"
        f"**Fats:** {macros.get('fats_g', '-')} g"
    )

    st.divider()

    for meal in plan.get("meals", []):
        st.subheader(meal["name"])
        for item in meal.get("items", []):
            st.write(f"- **{item['food']}** — {item['portion']} ({item['calories']} kcal)")

    st.divider()
    st.caption("⚠️ This is a general AI-generated suggestion, not a substitute for professional medical or dietary advice.")
