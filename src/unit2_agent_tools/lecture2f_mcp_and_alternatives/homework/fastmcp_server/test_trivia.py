import asyncio

from fastmcp import Client


async def test():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        # Test 1: Random fact (no args)
        result = await client.call_tool("get_random_fact")
        print("Random fact:", result.structured_content)

        # Test 2: Category-specific fact
        result = await client.call_tool("get_fact_about", {"category": "ducktales"})
        print("DuckTales fact:", result.structured_content)

        # Test 3: Invalid category (error handling)
        result = await client.call_tool("get_fact_about", {"category": "sports"})
        print("Bad category:", result.structured_content)


if __name__ == "__main__":
    asyncio.run(test())
