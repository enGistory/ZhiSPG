import importlib.util
import json
import shutil
import zipfile
from pathlib import Path


def load_patcher():
    script_path = Path(__file__).with_name("patch_static_branding.py")
    spec = importlib.util.spec_from_file_location("patch_static_branding", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_patches_white_label_login_layout(tmp_path):
    repo_root = Path(__file__).resolve().parents[4]
    jar_path = (
        repo_root
        / "dev/release/server/target/arks-sofaboot-0.0.1-SNAPSHOT-executable.jar"
    )
    branding_dir = repo_root / "dev/release/server/branding"
    config = json.loads((branding_dir / "brand.config.json").read_text(encoding="utf-8"))
    patched_jar = tmp_path / "server.jar"
    shutil.copy2(jar_path, patched_jar)

    summary = load_patcher().patch_jar(patched_jar, branding_dir, config)

    assert summary["loginPage"]["layout"] == 1
    assert summary["loginPage"]["backgroundAsset"] == 1

    with zipfile.ZipFile(patched_jar) as archive:
        login_chunk = archive.read(
            "BOOT-INF/classes/static/fcaf5dab-async.5fbc677c.js"
        ).decode("utf-8")
        background = archive.read("BOOT-INF/classes/static/login-bg.ccffd4ea.png")

    assert '"data-login-theme":"zhishu-workbench"' in login_chunk
    assert "layout-title-text-left" not in login_chunk
    assert "OpenSPG" not in login_chunk
    assert background.startswith(b"\x89PNG\r\n\x1a\n")
    assert "max-width: 1540px;" in login_chunk
    assert "margin: 0 auto;" in login_chunk
