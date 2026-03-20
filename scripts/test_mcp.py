"""
Smoke-test script for NutriTrack MCP Server tools.
Demonstrates all 8 MCP tools without requiring Claude Desktop.
Run with: python scripts/test_mcp.py
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import (
    _analyse_recipe,
    _check_allergens,
    _compare_ingredients,
    _find_allergen_free,
    _get_top_caffeine,
    _get_top_nutrient_density,
    _get_top_protein,
    _search_ingredients,
    list_tools,
)


EXPECTED_TOOL_COUNT = 8


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


async def run_tests():
    print("=" * 60)
    print("NutriTrack MCP Server Smoke Test")
    print("=" * 60)

    print("\n0. SERVER TOOL REGISTRATION")
    print("-" * 40)
    tools = await list_tools()
    _require(len(tools) == EXPECTED_TOOL_COUNT, f"Expected {EXPECTED_TOOL_COUNT} tools, got {len(tools)}")
    print(f"Registered {len(tools)} tools successfully.")

    print("\n1. SEARCH INGREDIENTS: 'chicken'")
    print("-" * 40)
    result = await _search_ingredients({"query": "chicken", "limit": 3})
    _require(result and result[0].text, "search_ingredients returned empty output")
    print(result[0].text)

    print("\n2. TOP PROTEIN INGREDIENTS")
    print("-" * 40)
    result = await _get_top_protein({"limit": 5})
    _require(result and result[0].text, "get_top_protein returned empty output")
    print(result[0].text)

    print("\n3. TOP CAFFEINE INGREDIENTS")
    print("-" * 40)
    result = await _get_top_caffeine({"limit": 5})
    _require(result and result[0].text, "get_top_caffeine returned empty output")
    print(result[0].text)

    print("\n4. CHECK ALLERGENS: 'pecans'")
    print("-" * 40)
    result = await _check_allergens({"ingredient_name": "pecans"})
    _require(result and result[0].text, "check_allergens returned empty output")
    print(result[0].text)

    print("\n5. FIND ALLERGEN-FREE: exclude 'gluten'")
    print("-" * 40)
    result = await _find_allergen_free({"allergen": "gluten", "limit": 5})
    _require(result and result[0].text, "find_allergen_free returned empty output")
    print(result[0].text)

    print("\n6. COMPARE INGREDIENTS: 'chicken' vs 'salmon'")
    print("-" * 40)
    result = await _compare_ingredients({
        "ingredient_name_1": "chicken breast",
        "ingredient_name_2": "salmon",
    })
    _require(result and result[0].text, "compare_ingredients returned empty output")
    print(result[0].text)

    print("\n7. ANALYSE RECIPE: Oatmeal Breakfast")
    print("-" * 40)
    result = await _analyse_recipe({
        "recipe_name": "Oatmeal Breakfast",
        "ingredients": [
            {"name": "oats", "quantity_g": 80},
            {"name": "whole milk", "quantity_g": 200},
        ],
    })
    _require(result and result[0].text, "analyse_recipe_nutrition returned empty output")
    print(result[0].text)

    print("\n8. TOP NUTRIENT DENSITY INGREDIENTS")
    print("-" * 40)
    result = await _get_top_nutrient_density({"limit": 5})
    _require(result and result[0].text, "get_top_nutrient_density returned empty output")
    print(result[0].text)

    print("\n" + "=" * 60)
    print("All MCP smoke checks passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_tests())
