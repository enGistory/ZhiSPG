#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path


TEXT_SUFFIXES = {".html", ".js", ".css", ".json"}
LOGIN_CHUNK = "BOOT-INF/classes/static/fcaf5dab-async.5fbc677c.js"
LOGIN_STYLE_RE = re.compile(
    r"let I=u\.styled\.div`.*?`,O=\(0,u\.styled\)\(A\.default\)`", re.DOTALL
)
LOGIN_HERO_RE = re.compile(
    r"\(0,n\.jsxs\)\(J,\{className:\"layout-title-first\",children:\["
    r"\(0,n\.jsx\)\(\"span\",\{className:\"layout-title-text-left\",children:\"[^\"]*\"\}\),"
    r"\(0,n\.jsx\)\(\"span\",\{className:\"layout-title-text-right\",children:"
    r"i\.default\.get\(\{id:\"spg\.pages\.Login\.SemanticallyEnhancedEditableAtlasFramework\","
    r"dm:\"[^\"]*\"\}\)\}\)\]\}\),"
    r"\(0,n\.jsx\)\(\"div\",\{className:\"layout-sub-title-text\",children:"
    r"i\.default\.get\(\{id:\"spg\.pages\.Login\.ANewGenerationOfEnterprise\",dm:\"[^\"]*\"\}\)\}\),"
)
LOGIN_TITLE_RE = re.compile(
    r"\(0,n\.jsx\)\(J,\{level:4,className:\"login-title\",children:"
    r"i\.default\.get\(\{id:\"spg\.pages\.Login\.Login\",dm:\"\\u767B\\u5F55\"\}\)\}\)"
)
LOGIN_PAGE_STYLE = r"""
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  background-image:
    linear-gradient(90deg, rgba(245, 248, 251, 0.96) 0%, rgba(245, 248, 251, 0.72) 52%, rgba(245, 248, 251, 0.95) 100%),
    url(${z.default});
  background-size: cover;
  background-position: center;
  color: #173348;

  .layout-header-container {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 2;
    height: 72px;
    padding: 18px 44px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(38, 88, 117, 0.08);
    background: rgba(255, 255, 255, 0.68);
    backdrop-filter: blur(18px);

    & > img {
      width: 36px;
      height: 36px;
      object-fit: contain;
      padding: 6px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 10px 28px rgba(23, 51, 72, 0.12);
    }
  }

  .layout-center-container {
    min-height: 100vh;
    box-sizing: border-box;
    width: 100%;
    max-width: 1540px;
    margin: 0 auto;
    padding: 128px min(7vw, 112px) 64px;
    display: grid;
    grid-template-columns: minmax(360px, 1fr) 420px;
    align-items: center;
    gap: min(7vw, 96px);
  }

  .brand-panel {
    max-width: 680px;
  }

  .brand-kicker {
    display: inline-flex;
    align-items: center;
    height: 28px;
    padding: 0 12px;
    border: 1px solid rgba(43, 93, 121, 0.16);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.74);
    color: #2b5d79;
    font-size: 12px;
    font-weight: 700;
  }

  .brand-title {
    margin: 18px 0 18px !important;
    color: #102a3a !important;
    font-size: 48px !important;
    line-height: 1.12 !important;
    font-weight: 750 !important;
  }

  .brand-subtitle {
    max-width: 560px;
    color: #496879;
    font-size: 18px;
    line-height: 1.8;
  }

  .brand-metrics {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 34px;

    span {
      display: inline-flex;
      align-items: baseline;
      gap: 10px;
      min-width: 138px;
      padding: 14px 16px;
      border: 1px solid rgba(43, 93, 121, 0.12);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.72);
      box-shadow: 0 18px 40px rgba(23, 51, 72, 0.08);
    }

    strong {
      color: #1769aa;
      font-size: 18px;
    }

    em {
      color: #5d7888;
      font-style: normal;
      font-size: 13px;
    }
  }

  .login-form {
    width: min(420px, calc(100vw - 48px));
    justify-self: end;

    .ant-card {
      border: 1px solid rgba(38, 88, 117, 0.13);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 28px 80px rgba(23, 51, 72, 0.15);
      backdrop-filter: blur(22px);

      .ant-card-body {
        padding: 34px 34px 30px;
      }
    }

    .login-title {
      display: flex;
      flex-direction: column;
      gap: 6px;
      margin-bottom: 26px;
      color: #142f42;
      text-align: left;
    }

    .login-title-main {
      font-size: 22px;
      font-weight: 700;
      line-height: 1.35;
    }

    .login-title-desc {
      color: #6b8492;
      font-size: 13px;
      line-height: 1.6;
      font-weight: 400;
    }

    .login-form-ipt-style {
      height: 44px;
      border: 1px solid rgba(43, 93, 121, 0.18);
      border-radius: 8px;
      background: #fff !important;
      box-shadow: none;

      &:hover,
      &:focus,
      &.ant-input-affix-wrapper-focused {
        border-color: #1769aa;
        box-shadow: 0 0 0 3px rgba(23, 105, 170, 0.1);
      }

      .ant-input-prefix {
        margin-right: 10px;
      }

      .ant-input-prefix .anticon,
      .ant-input-password-icon {
        color: #2b5d79 !important;
      }

      & > input {
        background: transparent;
        color: #173348;

        &::placeholder {
          color: #8ba0ac;
        }
      }
    }

    .submit-btn {
      margin-top: 18px;
      margin-bottom: 0;

      button {
        width: 100%;
        height: 44px;
        border: none;
        border-radius: 8px;
        background: #1769aa;
        box-shadow: 0 14px 28px rgba(23, 105, 170, 0.22);
        font-weight: 600;

        &:hover,
        &:focus {
          background: #125d99;
        }
      }
    }

    .third-party-login {
      display: none;
    }
  }

  @media (max-width: 980px) {
    .layout-header-container {
      height: 64px;
      padding: 14px 24px;
    }

    .layout-center-container {
      grid-template-columns: 1fr;
      padding: 96px 24px 40px;
      gap: 32px;
    }

    .brand-panel {
      max-width: 100%;
    }

    .brand-title {
      font-size: 34px !important;
    }

    .brand-subtitle {
      font-size: 15px;
    }

    .login-form {
      justify-self: start;
    }
  }
"""
HEADER_LINK_PATTERNS = {
    "tutorial": [
        (
            re.compile(r"\(0,a\.jsx\)\(c\.default,\{\}\),"),
            "",
        ),
    ],
    "officialWebsite": [
        (
            re.compile(
                r"\(0,a\.jsx\)\(s\.default,\{type:\"link\",onClick:\(\)=>\{"
                r"window\.open\(\"https://spg\.openkg\.cn\",\"_blank\"\);\},"
                r"children:i\.default\.get\(\{id:\"spg\.Header\.GlobalRightHeader\.OfficialWebsite\","
                r"dm:\"\\u5B98\\u7F51\"\}\)\}\),"
            ),
            "",
        ),
    ],
    "github": [
        (
            re.compile(
                r",\(0,a\.jsx\)\(s\.default,\{type:\"link\",onClick:\(\)=>\{"
                r"window\.open\(\"https://github\.com/[^\"]+/openspg\",\"_blank\"\);\},"
                r"children:\(0,a\.jsx\)\(l\.Icon,\{className:\"header-icon\","
                r"icon:\"ant-design:github-filled\"\}\)\}\)"
            ),
            "",
        ),
    ],
}


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


def normalize_header_links(config):
    requested = config.get("hideRightHeaderLinks", [])
    if requested is True:
        return sorted(HEADER_LINK_PATTERNS)
    if not requested:
        return []
    return list(requested)


def patch_header_links(data, requested_links):
    if not requested_links:
        return data, {}

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, {}

    counts = {}
    for link_name in requested_links:
        patterns = HEADER_LINK_PATTERNS.get(link_name)
        if not patterns:
            raise RuntimeError(f"Unknown right header link: {link_name}")

        for pattern, replacement in patterns:
            text, count = pattern.subn(replacement, text)
            if count:
                counts[link_name] = counts.get(link_name, 0) + count

    if counts:
        return text.encode("utf-8"), counts
    return data, {}


def js_string(value):
    return json.dumps(str(value), ensure_ascii=False)


def build_highlight_nodes(items):
    nodes = []
    for item in items[:3]:
        value = js_string(item.get("value", ""))
        label = js_string(item.get("label", ""))
        nodes.append(
            '(0,n.jsxs)("span",{children:['
            f'(0,n.jsx)("strong",{{children:{value}}}),'
            f'(0,n.jsx)("em",{{children:{label}}})'
            "]})"
        )
    return ",".join(nodes)


def patch_login_page(data, config):
    login_config = config.get("loginPage")
    if not login_config:
        return data, {}

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, {}

    theme = js_string(login_config.get("theme", "zhishu-workbench"))
    title = js_string(login_config.get("title", f"{config.get('brandName', '智数')}数据智能平台"))
    subtitle = js_string(
        login_config.get("subtitle", "面向企业知识图谱、数据治理与智能问答的一体化工作台")
    )
    kicker = js_string(login_config.get("kicker", "DATA INTELLIGENCE"))
    form_title = js_string(login_config.get("formTitle", "登录工作台"))
    form_subtitle = js_string(login_config.get("formSubtitle", "使用管理员账号进入系统"))
    highlights = build_highlight_nodes(login_config.get("highlights", []))

    counts = {}
    layout_parts = 0
    text, count = LOGIN_STYLE_RE.subn(
        f"let I=u.styled.div`{LOGIN_PAGE_STYLE}`,O=(0,u.styled)(A.default)`",
        text,
        count=1,
    )
    if count:
        layout_parts += count

    text, count = re.subn(
        r"return\(0,n\.jsxs\)\(I,\{children:\[",
        f'return(0,n.jsxs)(I,{{"data-login-theme":{theme},children:[',
        text,
        count=1,
    )
    if count:
        layout_parts += count

    hero_replacement = (
        '(0,n.jsxs)("section",{className:"brand-panel",children:['
        f'(0,n.jsx)("div",{{className:"brand-kicker",children:{kicker}}}),'
        f'(0,n.jsx)(J,{{className:"brand-title",children:{title}}}),'
        f'(0,n.jsx)("div",{{className:"brand-subtitle",children:{subtitle}}}),'
        f'(0,n.jsxs)("div",{{className:"brand-metrics",children:[{highlights}]}})'
        "]}),"
    )
    text, count = LOGIN_HERO_RE.subn(hero_replacement, text, count=1)
    if count:
        layout_parts += count

    title_replacement = (
        '(0,n.jsxs)("div",{className:"login-title",children:['
        f'(0,n.jsx)("span",{{className:"login-title-main",children:{form_title}}}),'
        f'(0,n.jsx)("span",{{className:"login-title-desc",children:{form_subtitle}}})'
        "]})"
    )
    text, count = LOGIN_TITLE_RE.subn(title_replacement, text, count=1)
    if count:
        layout_parts += count

    if layout_parts == 4:
        counts["layout"] = 1
        return text.encode("utf-8"), counts
    if layout_parts:
        counts["layoutPartial"] = layout_parts
        return text.encode("utf-8"), counts
    return data, {}


def patch_jar(jar_path, branding_dir, config):
    replacements = build_replacements(config)
    hidden_links = normalize_header_links(config)
    login_config = config.get("loginPage", {})
    login_asset = login_config.get("backgroundAsset")
    asset_map = {
        path: (branding_dir / local_name).read_bytes()
        for path, local_name in config.get("assetReplacements", {}).items()
    }
    login_asset_target = None
    login_asset_data = None
    if login_asset:
        login_asset_target = login_asset["target"]
        login_asset_data = (branding_dir / login_asset["source"]).read_bytes()

    summary = {"text": {}, "assets": [], "headerLinks": {}, "loginPage": {}}
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
                elif login_asset_target and info.filename == login_asset_target:
                    data = login_asset_data
                    summary["loginPage"]["backgroundAsset"] = (
                        summary["loginPage"].get("backgroundAsset", 0) + 1
                    )
                elif (
                    info.filename.startswith("BOOT-INF/classes/static/")
                    and Path(info.filename).suffix in TEXT_SUFFIXES
                ):
                    data, counts = patch_text(data, replacements)
                    for key, count in counts.items():
                        summary["text"][key] = summary["text"].get(key, 0) + count
                    data, counts = patch_header_links(data, hidden_links)
                    for key, count in counts.items():
                        summary["headerLinks"][key] = (
                            summary["headerLinks"].get(key, 0) + count
                        )
                    if info.filename == login_config.get("chunk", LOGIN_CHUNK):
                        data, counts = patch_login_page(data, config)
                        for key, count in counts.items():
                            summary["loginPage"][key] = (
                                summary["loginPage"].get(key, 0) + count
                            )

                target_zip.writestr(clone_info(info), data)

        shutil.move(str(temp_path), str(jar_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    missing_assets = sorted(set(asset_map) - set(summary["assets"]))
    if missing_assets:
        raise RuntimeError(f"Asset targets not found in jar: {missing_assets}")

    missing_links = sorted(set(hidden_links) - set(summary["headerLinks"]))
    if missing_links and config.get("requireHeaderLinkPatches", True):
        raise RuntimeError(f"Right header link targets not found in jar: {missing_links}")

    if login_config and config.get("requireLoginPagePatch", True):
        if summary["loginPage"].get("layout") != 1:
            raise RuntimeError("Login page layout target not found in jar")
        if login_asset and summary["loginPage"].get("backgroundAsset") != 1:
            raise RuntimeError("Login page background asset target not found in jar")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Patch frontend branding inside a server jar.")
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
