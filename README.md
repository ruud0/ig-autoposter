# ig-autoposter

Automated Instagram Reels pipeline for music producers. Drop a beat (wav/mp3) into `input/`, and the system generates a waveform animation video, writes an organic caption with Claude, and posts it to your Instagram as a Reel via the official Graph API.

## How it works

```
input/beat.wav → [FFmpeg waveform video] → [Claude caption] → [Instagram Graph API] → Live Reel
```

## Setup

### 1. Instagram Business Account
- Open Instagram → Settings → Account → Switch to Professional → **Business**
- Create or link a **Facebook Page** to the account

### 2. Meta Developer App
- Go to [developers.facebook.com](https://developers.facebook.com)
- Create a new app → Add **Instagram Graph API** product
- Generate a long-lived access token with these permissions:
  - `instagram_basic`
  - `instagram_content_publish`
  - `pages_read_engagement`
- Find your Instagram User ID via the Graph API Explorer

### 3. Install dependencies

```bash
pip install anthropic httpx python-dotenv pyngrok
winget install ffmpeg   # or download from ffmpeg.org
```

### 4. Configure

```bash
cp .env.example .env
```

Fill in your `.env`:
- `IG_ACCESS_TOKEN`: your long-lived Instagram token
- `IG_USER_ID`: your Instagram Business account user ID
- `ANTHROPIC_API_KEY`: for caption generation
- `NGROK_AUTH_TOKEN`: free account at [ngrok.com](https://ngrok.com) (needed to serve video to Instagram)

## Usage

```bash
# Drop audio files into input/ folder, then:

python pipeline.py ingest     # Generate videos + captions for new audio
python pipeline.py post       # Post the next queued item
python pipeline.py auto       # Ingest + post in one command
python pipeline.py status     # See what's queued/posted/failed
python pipeline.py preview <name>  # Preview a caption before posting
```

### Standalone tools

```bash
python visuals.py beat.wav "track name"    # Generate video only
python captions.py "track name" "dark"     # Generate caption only
python poster.py video.mp4 "caption"       # Post only
```

## Daily automation

Use Windows Task Scheduler or Claude Code's `/schedule` to run daily:

```bash
python pipeline.py auto
```

## Video specs

- 1080x1920 (9:16 vertical)
- 30-60 second clips
- Waveform animation + track name overlay
- Dark aesthetic with purple waveform (customizable in `config.py`)

## Architecture

| File | Purpose |
|------|---------|
| `pipeline.py` | CLI orchestrator: ingest, post, auto, status |
| `visuals.py` | FFmpeg waveform/spectrum video generator |
| `captions.py` | Claude-powered caption + hashtag generator |
| `poster.py` | Instagram Graph API publisher with ngrok tunneling |
| `config.py` | Environment variables and constants |
