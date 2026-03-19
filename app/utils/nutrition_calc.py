from typing import List, Dict, Any

# Allergen keyword mapping inferred from ingredient names
ALLERGEN_KEYWORDS = {
    "gluten": ["wheat", "barley", "rye", "bread", "pasta", "flour", "oat", "cereal", "cracker", "biscuit"],
    "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "whey", "lactose", "casein"],
    "nuts": ["nuts", "almond", "walnut", "pecan", "cashew", "pistachio", "hazelnut", "macadamia"],
    "soy": ["soy", "tofu", "miso", "tempeh", "edamame"],
    "egg": ["egg"],
    "fish": ["fish", "salmon", "tuna", "cod", "halibut", "sardine", "anchovy", "tilapia"],
    "shellfish": ["shrimp", "crab", "lobster", "oyster", "clam", "mussel", "scallop"],
}

# Daily reference values for health score calculation (based on NHS guidelines)
DAILY_REFERENCE = {
    "calories": 2000,
    "protein": 50,
    "carbohydrate": 260,
    "fat": 70,
    "fiber": 30,
    "sugars": 90,
    "sodium": 2300,
}

# Warning thresholds (per serving / recipe)
WARNING_THRESHOLDS = {
    "sodium": 600,      # mg - high sodium warning
    "sugars": 24,       # g - high sugar warning
    "fat": 26,          # g - high fat warning
    "calories": 800,    # kcal - high calorie warning
}


def infer_allergens(ingredient_name: str) -> List[str]:
    """Infer allergens from ingredient name using keyword matching."""
    name_lower = ingredient_name.lower()
    detected = []
    for allergen, keywords in ALLERGEN_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            detected.append(allergen)
    return detected


def compute_nutrient_density_score(ingredient) -> float:
    """
    Compute a nutrient density score (0-100) for a single ingredient.
    Higher score means more nutrients per calorie.
    Based on USDA nutrient profiling methodology.
    """
    if ingredient.calories == 0:
        return 0.0

    score = 0.0
    # Positive contributors (nutrients we want more of)
    score += min(ingredient.protein / 50 * 25, 25)       # protein: up to 25 points
    score += min(ingredient.fiber / 30 * 20, 20)         # fiber: up to 20 points
    score += min(ingredient.vitamin_c / 90 * 15, 15)     # vitamin C: up to 15 points
    score += min(ingredient.calcium / 1000 * 10, 10)     # calcium: up to 10 points
    score += min(ingredient.potassium / 3500 * 10, 10)   # potassium: up to 10 points
    score += min(ingredient.iron / 18 * 10, 10)          # iron: up to 10 points

    # Negative contributors (nutrients we want less of)
    score -= min(ingredient.sugars / 90 * 5, 5)          # excess sugar: up to -5 points
    score -= min(ingredient.sodium / 2300 * 5, 5)        # excess sodium: up to -5 points
    score -= min(ingredient.cholesterol / 300 * 5, 5)    # excess cholesterol: up to -5 points

    return round(max(0.0, min(100.0, score)), 2)


def compute_recipe_nutrition(ingredients_with_qty: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate total nutrition for a recipe given a list of
    ingredients and their quantities in grams.
    Returns totals, health score, warnings, and allergens.
    """
    totals = {
        "calories": 0.0,
        "protein": 0.0,
        "carbohydrate": 0.0,
        "fat": 0.0,
        "fiber": 0.0,
        "sugars": 0.0,
        "sodium": 0.0,
        "calcium": 0.0,
        "potassium": 0.0,
        "vitamin_c": 0.0,
        "vitamin_a": 0.0,
        "iron": 0.0,
        "caffeine": 0.0,
        "water": 0.0,
    }

    all_allergens = set()

    for item in ingredients_with_qty:
        ingredient = item["ingredient"]
        qty = item["quantity_g"]
        ratio = qty / 100.0  # All values stored per 100g

        for key in totals:
            value = getattr(ingredient, key, 0.0) or 0.0
            totals[key] += value * ratio

        # Collect allergens
        if ingredient.allergens:
            for allergen in ingredient.allergens.split(","):
                if allergen.strip():
                    all_allergens.add(allergen.strip())

    # Round all totals
    totals = {k: round(v, 2) for k, v in totals.items()}

    # Generate health warnings
    warnings = []
    if totals["sodium"] > WARNING_THRESHOLDS["sodium"]:
        warnings.append(f"High sodium ({totals['sodium']:.0f}mg) — exceeds 26% of daily limit")
    if totals["sugars"] > WARNING_THRESHOLDS["sugars"]:
        warnings.append(f"High sugar ({totals['sugars']:.1f}g) — exceeds recommended serving")
    if totals["fat"] > WARNING_THRESHOLDS["fat"]:
        warnings.append(f"High fat ({totals['fat']:.1f}g) — consider reducing portion size")
    if totals["calories"] > WARNING_THRESHOLDS["calories"]:
        warnings.append(f"High calorie ({totals['calories']:.0f} kcal) — large meal")
    if totals["caffeine"] > 200:
        warnings.append(f"High caffeine ({totals['caffeine']:.1f}mg) — exceeds recommended daily limit")

    # Compute overall health score (0-100)
    health_score = _compute_recipe_health_score(totals)

    return {
        "totals": totals,
        "health_score": health_score,
        "warnings": warnings,
        "allergens": sorted(list(all_allergens)),
    }


def _compute_recipe_health_score(totals: Dict[str, float]) -> float:
    """
    Compute a recipe health score from 0 to 100.
    Rewards high protein and fiber, penalises excess sodium, sugar, and fat.
    """
    score = 50.0  # Start at neutral

    # Positive: protein and fibre
    score += min(totals["protein"] / DAILY_REFERENCE["protein"] * 20, 20)
    score += min(totals["fiber"] / DAILY_REFERENCE["fiber"] * 15, 15)

    # Negative: excess sodium, sugar, fat
    if totals["sodium"] > WARNING_THRESHOLDS["sodium"]:
        score -= 15
    if totals["sugars"] > WARNING_THRESHOLDS["sugars"]:
        score -= 10
    if totals["fat"] > WARNING_THRESHOLDS["fat"]:
        score -= 10

    return round(max(0.0, min(100.0, score)), 1)