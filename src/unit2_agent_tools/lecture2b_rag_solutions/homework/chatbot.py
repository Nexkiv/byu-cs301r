import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).parent.parent / "class_material"))
from chroma_demo import query_whole_documents
from usage import print_usage, format_usage_markdown

PROMPT_PATH = Path(__file__).parent / "prompt.md"


async def answer_question(client, model, system_prompt, chroma_dir, collection, question, n_results):
    docs = query_whole_documents(chroma_dir, collection, question, n_results)
    context = "\n\n---\n\n".join(f"[Document {i + 1}]\n{doc}" for i, doc in enumerate(docs))

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]

    response = await client.responses.create(model=model, input=messages)
    return response.output_text, response.usage


def save_chat(model, system_prompt, qa_pairs, usage_list):
    timestamp = datetime.now().strftime("%H-%M-%S")
    filename = f"chat_{timestamp}.md"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        "# Chat Session\n\n",
        f"**Model**: {model}\n",
        f"**Saved**: {now_str}\n",
        f"**Questions**: {len(qa_pairs)}\n",
        "\n## System Prompt\n\n",
        system_prompt,
        "\n\n## Conversation\n",
    ]

    for question, answer in qa_pairs:
        parts.append(f"\n**Question**: {question}\n\n**Answer**: {answer}\n")

    if usage_list:
        parts.append("\n## Usage Statistics\n\n")
        parts.append(format_usage_markdown(model, usage_list))

    with open(filename, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    return filename


async def main():
    parser = argparse.ArgumentParser(description="RAG chatbot backed by ChromaDB")
    parser.add_argument("--chroma-dir", default="./my_chroma_db")
    parser.add_argument("--collection", default="gc_2025")
    parser.add_argument("--model", default="gpt-5-nano")
    parser.add_argument("--n-results", type=int, default=3)
    args = parser.parse_args()

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()
    client = AsyncOpenAI()
    usage_list = []
    qa_pairs = []

    print("RAG Chatbot — type /save to save, /exit to quit, or press Enter to quit.\n")
    try:
        while True:
            question = input("Question: ").strip()
            if not question:
                break
            if question == "/exit":
                print("Goodbye!")
                break
            if question == "/save":
                filename = save_chat(args.model, system_prompt, qa_pairs, usage_list)
                print(f"Chat saved to: {filename}\n")
                continue

            answer, usage = await answer_question(
                client, args.model, system_prompt,
                args.chroma_dir, args.collection, question, args.n_results,
            )
            usage_list.append(usage)
            qa_pairs.append((question, answer))
            print(f"Answer: {answer}\n")
    except KeyboardInterrupt:
        print()

    if usage_list:
        print_usage(args.model, usage_list)


if __name__ == "__main__":
    asyncio.run(main())
