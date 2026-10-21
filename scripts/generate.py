#!/usr/bin/env python3
"""
Agnes AI - Image and Video Generation Script (stdlib only, no httpx required)

Usage:
    # Text-to-Image
    python generate.py image --mode txt2img --prompt "A cat playing soccer" --size 1024x1024

    # Image Editing (Img2Img)
    python generate.py image --mode img2img --prompt "Change to evening scene" --image "https://..."

    # Create Video (Image-to-Video)
    python generate.py video --prompt "Cat kicks ball" --image "https://..."

    # Create Video (Text-to-Video, no image needed)
    python generate.py video --prompt "A cat playing soccer on a green field"

    # Poll an existing video task by video_id
    python generate.py poll --video-id video_xxx
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse


# ── Load API key from config.json, .env or environment variable ─────────────
API_KEY = os.environ.get("AGNES_API_KEY", "").strip()
skill_dir = Path(__file__).parent.parent

# Priority 1: config.json
config_path = skill_dir / "config.json"
try:
    if not API_KEY and config_path.exists():
        config_data = json.loads(config_path.read_text(encoding="utf-8"))
        if config_data.get("api_key"):
            API_KEY = config_data["api_key"].strip()
except Exception:
    pass

# Priority 2: .env file
if not API_KEY:
    env_path = skill_dir / ".env"
    try:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").strip().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("AGNES_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass

# Priority 3: Environment variable
if not API_KEY:
    API_KEY = os.environ.get("AGNES_API_KEY", "")

BASE_URL = "https://apihub.agnes-ai.com/v1"


# Price snapshot verified 2026-10-21; recheck official pricing before use.
IMAGE_MODELS = ("agnes-image-2.5-flash", "agnes-image-2.1-flash",
                "agnes-image-2.0-flash")
VIDEO_MODELS = ("agnes-video-2.5-flash",)


def post_with_fallback(path, payload, models):
    """Only switch after an explicit model-unavailable rejection.
    Ambiguous server/network failures may have accepted a generation: stop.
    """
    for index, model in enumerate(models):
        body = dict(payload, model=model)
        # The oldest editor keeps its legacy tags.
        if model == "agnes-image-2.0-flash" and body.get("extra_body", {}).get("image"):
            body["tags"] = ["img2img"]
        print(f"Generating with {model}...")
        try:
            return _post(path, body)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").lower()
            unavailable = exc.code in (400, 403, 404) and any(
                marker in detail for marker in (
                    "model_not_found", "model not found", "model unavailable",
                    "model is unavailable", "model_not_available",
                    "model is not available", "model_access_denied",
                    "model has been retired"))
            if not unavailable or index == len(models) - 1:
                raise
            print(f"{model} unavailable; using next verified free model.")
    raise RuntimeError("No compatible free model available")


def ensure_api_key():
    if not API_KEY:
        print("Error: Agnes AI API key is not configured.")
        print("\n📌 Configure API Key (choose one method):")
        print("\n  Method 1 (Recommended) - Edit config.json:")
        print(f"    Path: {config_path}")
        print('    Content: {"api_key": "your-api-key-here"}')
        print("\n  Method 2 - Environment Variable:")
        print("    export AGNES_API_KEY='your-api-key-here'")
        print("\n  Method 3 - .env file:")
        print(f"    Path: {skill_dir / '.env'}")
        print("    Content: AGNES_API_KEY=your-api-key-here")
        print("\n  Get your key from: https://platform.agnes-ai.com")
        sys.exit(1)


def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _post(path, payload):
    """POST to Agnes API, return parsed JSON."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=_headers(),
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read().decode("utf-8"))


def _get(path):
    """GET from Agnes API, return parsed JSON."""
    req = urllib.request.Request(
        BASE_URL.rsplit("/", 1)[0] + path,
        headers=_headers(),
        method="GET",
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read().decode("utf-8"))


def _download(url, dest_path):
    """Download a file from URL to dest_path."""
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    resp = urllib.request.urlopen(url, timeout=120)
    data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)
    return len(data)


# ── Image Generation ──────────────────────────────────────────────────────────

def generate_image(mode, prompt, image_url=None, size="1024x1024", seed=None, output_dir=None):
    """Generate or edit an image via Agnes AI API."""
    ensure_api_key()

    if mode not in ("txt2img", "img2img"):
        raise ValueError("Unknown image mode")
    if mode == "img2img" and not image_url:
        raise ValueError("--image is required for img2img")
    payload = {"prompt": prompt, "size": size,
               "extra_body": {"response_format": "url"}}
    if seed is not None:
        payload["seed"] = seed
    if mode == "img2img":
        payload["extra_body"]["image"] = (
            [image_url] if isinstance(image_url, str) else image_url)
    result = post_with_fallback("/images/generations", payload, IMAGE_MODELS)

    if not result.get("data"):
        print(f"Error: No image data in response: {result}")
        sys.exit(1)

    img_url = result["data"][0]["url"]
    print(f"Image URL: {img_url}")

    # Download and save
    out_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "generated-images"
    ext = "png"
    fname = Path(img_url).name.split("?")[0]
    if "." in fname:
        ext = fname.rsplit(".", 1)[-1]
    dest = out_dir / f"image_{seed or int(time.time())}.{ext}"
    counter = 1
    while dest.exists():
        dest = out_dir / f"image_{seed or int(time.time())}_{counter}.{ext}"
        counter += 1

    size_bytes = _download(img_url, dest)
    print(f"Saved to: {dest} ({size_bytes:,} bytes)")
    return str(dest)


# ── Video Generation ──────────────────────────────────────────────────────────

def create_video_task(prompt, image_url=None, seconds=5, aspect_ratio="16:9"):
    """Submit once; return video_id for the current API."""
    ensure_api_key()
    if not 4 <= int(seconds) <= 12:
        raise ValueError("seconds must be 4..12")
    payload = {"prompt": prompt, "seconds": str(seconds), "size": "720P",
               "aspect_ratio": aspect_ratio,
               "mode": "keyframe" if image_url else "text"}
    if image_url:
        payload["first_frame"] = image_url
    task = post_with_fallback("/videos", payload, VIDEO_MODELS)
    video_id = task.get("video_id")
    if not video_id:
        raise RuntimeError("No video_id returned; do not resubmit automatically. "
                           "Check the accepted task in the platform.")
    print(f"video_id: {video_id}")
    print(f"Resume: python generate.py poll --video-id {video_id}")
    return video_id


def poll_video_task(video_id, auto_download=True, output_dir=None, max_polls=600):
    """Poll the accepted task; never create another task on polling errors."""
    ensure_api_key()
    query = urllib.parse.urlencode({"video_id": video_id,
                                    "model_name": VIDEO_MODELS[0]})
    for attempt in range(max_polls):
        try:
            result = _get(f"/agnesapi?{query}")
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504, 520):
                raise
            time.sleep(min(30, max(2, int(exc.headers.get("Retry-After", "2")))))
            continue
        status = result.get("status")
        print(f"Poll {attempt + 1}: {status} {result.get('progress', 0)}%")
        if status == "failed":
            raise RuntimeError(f"Video generation failed: {result.get('error')}")
        if status == "completed":
            url = result.get("url")
            if not url:
                raise RuntimeError("Completed task has no url; do not resubmit.")
            if not auto_download:
                return url
            out = Path(output_dir) if output_dir else skill_dir / "generated-images"
            dest = out / f"video_{Path(video_id).name}_{time.time_ns()}.mp4"
            _download(url, dest)
            print(f"Saved to: {dest}")
            return str(dest)
        time.sleep(2)
    raise TimeoutError(f"Polling limit reached. Resume with --video-id {video_id}")


def generate_video(prompt, image_url=None, seconds=5, aspect_ratio="16:9", output_dir=None):
    video_id = create_video_task(prompt, image_url, seconds, aspect_ratio)
    return poll_video_task(video_id, output_dir=output_dir)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agnes AI - Image and Video Generation")
    subparsers = parser.add_subparsers(dest="type", help="Generation type")

    # image
    img_p = subparsers.add_parser("image", help="Generate or edit images")
    img_p.add_argument("--mode", choices=["txt2img", "img2img"], required=True)
    img_p.add_argument("--prompt", required=True)
    img_p.add_argument("--image", action="append", help="Source image URL (img2img only)")
    img_p.add_argument("--size", default="1024x1024", help="1024x1024 | 1024x768 | 768x1024")
    img_p.add_argument("--seed", type=int, default=None)
    img_p.add_argument("--output", default=None, help="Output directory")

    # video (blocking: create + poll)
    vid_p = subparsers.add_parser("video", help="Generate a video (create task + poll until done)")
    vid_p.add_argument("--prompt", required=True)
    vid_p.add_argument("--image", help="Source image URL (image-to-video mode)")
    vid_p.add_argument("--seconds", type=int, choices=range(4, 13), default=5)
    vid_p.add_argument("--aspect-ratio", choices=["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"], default="16:9")
    vid_p.add_argument("--output", default=None, help="Output directory")

    # create: submit video task and return video_id immediately (non-blocking)
    create_p = subparsers.add_parser("create", help="Submit video task and print video_id immediately (non-blocking)")
    create_p.add_argument("--prompt", required=True)
    create_p.add_argument("--image", help="Source image URL")
    create_p.add_argument("--seconds", type=int, choices=range(4, 13), default=5)
    create_p.add_argument("--aspect-ratio", choices=["21:9", "16:9", "4:3", "1:1", "3:4", "9:16"], default="16:9")

    # poll: check task status by video_id and download when done
    poll_p = subparsers.add_parser("poll", help="Poll a video task by video_id and download when done")
    poll_p.add_argument("--video-id", required=True, help="video_id from create; task_id is not accepted")
    poll_p.add_argument("--output", default=None, help="Output directory")
    poll_p.add_argument("--no-download", action="store_true", help="Print URL only, don't download")

    args = parser.parse_args()

    if args.type == "image":
        generate_image(args.mode, args.prompt, args.image, args.size, args.seed, args.output)
    elif args.type == "video":
        generate_video(args.prompt, args.image, args.seconds, args.aspect_ratio, args.output)
    elif args.type == "create":
        create_video_task(args.prompt, args.image, args.seconds, args.aspect_ratio)
    elif args.type == "poll":
        poll_video_task(args.video_id, auto_download=not args.no_download, output_dir=args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

