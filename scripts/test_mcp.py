"""
Manual test script for NutriTrack MCP Server tools.
Demonstrates all 7 MCP tools without requiring Claude Desktop.
Run with: python scripts/test_mcp.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from mcp_server import (
    _search_ingredients,
    _get_top_protein,
    _get_top_caffeine,
    _check_allergens,
    _find_allergen_free,
    _compare_ingredients,
    _analyse_recipe,
    _get_top_nutrient_density,
)

async def run_tests():
    print("=" * 60)
    print("NutriTrack MCP Server — Tool Demonstration")
    print("=" * 60)

    print("\n1. SEARCH INGREDIENTS: 'chicken'")
    print("-" * 40)
    result = await _search_ingredients({"query": "chicken", "limit": 3})
    print(result[0].text)

    print("\n2. TOP PROTEIN INGREDIENTS")
    print("-" * 40)
    result = await _get_top_protein({"limit": 5})
    print(result[0].text)

    print("\n3. TOP CAFFEINE INGREDIENTS")
    print("-" * 40)
    result = await _get_top_caffeine({"limit": 5})
    print(result[0].text)

    print("\n4. CHECK ALLERGENS: 'pecans'")
    print("-" * 40)
    result = await _check_allergens({"ingredient_name": "pecans"})
    print(result[0].text)

    print("\n5. FIND ALLERGEN-FREE: exclude 'gluten'")
    print("-" * 40)
    result = await _find_allergen_free({"allergen": "gluten", "limit": 5})
    print(result[0].text)

    print("\n6. COMPARE INGREDIENTS: 'chicken' vs 'salmon'")
    print("-" * 40)
    result = await _compare_ingredients({
        "ingredient_name_1": "chicken breast",
        "ingredient_name_2": "salmon"
    })
    print(result[0].text)

    print("\n7. ANALYSE RECIPE: Oatmeal Breakfast")
    print("-" * 40)
    result = await _analyse_recipe({
        "recipe_name": "Oatmeal Breakfast",
        "ingredients": [
            {"name": "oats", "quantity_g": 80},
            {"name": "whole milk", "quantity_g": 200},
        ]
    })
    print(result[0].text)

    print("\n8. TOP NUTRIENT DENSITY INGREDIENTS")
    print("-" * 40)
    result = await _get_top_nutrient_density({"limit": 5})
    print(result[0].text)

    print("\n" + "=" * 60)
    print("All MCP tools demonstrated successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())