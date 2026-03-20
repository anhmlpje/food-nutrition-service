import asyncio

from mcp_server import call_tool, list_tools


def test_mcp_lists_expected_tools():
    tools = asyncio.run(list_tools())
    tool_names = {tool.name for tool in tools}
    expected = {
        "search_ingredients",
        "get_top_protein_ingredients",
        "get_top_caffeine_ingredients",
        "check_ingredient_allergens",
        "find_allergen_free_ingredients",
        "compare_ingredients",
        "analyse_recipe_nutrition",
        "get_top_nutrient_density",
    }
    assert expected.issubset(tool_names)
    assert len(tools) == 8


def test_mcp_search_tool_returns_text_response():
    result = asyncio.run(call_tool("search_ingredients", {"query": "chicken", "limit": 1}))
    assert result
    assert result[0].type == "text"
    assert isinstance(result[0].text, str)
    assert result[0].text


def test_mcp_unknown_tool_returns_safe_error_text():
    result = asyncio.run(call_tool("unknown_tool", {}))
    assert result
    assert "Unknown tool" in result[0].text
