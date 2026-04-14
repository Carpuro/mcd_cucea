from pathlib import Path

def resolve_repo_path(*parts) -> Path:
    # /app is the repo root inside the container
    return Path(__file__).resolve().parents[1].joinpath(*parts)

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)