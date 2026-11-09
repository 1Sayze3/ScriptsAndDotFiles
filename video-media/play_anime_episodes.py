#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys
import requests

API_BASE_URL = "https://anidb.app/api/frontend/episode"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "application/json",
}
BATCH_SIZE = 3
MPV_INPUT_CONF = "/tmp/mpv_anime_input.conf"


def setup_mpv_keybindings():
    """Configure MPV keybindings:

    - 'q', 'Q', window close, and ctrl+c exit with code 2 to kill the Python
    loop.
    - '>', '<', 'n', and 'p' navigate between queued episodes inside MPV's
    playlist.
    """
    config_content = (
        "q quit 2\n"
        "Q quit 2\n"
        "CLOSE_WIN quit 2\n"
        "ctrl+c quit 2\n"
        "> playlist-next\n"
        "< playlist-prev\n"
        "n playlist-next\n"
        "p playlist-prev\n"
    )
    try:
        with open(MPV_INPUT_CONF, "w") as f:
            f.write(config_content)
    except OSError as err:
        print(f"[!] Warning: Could not write input config: {err}")


def fetch_stream_url(episode_id: int, preferred_lang: str) -> str | None:
    """Fetch the embed URL for a single episode ID."""
    url = f"{API_BASE_URL}/{episode_id}/languages"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        languages = data.get("languages", [])

        # 1. Match selected language
        for lang in languages:
            if lang.get("code", "").lower() == preferred_lang.lower():
                return lang.get("embed_url")

        # 2. Fallback to Japanese
        for lang in languages:
            if lang.get("code", "").lower() == "jpn":
                return lang.get("embed_url")

        # 3. Fallback to first available
        if languages:
            return languages[0].get("embed_url")

    except (requests.RequestException, ValueError):
        pass

    return None


def select_language(
    sample_languages: list[dict], preselected_code: str | None
) -> str:
    """Prompt user with Japanese selected as the default option."""
    if preselected_code:
        return preselected_code.lower()

    if not sample_languages:
        return "jpn"

    # Identify index of Japanese ('jpn') to set as default
    default_idx = 1
    for idx, lang in enumerate(sample_languages, start=1):
        if lang.get("code", "").lower() == "jpn":
            default_idx = idx
            break

    print("\nAvailable Audio Tracks:")
    for idx, lang in enumerate(sample_languages, start=1):
        name = lang.get("name", "Unknown")
        code = lang.get("code", "N/A")
        default_tag = " (Default)" if idx == default_idx else ""
        print(f"  [{idx}] {name} ({code}){default_tag}")

    while True:
        choice = input(
            f"\nSelect language [1-{len(sample_languages)}] (default {default_idx}): "
        ).strip()
        if choice == "":
            return sample_languages[default_idx - 1].get("code", "jpn")
        if choice.isdigit() and 1 <= int(choice) <= len(sample_languages):
            return sample_languages[int(choice) - 1].get("code", "jpn")
        print("Invalid choice. Please enter a valid number.")


def daemonize():
    """Detach into the background and terminate the parent Kitty window."""
    parent_pid = os.getppid()

    try:
        pid = os.fork()
        if pid > 0:
            try:
                os.kill(parent_pid, signal.SIGHUP)
            except ProcessLookupError:
                pass
            sys.exit(0)
    except OSError as err:
        sys.stderr.write(f"Fork failed: {err}\n")
        sys.exit(1)

    os.setsid()

    with (
        open(os.devnull, "r") as devnull_r,
        open(os.devnull, "a+") as devnull_w,
    ):
        os.dup2(devnull_r.fileno(), sys.stdin.fileno())
        os.dup2(devnull_w.fileno(), sys.stdout.fileno())
        os.dup2(devnull_w.fileno(), sys.stderr.fileno())


def playback_loop(start_id: int, preferred_lang: str):
    """Fetch 3 URLs in order, load into MPV playlist, and fetch the next batch on completion."""
    current_id = start_id

    while True:
        urls = []

        # Fetch batch of 3 consecutive episodes
        for offset in range(BATCH_SIZE):
            ep_id = current_id + offset
            url = fetch_stream_url(ep_id, preferred_lang)
            if url:
                urls.append(url)
            else:
                break

        # Stop if no valid URLs could be fetched
        if not urls:
            break

        # Pass all 3 URLs into MPV as a native sequential playlist
        cmd = [
            "mpv",
            "--no-terminal",
            f"--input-conf={MPV_INPUT_CONF}",
        ] + urls

        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        # Stop if user pressed 'q', closed the player window, or MPV errored
        if result.returncode != 0:
            break

        # Advance ID by the number of episodes retrieved in this batch
        current_id += len(urls)

        # Stop if we hit the end of the available episodes (less than 3 returned)
        if len(urls) < BATCH_SIZE:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Stream anime in 3-episode batches via MPV with Japanese default."
    )
    parser.add_argument(
        "episode_id", type=int, help="Starting Episode ID (e.g. 234)"
    )
    parser.add_argument(
        "-l",
        "--lang",
        type=str,
        default="jpn",
        help="Audio code override (default: jpn)",
    )
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Force the interactive language selection menu",
    )
    args = parser.parse_args()

    chosen_lang = args.lang

    # If --prompt flag is passed, show interactive selector; otherwise use Japanese default
    if args.prompt:
        initial_url = f"{API_BASE_URL}/{args.episode_id}/languages"
        try:
            res = requests.get(initial_url, headers=HEADERS, timeout=10)
            res.raise_for_status()
            data = res.json()
            chosen_lang = select_language(data.get("languages", []), None)
        except Exception as e:
            print(f"[!] Could not query languages: {e}. Defaulting to Japanese.")
            chosen_lang = "jpn"

    setup_mpv_keybindings()
    daemonize()
    playback_loop(args.episode_id, chosen_lang)


if __name__ == "__main__":
    main()
