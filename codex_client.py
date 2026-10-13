"""Call the configured stdio MCP server from chats that predate installation."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent


async def invoke(args):
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "launch_codex.py"), "--host", "127.0.0.1"],
    )
    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1], read_timeout_seconds=180) as session:
            init = await session.initialize()
            if args.tool == "list":
                result = await session.list_tools()
                print(json.dumps({"initialization": init.model_dump(by_alias=True),
                                  "tools": [t.model_dump(by_alias=True) for t in result.tools]}, indent=2))
                return
            arguments = json.loads(Path(args.arguments).read_text(encoding="utf-8-sig")) if args.arguments else {}
            if args.script:
                arguments["code"] = Path(args.script).read_text(encoding="utf-8-sig")
                if args.tool == "execute_code":
                    arguments.setdefault("include_screenshot", False)
            result = await session.call_tool(args.tool, arguments)
            content = []
            failed = getattr(result, "is_error", False) or getattr(result, "isError", False)
            for index, item in enumerate(result.content):
                serialized = item.model_dump(by_alias=True)
                mime_type = serialized.get("mimeType", serialized.get("mime_type"))
                if item.type == "image" and args.image_dir:
                    import base64
                    directory = Path(args.image_dir)
                    directory.mkdir(parents=True, exist_ok=True)
                    suffix = "png" if mime_type == "image/png" else "jpg"
                    image = directory / f"{args.tool}-{index}.{suffix}"
                    image.write_bytes(base64.b64decode(item.data))
                    content.append({"type": "image", "path": str(image), "mimeType": mime_type})
                elif item.type == "image":
                    content.append({"type": "image", "mimeType": mime_type, "omitted": True})
                else:
                    content.append(serialized)
            print(json.dumps({"isError": failed, "content": content}, indent=2))
            if failed:
                raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool")
    parser.add_argument("--arguments", help="JSON file containing tool arguments")
    parser.add_argument("--script", help="Python script for an execute_code tool")
    parser.add_argument("--image-dir", help="Directory to save image feedback")
    asyncio.run(invoke(parser.parse_args()))
