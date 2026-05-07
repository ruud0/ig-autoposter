"""
ig-autoposter CLI — ingest audio, generate Reels, post to Instagram.

Usage:
    python pipeline.py ingest          Scan input/ for new audio, generate videos + captions
    python pipeline.py post            Post the next queued item to Instagram
    python pipeline.py auto            Ingest new files + post one queued item
    python pipeline.py status          Show queue state
    python pipeline.py preview <slug>  Show caption for a queued item before posting
"""

import json
import sys
import time
from pathlib import Path

from config import INPUT_DIR, OUTPUT_DIR, QUEUE_FILE

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".ogg", ".m4a"}


def _load_queue() -> list[dict]:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    return []


def _save_queue(queue: list[dict]):
    QUEUE_FILE.write_text(
        json.dumps(queue, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _find_new_audio(queue: list[dict]) -> list[Path]:
    queued_sources = {item["source"] for item in queue}
    new_files = []
    for f in INPUT_DIR.iterdir():
        if f.suffix.lower() in AUDIO_EXTENSIONS and str(f) not in queued_sources:
            new_files.append(f)
    return sorted(new_files)


def cmd_ingest():
    from visuals import generate_reel
    from captions import generate_caption

    queue = _load_queue()
    new_files = _find_new_audio(queue)

    if not new_files:
        print("No new audio files in input/")
        return

    for audio_path in new_files:
        track_name = audio_path.stem
        print(f"\n--- Processing: {track_name} ---")

        print("  Generating video...")
        video_path = generate_reel(audio_path, track_name)
        print(f"  Video: {video_path}")

        print("  Generating caption...")
        caption = generate_caption(track_name)
        print(f"  Caption: {caption[:80]}...")

        queue.append({
            "source": str(audio_path),
            "video": str(video_path),
            "track_name": track_name,
            "caption": caption,
            "status": "pending",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "posted_at": None,
            "media_id": None,
        })
        print(f"  Queued.")

    _save_queue(queue)
    pending = sum(1 for i in queue if i["status"] == "pending")
    print(f"\nDone. {len(new_files)} new items ingested. {pending} pending in queue.")


def cmd_post():
    from poster import publish_reel

    queue = _load_queue()
    pending = [i for i in queue if i["status"] == "pending"]

    if not pending:
        print("Nothing to post. Run 'python pipeline.py ingest' first.")
        return

    item = pending[0]
    print(f"Posting: {item['track_name']}")
    print(f"Caption: {item['caption'][:100]}...")

    try:
        result = publish_reel(item["video"], item["caption"])
        item["status"] = "posted"
        item["posted_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        item["media_id"] = result.get("id")
        print(f"Posted successfully! Media ID: {item['media_id']}")
    except Exception as e:
        item["status"] = "failed"
        item["error"] = str(e)
        print(f"Failed: {e}")

    _save_queue(queue)


def cmd_auto():
    cmd_ingest()
    print()
    cmd_post()


def cmd_status():
    queue = _load_queue()
    if not queue:
        print("Queue is empty.")
        return

    pending = [i for i in queue if i["status"] == "pending"]
    posted = [i for i in queue if i["status"] == "posted"]
    failed = [i for i in queue if i["status"] == "failed"]

    print(f"Queue: {len(queue)} total | {len(pending)} pending | {len(posted)} posted | {len(failed)} failed\n")

    for item in queue:
        status_icon = {"pending": "[ ]", "posted": "[x]", "failed": "[!]"}.get(item["status"], "[?]")
        date = item.get("posted_at") or item.get("created_at", "")
        print(f"  {status_icon} {item['track_name']}  ({item['status']})  {date}")


def cmd_preview(slug: str):
    queue = _load_queue()
    for item in queue:
        if slug.lower() in item["track_name"].lower():
            print(f"Track: {item['track_name']}")
            print(f"Status: {item['status']}")
            print(f"Video: {item['video']}")
            print(f"\nCaption:\n{item['caption']}")
            return
    print(f"No queued item matching '{slug}'")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "ingest":
        cmd_ingest()
    elif cmd == "post":
        cmd_post()
    elif cmd == "auto":
        cmd_auto()
    elif cmd == "status":
        cmd_status()
    elif cmd == "preview":
        if len(sys.argv) < 3:
            print("Usage: python pipeline.py preview <slug>")
            sys.exit(1)
        cmd_preview(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
