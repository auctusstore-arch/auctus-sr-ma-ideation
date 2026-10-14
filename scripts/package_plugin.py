#!/usr/bin/env python3
"""Check contained plugin references and build a distributable plugin ZIP."""
import hashlib
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = ["plugin.json", "mcp.json", ".mcp.json", ".codex-plugin/plugin.json", "README.md"]


def validate():
    manifest = json.loads((ROOT / "plugin.json").read_text())
    compat = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "auctus-sr-ma-ideation"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert (manifest["name"], manifest["version"]) == (compat["name"], compat["version"])
    interface = manifest["extensions"]["com.openai"]["interface"]
    assert len(interface["shortDescription"]) <= 30
    assert 1 <= len(interface["defaultPrompt"]) <= 3
    for key in ("displayName", "defaultPrompt", "logo", "logoDark", "composerIcon", "composerIconDark"):
        assert interface[key] == compat["interface"][key], f"Manifest mismatch: {key}"
    for key in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        asset = (ROOT / interface[key]).resolve()
        assert asset.is_relative_to(ROOT) and asset.is_file()
        assert asset.stat().st_size <= 5 * 1024 * 1024
    mcp = json.loads((ROOT / "mcp.json").read_text())
    legacy_mcp = json.loads((ROOT / compat["mcpServers"]).read_text())
    def canonical_servers(config):
        return {name: {**server, "headers": server.get("headers", {})}
                for name, server in config["mcpServers"].items()}
    assert canonical_servers(mcp) == canonical_servers(legacy_mcp)
    server = mcp["mcpServers"]["pubmed-auctus"]
    assert server["type"] == "streamable-http"
    assert server["url"] == "https://pubmed.caseyjhand.com/mcp"
    catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    assert catalog["name"] == "auctus"
    entry = catalog["plugins"][0]
    assert entry["name"] == manifest["name"]
    assert entry["source"]["path"].startswith("./")
    assert (ROOT / entry["source"]["path"] / "plugin.json").resolve() == ROOT / "plugin.json"
    skill = ROOT / "skills/sr-ideation/SKILL.md"
    assert skill.read_text().startswith("---\nname: sr-ideation\n")
    for path in (ROOT / "skills").rglob("*.md"):
        text = path.read_text()
        assert "\u2014" not in text, str(path)
        for link in re.findall(r"\]\(([^)]+)\)", text):
            if not link.startswith(("http://", "https://", "#")):
                target = (path.parent / link.split("#")[0]).resolve()
                assert target.is_relative_to(ROOT) and target.exists(), (path, link)
    return manifest


def build():
    manifest = validate()
    files = [ROOT / path for path in TOP_FILES]
    for folder in ("assets", "skills"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink not allowed: {path}")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" and path.name != ".DS_Store":
                files.append(path)
    output = ROOT / "dist" / f"{manifest['name']}-{manifest['version']}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = (Path(manifest["name"]) / path.relative_to(ROOT)).as_posix()
            # Stable timestamps also accept files unpacked from archives with
            # epoch timestamps, which ZIP otherwise rejects as pre-1980.
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert {name.split("/")[0] for name in archive.namelist()} == {manifest["name"]}
    checksum = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".zip.sha256").write_text(f"{checksum}  {output.name}\n")
    print(json.dumps({"archive": str(output), "files": len(files), "sha256": checksum}))
    return output


if __name__ == "__main__":
    build()
