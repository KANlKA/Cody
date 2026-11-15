import hashlib, json
from pathlib import Path

MODEL_DIR = Path("cache/models/BAAI__bge-m3--5617a9f61b02")
REPOSITORY = "BAAI/bge-m3"
REVISION = "5617a9f61b028005a4858fdac845db406aefb181"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


hashes = {
    str(p.relative_to(MODEL_DIR)).replace("\\", "/"): sha256(p)
    for p in MODEL_DIR.rglob("*.py")
    if p.is_file()
}
manifest = {"repository": REPOSITORY, "revision": REVISION, "python_file_sha256": hashes}
(MODEL_DIR / ".cody_model.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("wrote manifest with", len(hashes), "python files:", list(hashes))