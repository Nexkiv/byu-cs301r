"""
Simple embedding similarity comparison tool.
"""

import asyncio
import numpy as np
from openai import AsyncOpenAI


async def embed(client: AsyncOpenAI, content: str) -> np.ndarray:
    """Create embedding for text."""
    response = await client.embeddings.create(
        input=[content],
        model='text-embedding-3-small'
    )
    return np.array(response.data[0].embedding)


def similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings."""
    return float(np.dot(emb1, emb2))


async def main():
    client = AsyncOpenAI()

    print("\nEmbedding Similarity Comparison")
    print("=" * 50)

    while True:
        # Get texts from user
        text1 = input("\nText 1: ").strip()

        if text1 == '' or text1 == '/exit':
            break

        text2 = input("Text 2: ").strip()

        # Create embeddings
        print("\nCreating embeddings...")
        emb1 = await embed(client, text1)
        emb2 = await embed(client, text2)

        # Calculate and show similarity
        sim = similarity(emb1, emb2)

        print("\n" + "=" * 50)
        print(f"Similarity: {sim:.4f}")
        print("=" * 50)

        # Visual bar
        bar = int(sim * 50)
        print(f"[{'█' * bar}{'░' * (50 - bar)}]")
        print("=" * 50)


if __name__ == '__main__':
    asyncio.run(main())
