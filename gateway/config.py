"""Local configuration; credentials can stay in an external, untracked key file."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    # Minimal .env reader so we don't need python-dotenv. Real env vars win.
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(ROOT / ".env")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "" if LLM_PROVIDER == "gemini" else "ollama")
LLM_API_KEY_FILE = os.environ.get("LLM_API_KEY_FILE", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemma-4-31b-it" if LLM_PROVIDER == "gemini" else "gemma4:e4b")
LLM_SMALL_MODEL = os.environ.get("LLM_SMALL_MODEL", LLM_MODEL)
LLM_VISION = os.environ.get("LLM_VISION", "1") == "1"
LLM_TIMEOUT = float(os.environ.get("LLM_TIMEOUT", "180"))

DB_PATH = ROOT / os.environ.get("GATEWAY_DB", "data/gateway.db")
CACHE_DIR = ROOT / os.environ.get("GATEWAY_CACHE", "data/cache")
SOURCES_FILE = ROOT / "sources.yaml"

CRAWL_DELAY = float(os.environ.get("CRAWL_DELAY", "2"))
USER_AGENT = os.environ.get(
    "USER_AGENT", "StartupASEANGatewayBot/0.1 (hackathon prototype)"
)
# Cleaned page text sent to the model is cut to this many characters.
MAX_PAGE_CHARS = int(os.environ.get("MAX_PAGE_CHARS", "24000"))

# Domains we treat as aggregators: listings found there get followed to the organiser's own page.
AGGREGATOR_DOMAINS = {
    "e27.co", "f6s.com", "devpost.com", "techinasia.com", "gust.com",
    "crunchbase.com", "startupblink.com", "dealroom.co",
}
