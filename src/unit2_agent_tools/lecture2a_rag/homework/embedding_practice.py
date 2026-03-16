import argparse
import asyncio
from pathlib import Path

import numpy as np
from openai import AsyncOpenAI


async def embed(client: AsyncOpenAI, content: list[str] | str, batch_size: int = 2048) -> np.ndarray:
    """Create embeddings for the given content using OpenAI's embedding model.

    Handles batching for large inputs to stay within API limits.
    """
    if isinstance(content, str):
        content = [content]

    # If content fits in one batch, process it directly
    if len(content) <= batch_size:
        response = await client.embeddings.create(
            input=content,
            model='text-embedding-3-small'
        )
        return np.array([emb.embedding for emb in response.data])

    # Process in batches for large inputs
    all_embeddings = []
    num_batches = (len(content) + batch_size - 1) // batch_size
    for batch_num, i in enumerate(range(0, len(content), batch_size), 1):
        batch = content[i:i + batch_size]
        print(f"  Processing batch {batch_num}/{num_batches}...")
        response = await client.embeddings.create(
            input=batch,
            model='text-embedding-3-small'
        )
        batch_embeddings = [emb.embedding for emb in response.data]
        all_embeddings.extend(batch_embeddings)

    return np.array(all_embeddings)


def calculate_similarity(query_embedding: np.ndarray, content_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and content embeddings."""
    return (query_embedding @ content_embeddings.T).flatten()


def chunk_text(lines: list[str], chunk_size: int) -> list[str]:
    """Combine lines into chunks of approximately chunk_size characters.

    Args:
        lines: List of text lines
        chunk_size: Target size for each chunk in characters (0 means no chunking)

    Returns:
        List of text chunks
    """
    if chunk_size == 0:
        # No chunking, return lines as-is
        return lines

    chunks = []
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line)

        # If adding this line would exceed chunk_size, save current chunk and start new one
        if current_chunk and current_size + line_size + 1 > chunk_size:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size + 1  # +1 for newline

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


async def search_scripts(
        client: AsyncOpenAI,
        content_dir: Path,
        query: str,
        threshold: float = 0.32,
        chunk_size: int = 0
):
    """Search through movie script files using embedding similarity."""
    print(f"\n=== Searching movie scripts in {content_dir} ===\n")

    # Load script lines from text files
    script_lines = []
    for script_file in sorted(content_dir.glob('*.txt'), key=lambda f: f.name):
        lines = script_file.read_text().splitlines()
        # Filter out empty lines
        lines = [line.strip() for line in lines if line.strip()]
        script_lines.extend(lines)

    if not script_lines:
        print(f"No script lines found in {content_dir}")
        return []

    print(f"Loaded {len(script_lines)} script lines")

    # Apply chunking if specified
    if chunk_size > 0:
        script_chunks = chunk_text(script_lines, chunk_size)
        print(f"Chunked into {len(script_chunks)} chunks (target size: {chunk_size} chars)")
    else:
        script_chunks = script_lines
        print(f"No chunking applied")

    print(f"Creating embeddings...")

    # Embed all script chunks
    content_embeds = await embed(client, script_chunks)
    print(f"Embeddings shape: {content_embeds.shape}\n")

    # Search
    print(f"Query: '{query}'")
    print(f"Threshold: {threshold}\n")

    query_embed = await embed(client, query)
    scores = calculate_similarity(query_embed, content_embeds)

    # Filter by threshold
    hits_mask = scores > threshold
    hits = np.array(script_chunks)[hits_mask]
    hit_scores = scores[hits_mask]

    # Sort by score
    sorted_indices = np.argsort(hit_scores)[::-1]
    hits = hits[sorted_indices]
    hit_scores = hit_scores[sorted_indices]

    print(f"Found {len(hits)} matches:\n")
    for chunk, score in zip(hits, hit_scores):
        print(f"[{score:.3f}] {chunk}\n")

    return hits


async def main(query: str, threshold: float, content_dir: str, chunk_size: int):
    """Run the embedding workflow demonstration."""
    client = AsyncOpenAI()

    # Search movie scripts (if data directory exists)
    dir_path = Path(content_dir)
    if dir_path.exists():
        await search_scripts(
            client,
            dir_path,
            query=query,
            threshold=threshold,
            chunk_size=chunk_size
        )
    else:
        print(f"\n=== Movie Script Search Demo ===")
        print(f"Skipping script search - directory not found: {dir_path}")
        print("To enable this demo, update the content_dir path in the script.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Search movie scripts using semantic similarity'
    )
    parser.add_argument(
        'query',
        type=str,
        help='Search query (e.g., "computer program")'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.32,
        help='Similarity threshold (0.0 to 1.0, default: 0.32)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=0,
        help='Chunk size in characters (0 = no chunking, use individual lines, default: 0)'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default='../../../shared/text/movies/',
        help='Directory containing movie scripts (default: ../../../shared/text/movies/)'
    )

    args = parser.parse_args()
    asyncio.run(main(args.query, args.threshold, args.dir, args.chunk_size))
