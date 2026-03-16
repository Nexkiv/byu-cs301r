import asyncio
from pathlib import Path

import numpy as np
from openai import AsyncOpenAI


async def embed(client: AsyncOpenAI, content: list[str] | str) -> np.ndarray:
    """Create embeddings for the given content using OpenAI's embedding model."""
    if isinstance(content, str):
        content = [content]

    response = await client.embeddings.create(
        input=content,
        model='text-embedding-3-small'
    )
    return np.array([emb.embedding for emb in response.data])


def calculate_similarity(query_embedding: np.ndarray, content_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and content embeddings."""
    return (query_embedding @ content_embeddings.T).flatten()


async def demonstrate_basic_similarity(client: AsyncOpenAI):
    """Demonstrate basic embedding similarity with simple phrases."""
    print("=== Basic Similarity Demo ===\n")

    phrases = [
        'hello', 'hi', 'good-bye', 'see ya later', 'moose',
        '1 + 1 = 2', '2 + 2 = 5', 'qperqoweirupqweor',
        '!@#$%^&*()_', 'def foobar(): return 7',
        'specificity', 'agent engineering', 'Utah'
    ]

    print(f"Embedding {len(phrases)} phrases...")
    embeds = await embed(client, phrases)
    print(f"Created embeddings with shape: {embeds.shape}\n")

    # Test query
    query_phrase = 'hola'
    print(f"Query phrase: '{query_phrase}'")
    query_embed = await embed(client, query_phrase)

    # Calculate similarities
    similarities = calculate_similarity(query_embed, embeds)

    # Show top matches
    print("\nSimilarity scores:")
    sorted_indices = np.argsort(similarities)[::-1]
    for idx in sorted_indices[:5]:
        print(f"  {phrases[idx]:20s} -> {similarities[idx]:.3f}")

    return phrases, embeds, query_phrase, query_embed


async def search_verses(
        client: AsyncOpenAI,
        content_dir: Path,
        query: str,
        threshold: float = 0.32
):
    """Search through text files using embedding similarity."""
    print(f"\n=== Searching verses in {content_dir} ===\n")

    # Load verses from text files
    content_verses = []
    for content_file in sorted(content_dir.glob('*.txt'), key=lambda f: f.name):
        verses = content_file.read_text().splitlines()
        # Filter out empty verses
        verses = [v.strip() for v in verses if v.strip()]
        content_verses.extend(verses)

    if not content_verses:
        print(f"No verses found in {content_dir}")
        return []

    print(f"Loaded {len(content_verses)} verses")
    print(f"Creating embeddings...")

    # Embed all verses
    content_embeds = await embed(client, content_verses)
    print(f"Embeddings shape: {content_embeds.shape}\n")

    # Search
    print(f"Query: '{query}'")
    print(f"Threshold: {threshold}\n")

    query_embed = await embed(client, query)
    scores = calculate_similarity(query_embed, content_embeds)

    # Filter by threshold
    hits_mask = scores > threshold
    hits = np.array(content_verses)[hits_mask]
    hit_scores = scores[hits_mask]

    # Sort by score
    sorted_indices = np.argsort(hit_scores)[::-1]
    hits = hits[sorted_indices]
    hit_scores = hit_scores[sorted_indices]

    print(f"Found {len(hits)} matches:\n")
    for verse, score in zip(hits, hit_scores):
        print(f"[{score:.3f}] {verse}\n")

    return hits


async def plot_similarity(
        phrases: list[str],
        embeds: np.ndarray,
        query_phrase: str,
        query_embed: np.ndarray
):
    """Plot similarity scores as a bar chart."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Skipping visualization.")
        return

    similarities = calculate_similarity(query_embed, embeds)

    plt.figure(figsize=(12, 6))
    plt.bar(x=range(len(phrases)), height=similarities)
    plt.xticks(
        range(len(phrases)),
        phrases,
        rotation=45,
        ha='right',
        rotation_mode='anchor'
    )
    plt.title(f'Embedding similarity for "{query_phrase}"')
    plt.ylabel('Similarity Score')
    plt.ylim([0, 1])
    plt.tight_layout()
    plt.savefig('embedding_similarity.png')
    print(f"\nSaved similarity plot to embedding_similarity.png")
    plt.close()


async def main():
    """Run the embedding workflow demonstration."""
    client = AsyncOpenAI()

    # Demo 1: Basic similarity
    phrases, embeds, query_phrase, query_embed = await demonstrate_basic_similarity(client)

    # Optional: Create visualization
    await plot_similarity(phrases, embeds, query_phrase, query_embed)

    # Demo 2: Search verses (if data directory exists)
    content_dir = Path('../../../shared/text/1_ne/')
    if content_dir.exists():
        await search_verses(
            client,
            content_dir,
            query='eat fruit',
            threshold=0.32
        )
    else:
        print(f"\n=== Verse Search Demo ===")
        print(f"Skipping verse search - directory not found: {content_dir}")
        print("To enable this demo, update the content_dir path in the script.")


if __name__ == '__main__':
    asyncio.run(main())
