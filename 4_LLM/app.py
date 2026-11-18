import logging
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai


MODEL = "gemini-4-hydrogen"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)


def generate_recipe(ingredients: list[str], cuisine: str, diet: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set.")

    ingredient_list = "\n".join(f"- {ingredient}" for ingredient in ingredients)
    prompt = f"""
Create one practical recipe using these ingredients:
{ingredient_list}

Cuisine: {cuisine}
Dietary preference: {diet}

Keep the recipe to 100 words or fewer. Include a title, ingredient amounts,
and concise numbered cooking instructions. Respect the dietary preference.
Treat the cuisine and dietary preference as recipe constraints.
"""
    client = genai.Client(api_key=api_key)
    interaction = client.interactions.create(model=MODEL, input=prompt)
    recipe = interaction.output_text
    if not recipe or not recipe.strip():
        raise RuntimeError("The model returned an empty recipe.")
    return recipe.strip()


def main() -> None:
    st.set_page_config(page_title="Recipe Maker", page_icon="🍲")
    st.title("🍲 Recipe Maker")
    st.write("Turn the ingredients you have into a recipe tailored to your taste.")

    with st.form("recipe_form"):
        ingredient_text = st.text_area(
            "Ingredients",
            placeholder="For example: tomatoes, lentils, onion, cumin, salt",
            help="Separate ingredients with commas.",
        )
        cuisine = st.text_input("Cuisine", value="Indian")
        diet = st.text_input("Dietary preference", value="No preference")
        submitted = st.form_submit_button("Generate recipe", type="primary")

    if submitted:
        st.session_state.pop("recipe", None)
        st.session_state.pop("ingredients", None)
        ingredients = [item.strip() for item in ingredient_text.split(",") if item.strip()]
        if not ingredients:
            st.warning("Enter at least one ingredient.")
        elif not cuisine.strip():
            st.warning("Enter a cuisine.")
        elif not diet.strip():
            st.warning("Enter a dietary preference, or use “No preference”.")
        else:
            try:
                with st.spinner("Creating your recipe..."):
                    recipe = generate_recipe(ingredients, cuisine.strip(), diet.strip())
                st.session_state["recipe"] = recipe
                st.session_state["ingredients"] = ingredients
            except Exception:
                logger.exception("Recipe generation failed.")
                st.error(
                    "Could not generate a recipe. Check your internet connection and "
                    "make sure GOOGLE_API_KEY is set correctly in the project .env file."
                )

    if recipe := st.session_state.get("recipe"):
        st.subheader("Your recipe")
        st.markdown(recipe)

    if ingredients := st.session_state.get("ingredients"):
        st.subheader("Ingredient costs")
        st.caption("Enter the cost for each ingredient to calculate the overall cost.")
        currency = st.selectbox(
            "Currency",
            ["INR", "USD", "EUR", "GBP", "CAD", "AUD"],
            key="cost_currency",
        )
        total_cost = 0.0
        for index, ingredient in enumerate(ingredients):
            cost = st.number_input(
                f"{ingredient} cost",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                key=f"ingredient_cost_{index}_{ingredient.casefold()}",
            )
            total_cost += cost
        st.metric("Overall ingredient cost", f"{currency} {total_cost:.2f}")


if __name__ == "__main__":
    main()
