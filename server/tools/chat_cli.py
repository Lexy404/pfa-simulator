"""Interactive text client for /ws/session.

Usage:  python tools/chat_cli.py [--url ws://localhost:8000/ws/session]
Type a line and press Enter; Ctrl+D or Ctrl+C to quit.
"""

import argparse
import asyncio
import sys

import websockets

from pfa_server.protocol import ErrorMessage, NpcDone, NpcToken, PlayerText, parse_server_message


async def chat(url: str) -> None:
    async with websockets.connect(url) as ws:
        print(f"Connected to {url}. Type your line (Ctrl+D to quit).")
        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, lambda: input("\nyou> "))
            if not line.strip():
                continue
            await ws.send(PlayerText(text=line).model_dump_json())

            print("npc> ", end="", flush=True)
            while True:
                msg = parse_server_message(await ws.recv())
                if isinstance(msg, NpcToken):
                    print(msg.text, end="", flush=True)
                elif isinstance(msg, NpcDone):
                    lat = msg.latency
                    print(f"\n     [ttft {lat.ttft_ms:.0f} ms | total {lat.total_ms:.0f} ms]")
                    break
                elif isinstance(msg, ErrorMessage):
                    print(f"\n[error] {msg.message}")
                    break


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="ws://localhost:8000/ws/session")
    args = parser.parse_args()
    try:
        asyncio.run(chat(args.url))
    except (EOFError, KeyboardInterrupt):
        print("\nbye")
    except OSError as e:
        sys.exit(f"Cannot connect to {args.url}: {e}")


if __name__ == "__main__":
    main()
