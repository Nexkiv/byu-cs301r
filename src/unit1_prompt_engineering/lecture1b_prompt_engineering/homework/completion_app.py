import argparse
import sys
from pathlib import Path
from time import time

import yaml
from openai import AsyncOpenAI

# Add class_material directory to Python path for imports
class_material_dir = Path(__file__).parent.parent / "class_material"
sys.path.insert(0, str(class_material_dir))

from usage import print_usage

import json


def pretty_print_json(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            print("Invalid JSON string!")
            return

    formatted = json.dumps(data, indent=4, sort_keys=True)
    print(formatted)


async def main(model: Path, prompt: str):
    client = AsyncOpenAI()
    agent = yaml.safe_load(model.read_text())
    start = time()
    response = await client.responses.create(
        input=prompt,
        model=agent.get('model', 'gpt-5-mini'),
        **agent.get('kwargs', {})
    )
    print(pretty_print_json(response.output_text))

    print(f'{round(time() - start, 2)} seconds elapsed', file=sys.stderr)
    print_usage(model, response.usage)


# Launch app
if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser('AI Response')
    parser.add_argument('prompt_file', type=Path)
    parser.add_argument('--model', default='llm.yaml', type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.model, args.prompt_file.read_text()))
