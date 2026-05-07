import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
QUEUE_FILE = BASE_DIR / "queue.json"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_DURATION_MIN = 30
VIDEO_DURATION_MAX = 60

WAVEFORM_COLOR = "0x8B5CF6"  # purple
BG_COLOR = "0x0A0A0A"  # near-black
TEXT_COLOR = "white"

GRAPH_API_BASE = "https://graph.instagram.com/v21.0"

HASHTAG_POOL = [
    "#beats", "#producer", "#beatmaker", "#musicproduction",
    "#typebeat", "#instrumental", "#newmusic", "#producerlife",
    "#beatmaking", "#studiolife", "#hiphopbeats", "#trapbeats",
    "#flstudio", "#ableton", "#sampling", "#mixingandmastering",
    "#undergroundbeats", "#indiemusic", "#lofi", "#vibes",
    "#sounddesign", "#musicproducer", "#beatsforsale", "#prodby",
    "#cookingbeats", "#inthestudio", "#wavs", "#drillbeats",
    "#rnbbeats", "#electronicmusic",
]

CAPTION_STYLES = [
    "minimal",       # just a mood word or phrase
    "behind_scenes", # production process angle
    "mood",          # describe the feeling/atmosphere
    "mystery",       # cryptic, intriguing one-liner
]
