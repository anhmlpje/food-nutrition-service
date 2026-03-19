"""
NutriTrack MCP Server
Exposes NutriTrack API functionality as MCP tools,
allowing AI assistants like Claude to directly query
nutritional data, analyse recipes, and detect allergens.

Run with: python mcp_server.py
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Fix working directory to project root so database path resolves correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app import models
from app.utils.nutrition_calc import (
    compute_recipe_nutrition,
    infer_allergens,
    compute_nutrient_density_score,
    ALLERGEN_KEYWORDS,
)

# Initialise the MCP server
server = Server("nutritrack")


def get_db() -> Session:
    """Create a fresh database session for each tool call."""
    db = SessionLocal()
    return db


# ─── Tool Definitions ────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Register all available MCP tools."""
    return [
        Tool(
            name="search_ingredients",
            description=(
                "Search for ingredients by name in the NutriTrack database. "
                "Returns nutritional data including calories, protein, carbs, fat, "
                "fibre, and micronutrients per 100g."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Ingredient name or keyword to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_top_protein_ingredients",
            description=(
                "Returns the top N ingredients ranked by protein content per 100g. "
                "Useful for finding high-protein foods for meal planning."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top ingredients to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_top_caffeine_ingredients",
            description=(
                "Returns the top N ingredients ranked by caffeine content per 100g. "
                "Useful for identifying high-caffeine foods and beverages."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top ingredients to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="check_ingredient_allergens",
            description=(
                "Check which allergens are present in a specific ingredient. "
                "Detects: gluten, dairy, nuts, soy, egg, fish, shellfish."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient_name": {
                        "type": "string",
                        "description": "Name of the ingredient to check"
                    }
                },
                "required": ["ingredient_name"]
            }
        ),
        Tool(
            name="find_allergen_free_ingredients",
            description=(
                "Find ingredients that do not contain a specified allergen. "
                "Supported allergens: gluten, dairy, nuts, soy, egg, fish, shellfish."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "allergen": {
                        "type": "string",
                        "description": "Allergen to exclude (e.g. 'gluten', 'dairy', 'nuts')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["allergen"]
            }
        ),
        Tool(
            name="compare_ingredients",
            description=(
                "Compare the nutritional profiles of two ingredients side by side. "
                "Returns absolute values and percentage differences for all key nutrients."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient_name_1": {
                        "type": "string",
                        "description": "Name of the first ingredient"
                    },
                    "ingredient_name_2": {
                        "type": "string",
                        "description": "Name of the second ingredient"
                    }
                },
                "required": ["ingredient_name_1", "ingredient_name_2"]
            }
        ),
        Tool(
            name="analyse_recipe_nutrition",
            description=(
                "Calculate the full nutritional breakdown for a custom recipe. "
                "Provide a list of ingredients with quantities in grams. "
                "Returns macros, micronutrients, health score (0-100), "
                "dietary warnings, and detected allergens."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_name": {
                        "type": "string",
                        "description": "Name of the recipe"
                    },
                    "ingredients": {
                        "type": "array",
                        "description": "List of ingredients with quantities",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Ingredient name (must exist in database)"
                                },
                                "quantity_g": {
                                    "type": "number",
                                    "description": "Quantity in grams"
                                }
                            },
                            "required": ["name", "quantity_g"]
                        }
                    }
                },
                "required": ["recipe_name", "ingredients"]
            }
        ),
    Tool(
            name="get_top_nutrient_density",
            description=(
                "Returns the top N ingredients ranked by nutrient density score (0-100). "
                "The score rewards high protein, fibre, vitamins and minerals, "
                "while penalising excess sugar, sodium and cholesterol. "
                "Based on NHS daily reference values. "
                "Useful for identifying the most nutritionally valuable foods."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top ingredients to return (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
    ]


# ─── Tool Implementations ─────────────────────────────────────────────────────

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to the appropriate handler."""
    try:
        if name == "search_ingredients":
            return await _search_ingredients(arguments)
        elif name == "get_top_protein_ingredients":
            return await _get_top_protein(arguments)
        elif name == "get_top_caffeine_ingredients":
            return await _get_top_caffeine(arguments)
        elif name == "check_ingredient_allergens":
            return await _check_allergens(arguments)
        elif name == "find_allergen_free_ingredients":
            return await _find_allergen_free(arguments)
        elif name == "compare_ingredients":
            return await _compare_ingredients(arguments)
        elif name == "analyse_recipe_nutrition":
            return await _analyse_recipe(arguments)
        elif name == "get_top_nutrient_density":
            return await _get_top_nutrient_density(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        # Return error as text instead of crashing the server
        return [TextContent(type="text", text=f"Tool error: {str(e)}")]


async def _search_ingredients(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        query = args.get("query", "")
        limit = args.get("limit", 5)
        results = (
            db.query(models.Ingredient)
            .filter(models.Ingredient.name.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )
        if not results:
            return [TextContent(type="text", text=f"No ingredients found matching '{query}'.")]

        lines = [f"Found {len(results)} ingredient(s) matching '{query}':\n"]
        for ing in results:
            lines.append(
                f"• {ing.name} (ID: {ing.id})\n"
                f"  Calories: {ing.calories} kcal | Protein: {ing.protein}g | "
                f"Carbs: {ing.carbohydrate}g | Fat: {ing.fat}g | Fibre: {ing.fiber}g\n"
                f"  Sodium: {ing.sodium}mg | Calcium: {ing.calcium}mg | "
                f"Vitamin C: {ing.vitamin_c}mg\n"
                f"  Allergens: {ing.allergens or 'none detected'}\n"
            )
        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()


async def _get_top_protein(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        limit = args.get("limit", 10)
        results = (
            db.query(models.Ingredient)
            .order_by(models.Ingredient.protein.desc())
            .limit(limit)
            .all()
        )
        lines = [f"Top {limit} ingredients by protein content (per 100g):\n"]
        for i, ing in enumerate(results, 1):
            score = ing.protein / ing.calories * 100 if ing.calories > 0 else 0
            lines.append(
                f"{i}. {ing.name}\n"
                f"   Protein: {ing.protein}g | Calories: {ing.calories} kcal | "
                f"Efficiency score: {score:.1f}%\n"
            )
        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()


async def _get_top_caffeine(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        limit = args.get("limit", 10)
        results = (
            db.query(models.Ingredient)
            .filter(models.Ingredient.caffeine > 0)
            .order_by(models.Ingredient.caffeine.desc())
            .limit(limit)
            .all()
        )
        if not results:
            return [TextContent(type="text", text="No caffeinated ingredients found.")]

        lines = [f"Top {limit} ingredients by caffeine content (per 100g):\n"]
        for i, ing in enumerate(results, 1):
            lines.append(f"{i}. {ing.name} — {ing.caffeine}mg caffeine\n")
        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()


async def _check_allergens(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        name = args.get("ingredient_name", "")
        ingredient = (
            db.query(models.Ingredient)
            .filter(models.Ingredient.name.ilike(f"%{name}%"))
            .first()
        )
        if not ingredient:
            return [TextContent(type="text", text=f"Ingredient '{name}' not found in database.")]

        allergens = ingredient.allergens.split(",") if ingredient.allergens else []
        allergens = [a.strip() for a in allergens if a.strip()]

        if allergens:
            result = (
                f"Allergen report for '{ingredient.name}':\n"
                f"⚠️  Contains: {', '.join(allergens)}\n"
                f"Not suitable for people with {' or '.join(allergens)} allergies."
            )
        else:
            result = (
                f"Allergen report for '{ingredient.name}':\n"
                f"✅ No major allergens detected."
            )
        return [TextContent(type="text", text=result)]
    finally:
        db.close()


async def _find_allergen_free(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        allergen = args.get("allergen", "").lower()
        limit = args.get("limit", 10)

        if allergen not in ALLERGEN_KEYWORDS:
            supported = ", ".join(ALLERGEN_KEYWORDS.keys())
            return [TextContent(
                type="text",
                text=f"Unsupported allergen '{allergen}'. Supported: {supported}"
            )]

        results = (
            db.query(models.Ingredient)
            .filter(~models.Ingredient.allergens.contains(allergen))
            .limit(limit)
            .all()
        )

        lines = [f"Ingredients free from {allergen} (showing {len(results)}):\n"]
        for ing in results:
            lines.append(f"• {ing.name} — {ing.calories} kcal per 100g")
        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()


async def _compare_ingredients(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        name1 = args.get("ingredient_name_1", "")
        name2 = args.get("ingredient_name_2", "")

        ing1 = db.query(models.Ingredient).filter(
            models.Ingredient.name.ilike(f"%{name1}%")
        ).first()
        ing2 = db.query(models.Ingredient).filter(
            models.Ingredient.name.ilike(f"%{name2}%")
        ).first()

        if not ing1:
            return [TextContent(type="text", text=f"Ingredient '{name1}' not found.")]
        if not ing2:
            return [TextContent(type="text", text=f"Ingredient '{name2}' not found.")]

        fields = ["calories", "protein", "carbohydrate", "fat", "fiber", "sugars", "sodium"]
        lines = [f"Nutritional comparison (per 100g): {ing1.name} vs {ing2.name}\n"]
        lines.append(f"{'Nutrient':<20} {ing1.name:<25} {ing2.name:<25} Difference")
        lines.append("-" * 80)

        for field in fields:
            v1 = getattr(ing1, field) or 0.0
            v2 = getattr(ing2, field) or 0.0
            diff = v2 - v1
            diff_str = f"+{diff:.1f}" if diff > 0 else f"{diff:.1f}"
            lines.append(f"{field:<20} {v1:<25.1f} {v2:<25.1f} {diff_str}")

        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()


async def _analyse_recipe(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        recipe_name = args.get("recipe_name", "Custom Recipe")
        ingredient_list = args.get("ingredients", [])

        ingredients_with_qty = []
        not_found = []

        for item in ingredient_list:
            ing = db.query(models.Ingredient).filter(
                models.Ingredient.name.ilike(f"%{item['name']}%")
            ).first()
            if ing:
                ingredients_with_qty.append({
                    "ingredient": ing,
                    "quantity_g": item["quantity_g"]
                })
            else:
                not_found.append(item["name"])

        if not ingredients_with_qty:
            return [TextContent(type="text", text="No valid ingredients found in database.")]

        result = compute_recipe_nutrition(ingredients_with_qty)
        totals = result["totals"]

        lines = [
            f"Nutritional analysis for: {recipe_name}\n",
            f"{'─' * 40}",
            f"Calories:      {totals['calories']:.1f} kcal",
            f"Protein:       {totals['protein']:.1f}g",
            f"Carbohydrates: {totals['carbohydrate']:.1f}g",
            f"Fat:           {totals['fat']:.1f}g",
            f"Fibre:         {totals['fiber']:.1f}g",
            f"Sodium:        {totals['sodium']:.1f}mg",
            f"",
            f"Health Score:  {result['health_score']}/100",
            f"Allergens:     {', '.join(result['allergens']) if result['allergens'] else 'none detected'}",
            f"Warnings:      {'; '.join(result['warnings']) if result['warnings'] else 'none'}",
        ]

        if not_found:
            lines.append(f"\nNote: Could not find: {', '.join(not_found)}")

        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()

async def _get_top_nutrient_density(args: dict) -> list[TextContent]:
    db = get_db()
    try:
        limit = args.get("limit", 10)
        ingredients = db.query(models.Ingredient).all()

        scored = []
        for ing in ingredients:
            score = compute_nutrient_density_score(ing)
            if score > 0:
                scored.append({
                    "name": ing.name,
                    "score": score,
                    "calories": ing.calories,
                    "protein": ing.protein,
                    "fiber": ing.fiber,
                    "vitamin_c": ing.vitamin_c,
                    "iron": ing.iron,
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        scored = scored[:limit]

        lines = [f"Top {limit} ingredients by nutrient density score (0-100):\n"]
        for i, item in enumerate(scored, 1):
            lines.append(
                f"{i}. {item['name']} — Score: {item['score']}/100\n"
                f"   Calories: {item['calories']} kcal | Protein: {item['protein']}g | "
                f"Fibre: {item['fiber']}g | Vitamin C: {item['vitamin_c']}mg | "
                f"Iron: {item['iron']}mg\n"
            )
        return [TextContent(type="text", text="\n".join(lines))]
    finally:
        db.close()   


# ─── Entry Point ──────────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())