import random

from fastmcp import FastMCP

mcp = FastMCP("TriviaServer")

FACTS = {
    "science": [
        "Honey never spoils. Archaeologists have found 3,000-year-old honey in Egyptian tombs that was still edible.",
        "Octopuses have three hearts and blue blood.",
        "A teaspoon of a neutron star would weigh about 6 billion tons.",
        "Bananas are naturally radioactive due to their potassium content.",
    ],
    "history": [
        "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "Oxford University is older than the Aztec Empire.",
        "The shortest war in history lasted 38 minutes, between Britain and Zanzibar in 1896.",
        "Ancient Romans used crushed mouse brains as toothpaste.",
    ],
    "animals": [
        "A group of flamingos is called a 'flamboyance.'",
        "Cows have best friends and get stressed when separated.",
        "Sea otters hold hands while sleeping so they don't drift apart.",
        "The heart of a shrimp is located in its head.",
    ],
    "ducktales": [
        "John D. Rockerduck represents the inherited money billionaire, Scrooge represents the rags to riches \
        billionaire, Flintheart Glomgold represents the 'greed is good' billionaire, and Mark Beaks represents \
        the tech-bro billionaire.",
        "Duckberg is where the Duck family is from, Mouseton is where Mickey Mouse is from, Spoonerville is \
        where Goofy is from, St. Canard is where Drake Mallard is from, and Cape Suzette is where Kit Cloudkicker \
        is from.",
        "The voice actress for Black Heron, who is trying to steal the gummiberry juice recipie, is the daughter of \
        the voice actor for Zummi Gummi, who is one of the protectors of the Gummi Bear knowledge in the original \
        Gummi Bears show"
    ]
}


@mcp.tool
def get_random_fact() -> str:
    """Return a random trivia fact from any category."""
    category = random.choice(list(FACTS.keys()))
    fact = random.choice(FACTS[category])
    return f"[{category.title()}] {fact}"


@mcp.tool
def get_fact_about(category: str) -> str:
    """Return a random fact from a specific category.
    category: One of 'science', 'history', or 'animals'.
    """
    category = category.lower().strip()
    if category not in FACTS:
        available = ", ".join(FACTS.keys())
        return f"Unknown category '{category}'. Available: {available}"
    return random.choice(FACTS[category])


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
