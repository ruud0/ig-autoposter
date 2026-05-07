"""Generate organic Instagram captions + hashtags for beats using Claude."""

import random

import anthropic

from config import ANTHROPIC_API_KEY, HASHTAG_POOL, CAPTION_STYLES


def generate_caption(
    track_name: str,
    mood: str | None = None,
    style: str | None = None,
) -> str:
    """
    Generate an Instagram caption for a beat post.

    Returns caption text with hashtags appended.
    """
    if style is None:
        style = random.choice(CAPTION_STYLES)

    style_instructions = {
        "minimal": "Write 1-5 words max. A single mood word, a vibe, a texture. No sentences. Think album liner notes.",
        "behind_scenes": "Write 1-2 short sentences about the production process — what inspired it, what sound you were going for. First person, casual tone.",
        "mood": "Write 1-2 sentences describing the atmosphere or feeling of this beat. Evocative, not literal. Paint a scene.",
        "mystery": "Write a cryptic, intriguing one-liner. Like a caption you'd see from a cool artist — minimal punctuation, lowercase vibes.",
    }

    mood_hint = f"\nThe mood/vibe of this beat: {mood}" if mood else ""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        messages=[{
            "role": "user",
            "content": (
                f"Write an Instagram caption for a beat/instrumental called \"{track_name}\".{mood_hint}\n\n"
                f"Style: {style_instructions[style]}\n\n"
                "Rules:\n"
                "- No emojis\n"
                "- No \"link in bio\" or sales language\n"
                "- No hashtags (I'll add those separately)\n"
                "- Sound like a real producer, not a marketer\n"
                "- Lowercase is fine\n"
                "- Output ONLY the caption text, nothing else"
            ),
        }],
    )

    caption = response.content[0].text.strip()

    # Pick 15-20 random hashtags from the pool
    n_tags = random.randint(15, 20)
    tags = random.sample(HASHTAG_POOL, min(n_tags, len(HASHTAG_POOL)))
    hashtag_block = " ".join(tags)

    return f"{caption}\n\n.\n.\n.\n{hashtag_block}"


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "midnight drift"
    mood = sys.argv[2] if len(sys.argv) > 2 else None
    print(generate_caption(name, mood))
