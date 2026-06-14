#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path


TEXT_SUFFIXES = {".html", ".js", ".css", ".json"}


def upper_unicode_escapes(value):
    output = []
    index = 0
    while index < len(value):
        if value[index : index + 2] == "\\u" and index + 6 <= len(value):
            output.append("\\u" + value[index + 2 : index + 6].upper())
            index += 6
        else:
            output.append(value[index])
            index += 1
    return "".join(output)


def js_short_escaped(value, latin1_uppercase=True, unicode_uppercase=True):
    output = []
    for char in value:
        codepoint = ord(char)
        if char == "\\":
            output.append("\\\\")
        elif char == '"':
            output.append('\\"')
        elif 32 <= codepoint <= 126:
            output.append(char)
        elif codepoint <= 255:
            template = "\\x{codepoint:02X}" if latin1_uppercase else "\\x{codepoint:02x}"
            output.append(template.format(codepoint=codepoint))
        else:
            template = "\\u{codepoint:04X}" if unicode_uppercase else "\\u{codepoint:04x}"
            output.append(template.format(codepoint=codepoint))
    return "".join(output)


def js_escaped_variants(value):
    json_escaped = json.dumps(value, ensure_ascii=True)[1:-1]
    return [
        value,
        json_escaped,
        upper_unicode_escapes(json_escaped),
        js_short_escaped(value),
        js_short_escaped(value, latin1_uppercase=False, unicode_uppercase=False),
        js_short_escaped(value, latin1_uppercase=False, unicode_uppercase=True),
        js_short_escaped(value, latin1_uppercase=True, unicode_uppercase=False),
    ]


def build_replacements(config):
    replacements = []
    for item in config.get("textReplacements", []):
        source = item["from"]
        target = item["to"]
        for escaped_source, escaped_target in zip(
            js_escaped_variants(source), js_escaped_variants(target)
        ):
            replacements.append((escaped_source, escaped_target))

    seen = set()
    unique = []
    for source, target in replacements:
        key = (source, target)
        if key not in seen:
            seen.add(key)
            unique.append((source, target))
    return unique


def clone_info(info):
    cloned = zipfile.ZipInfo(info.filename, info.date_time)
    cloned.comment = info.comment
    cloned.extra = info.extra
    cloned.internal_attr = info.internal_attr
    cloned.external_attr = info.external_attr
    cloned.create_system = info.create_system
    cloned.compress_type = info.compress_type
    return cloned


def patch_text(data, replacements):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, {}

    counts = {}
    for source, target in replacements:
        count = text.count(source)
        if count:
            text = text.replace(source, target)
            counts[source] = counts.get(source, 0) + count

    if counts:
        return text.encode("utf-8"), counts
    return data, {}


def patch_jar(jar_path, branding_dir, config):
    replacements = build_replacements(config)
    asset_map = {
        path: (branding_dir / local_name).read_bytes()
        for path, local_name in config.get("assetReplacements", {}).items()
    }

    summary = {"text": {}, "assets": []}
    jar_path = jar_path.resolve()
    fd, temp_name = tempfile.mkstemp(suffix=".jar", prefix=jar_path.stem + "-patched-")
    os.close(fd)
    temp_path = Path(temp_name)

    try:
        with zipfile.ZipFile(jar_path, "r") as source_zip, zipfile.ZipFile(
            temp_path, "w", allowZip64=True
        ) as target_zip:
            for info in source_zip.infolist():
                data = source_zip.read(info.filename)

                if info.filename in asset_map:
                    data = asset_map[info.filename]
                    summary["assets"].append(info.filename)
                elif (
                    info.filename.startswith("BOOT-INF/classes/static/")
                    and Path(info.filename).suffix in TEXT_SUFFIXES
                ):
                    data, counts = patch_text(data, replacements)
                    for key, count in counts.items():
                        summary["text"][key] = summary["text"].get(key, 0) + count

                target_zip.writestr(clone_info(info), data)

        shutil.move(str(temp_path), str(jar_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    missing_assets = sorted(set(asset_map) - set(summary["assets"]))
    if missing_assets:
        raise RuntimeError(f"Asset targets not found in jar: {missing_assets}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Patch OpenSPG frontend branding inside a server jar.")
    parser.add_argument("--jar", required=True, type=Path)
    parser.add_argument("--branding-dir", required=True, type=Path)
    parser.add_argument("--config", default="brand.config.json")
    args = parser.parse_args()

    config_path = args.branding_dir / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    summary = patch_jar(args.jar, args.branding_dir, config)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
