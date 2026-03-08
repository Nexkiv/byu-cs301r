import asyncio
import json
import sys
from pathlib import Path

import yaml
from openai import AsyncOpenAI

# Add class_material directory to Python path for imports
class_material_dir = Path(__file__).parent.parent / "class_material"
sys.path.insert(0, str(class_material_dir))

from run_agent import run_agent
from tools import ToolBox
from usage import print_usage

toolbox = ToolBox()


async def main(agent_config: Path):
    client = AsyncOpenAI()
    config = yaml.safe_load(agent_config.read_text())
    agents = {agent['name']: agent for agent in config['agents']}

    usage = []
    chat_history = []

    try:
        # Load Hoid facts from the fact file
        try:
            hoid_facts = Path(__file__).parent.joinpath("Hoid-fact-file.md").read_text()
        except FileNotFoundError:
            print("ERROR: Hoid-fact-file.md not found in the homework directory.", file=sys.stderr)
            return

        # Step 1: Historian agent asks for story details
        # Should ask for: story title, genre, plot description, and setting
        opener = await run_agent(
            client, toolbox, agents['historian'],
            "Greet the user like you are welcoming them to your library, "
            "ask the user to provide you with story details so you can find the story "
            "in which to search for the world hopper named Hoid",
            chat_history, usage
        )
        print(opener)
        story_input = input(">>> ").strip()
        if not story_input:
            return

        # Step 2: Clarity checker evaluates if story description needs clarification
        print("\nHmmmm, let me see...")
        clarity_input = json.dumps({"story_description": story_input})
        clarity_raw = await run_agent(
            client, toolbox, agents['clarity_checker'],
            clarity_input, [], usage
        )
        clarity = json.loads(clarity_raw)

        story_summary = clarity.get("story_summary", "").strip()
        is_clear = clarity.get("is_clear", False)
        questions = clarity.get("clarifying_questions", []) or []

        # Step 2b: Conditionally ask clarifying questions only if unclear
        clarifications = []
        if not is_clear and questions:
            print("\nAh, yes, I have just a few questions.")
            for q in questions[:5]:  # Max 5 questions
                # Should present the question {q} to the user naturally
                q_text = await run_agent(
                    client, toolbox, agents['historian'],
                    f"You want to make sure that you have the right story."
                    f"Phrase your question in a way that will maximize your ability to find the right story."
                    f"You will be passing this information onto a researcher so they can provide you with the "
                    f"necessary story information. Your only task is to make sure you have the right story."
                    f"Question to ask: {q}",
                    chat_history, usage
                )
                print(q_text)
                answer = input(">>> ").strip()
                clarifications.append({"question": q, "answer": answer})

        # Step 3: Research planner creates search tasks
        print("\nLet me get my assistants to find that for you.")
        planner_input = json.dumps({
            "story_description": story_input,
            "story_summary": story_summary,
            "clarifications": clarifications
        })
        planner_raw = await run_agent(
            client, toolbox, agents['research_planner'],
            planner_input, [], usage
        )
        planner = json.loads(planner_raw)
        search_tasks = planner.get("search_tasks", []) or []

        if not search_tasks:
            print("No search tasks returned. Cannot proceed.", file=sys.stderr)
            return

        # Step 4: Execute research tasks in parallel
        print(f"\nThere we go, you {len(search_tasks)} go get me information on this.")

        async def _run_research_task(task):
            task_json = json.dumps(task)
            research_raw = await run_agent(
                client, toolbox, agents['researcher'],
                task_json, [], usage
            )
            return json.loads(research_raw)

        research_summaries = await asyncio.gather(
            *[_run_research_task(task) for task in search_tasks]
        )

        # Step 5: Hoid-disguiser agent places Hoid in the story
        print("\nAh yes, this is the right volume")
        disguiser_input = json.dumps({
            "story_description": story_input,
            "story_summary": story_summary,
            "research_summaries": research_summaries,
            "hoid_facts": hoid_facts
        })
        disguise_raw = await run_agent(
            client, toolbox, agents['hoid_disguiser'],
            disguiser_input, [], usage
        )
        disguise = json.loads(disguise_raw)

        # Step 6: Historian presents final results
        print("\nHere it is...")
        presentation_input = json.dumps({
            "story": story_summary,
            "hoid_placement": disguise
        })
        # Should present the placement in an engaging narrative style
        # Explain: where Hoid appears, his disguise/name, role, and motives
        final_presentation = await run_agent(
            client, toolbox, agents['historian'],
            f"You now have an accurate account of where Hoid was in the story that the user asked about."
            f"Present the final story excerpt in a way that has narrative flair and makes it clear that your"
            f"information is accurate but also mysterious to the regular searchers of the archives."
            f"You want this response to be as short as possible, just the facts and nothing more."
            f"About one paragraph long."
            f" Data to present:\n{presentation_input}",
            chat_history, usage
        )

        print("\n" + final_presentation + "\n")

    finally:
        # Always print usage if any was collected
        if usage:
            print("\n" + "=" * 50)
            print("Token Usage Summary")
            print("=" * 50)
            print_usage(agents['historian']['model'], usage)


if __name__ == '__main__':
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'hoid_was_here.yaml'
    try:
        asyncio.run(main(Path(config_file)))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
