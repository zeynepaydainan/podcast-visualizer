"""Podcast Library MCP server.

This is a custom MCP (Model Context Protocol) server built with FastMCP.
It acts as the "librarian" of the system: it stores podcast episode
transcripts and finished visual summaries, and hands them to any
MCP-compatible agent that asks.

It runs as a separate process and communicates over stdio (standard
input/output). The ADK agents connect to it via McpToolset.

Security features:
- Episode IDs are validated against a strict allowlist pattern before
  being used in file paths, preventing path traversal attacks
  (e.g. an ID like "../../etc/passwd" is rejected).
- Transcript and summary sizes are capped to prevent runaway inputs.
- All file access is confined to the data/ directory.
"""

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# --- Configuration -----------------------------------------------------

# All data lives under the data/ folder next to this file.
BASE_DIR = Path(__file__).resolve().parent.parent / "data"
EPISODES_DIR = BASE_DIR / "episodes"
SUMMARIES_DIR = BASE_DIR / "summaries"

# Create the folders on first run so the server never crashes on a
# missing directory.
EPISODES_DIR.mkdir(parents=True, exist_ok=True)
SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

# Security: episode IDs may only contain lowercase letters, digits and
# hyphens, 1 to 64 characters. Anything else is rejected outright.
EPISODE_ID_PATTERN = re.compile(r"^[a-z0-9-]{1,64}$")

# Security: size caps (in characters) to prevent oversized inputs.
MAX_TRANSCRIPT_CHARS = 200_000  # ~50k tokens, far beyond any 5-min episode
MAX_SUMMARY_CHARS = 300_000

mcp = FastMCP("podcast-library")


def _validate_episode_id(episode_id: str) -> str:
    """Validate an episode ID or raise a clear error.

    This is the path-traversal guard: because the ID can only contain
    [a-z0-9-], it can never contain "/", "..", or anything else that
    would escape the data directory.
    """
    episode_id = episode_id.strip().lower()
    if not EPISODE_ID_PATTERN.match(episode_id):
        raise ValueError(
            "Invalid episode_id. Use only lowercase letters, digits and "
            "hyphens (e.g. 'insulin-pcos-101')."
        )
    return episode_id


# --- Tools exposed to agents -------------------------------------------


@mcp.tool()
def list_episodes() -> list[str]:
    """List the IDs of all podcast episodes available in the library."""
    return sorted(p.stem for p in EPISODES_DIR.glob("*.txt"))


@mcp.tool()
def get_transcript(episode_id: str) -> str:
    """Fetch the full transcript text of an episode by its ID.

    Args:
        episode_id: The episode identifier, e.g. 'insulin-pcos-101'.
    """
    episode_id = _validate_episode_id(episode_id)
    path = EPISODES_DIR / f"{episode_id}.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"No episode named '{episode_id}'. "
            f"Available: {sorted(p.stem for p in EPISODES_DIR.glob('*.txt'))}"
        )
    return path.read_text(encoding="utf-8")


@mcp.tool()
def add_episode(episode_id: str, transcript: str) -> str:
    """Store a new episode transcript in the library.

    Args:
        episode_id: A new identifier for the episode (lowercase letters,
            digits and hyphens only).
        transcript: The full transcript text of the episode.
    """
    episode_id = _validate_episode_id(episode_id)
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        raise ValueError(
            f"Transcript too large ({len(transcript)} chars). "
            f"Maximum is {MAX_TRANSCRIPT_CHARS}."
        )
    path = EPISODES_DIR / f"{episode_id}.txt"
    path.write_text(transcript, encoding="utf-8")
    return f"Episode '{episode_id}' stored ({len(transcript)} characters)."


@mcp.tool()
def save_summary(episode_id: str, html: str) -> str:
    """Save a finished visual summary (HTML) for an episode.

    Args:
        episode_id: The episode the summary belongs to.
        html: The complete HTML of the visual one-pager.
    """
    episode_id = _validate_episode_id(episode_id)
    if len(html) > MAX_SUMMARY_CHARS:
        raise ValueError(
            f"Summary too large ({len(html)} chars). "
            f"Maximum is {MAX_SUMMARY_CHARS}."
        )
    path = SUMMARIES_DIR / f"{episode_id}.html"
    path.write_text(html, encoding="utf-8")
    return f"Summary saved to {path}"


@mcp.tool()
def get_summary(episode_id: str) -> str:
    """Fetch a previously saved visual summary (HTML) for an episode."""
    episode_id = _validate_episode_id(episode_id)
    path = SUMMARIES_DIR / f"{episode_id}.html"
    if not path.exists():
        raise FileNotFoundError(f"No saved summary for '{episode_id}' yet.")
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    # stdio transport: the ADK agent launches this script as a child
    # process and talks to it over standard input/output. No ports,
    # no networking.
    mcp.run(transport="stdio")
