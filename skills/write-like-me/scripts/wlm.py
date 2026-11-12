#!/usr/bin/env python3
"""write-like-me: Claude writes in your voice, one tested voice per format.

Standard library only. Your voice lives in a plain folder (default ~/.write-like-me,
or $WLM_HOME). The writer is a clean headless `claude -p` call on your own Claude
subscription, with no tools, memory or project files, so nothing but your voice
and your facts shapes the draft.

  wlm.py init                       make your voice folder from the templates
  wlm.py formats                    list formats and how many examples each has
  wlm.py write <format> --facts f   write a piece, check it, repair it once
  wlm.py check <format> draft.md    lint a draft (exit 1 on errors)
  wlm.py brief <format> --facts f   print the full prompt (for any chat app)
  wlm.py test <format>              blind test: can a judge tell yours from Claude's?
  wlm.py doctor                     which engines work on this machine
  wlm.py pack                       zip the skill with your voice inside, for claude.ai / desktop
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"


def _home():
    if os.environ.get("WLM_HOME"):
        return Path(os.environ["WLM_HOME"]).expanduser()
    user = Path.home() / ".write-like-me"
    packed = SKILL_DIR / "voice"  # a voice packed into the skill, for claude.ai / Claude desktop
    return packed if not user.exists() and (packed / "formats.json").exists() else user


HOME = _home()
ECHO_URL = "https://echo.fulcrum.inc/api/v1"
SYSTEM = "You are a text-only writer. Follow only the supplied task. Return only the requested output."
OUTPUT_RULE = "Return only the finished piece. No preamble, no notes, no alternatives."


class EngineError(RuntimeError):
    pass


# ---------- your voice folder ----------

def need_home():
    if not (HOME / "formats.json").exists():
        sys.exit(f"No voice folder at {HOME}. Run: wlm.py init")


def config():
    path = HOME / "config.json"
    return json.loads(path.read_text()) if path.exists() else {}


def registry():
    return json.loads((HOME / "formats.json").read_text())["formats"]


def fmt(format_id):
    for item in registry():
        if item["id"] == format_id:
            return item
    sys.exit(f"Unknown format '{format_id}'. Run: wlm.py formats")


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def examples(format_id):
    """Pieces in examples.md start with a '## label' line. The label says what it was (a reply to X, a launch post)."""
    text = read(HOME / "formats" / format_id / "examples.md")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    pieces = []
    for block in re.split(r"(?m)^## ", text)[1:]:
        label, _, body = block.partition("\n")
        if body.strip():
            pieces.append({"label": label.strip(), "text": body.strip()})
    return pieces


def rules(format_id):
    out = []
    for path in (HOME / "lint.json", HOME / "formats" / format_id / "lint.json"):
        if path.exists():
            out += json.loads(path.read_text()).get("rules", [])
    return out


# ---------- the prompt ----------

def split_facts(facts, task=None):
    lines = facts.strip().splitlines()
    if lines and lines[0].lower().startswith("task:"):
        task = task or lines[0].split(":", 1)[1].strip()
        lines = lines[1:]
    return "\n".join(lines).strip(), task


def assemble(format_id, facts, task=None, engine="claude", pieces=None):
    f = fmt(format_id)
    facts, task = split_facts(facts, task)
    pieces = examples(format_id) if pieces is None else pieces
    pieces = pieces[: f.get("examples_in_prompt", 6)]
    name = config().get("name", "me")
    length = f.get("length", {})
    shape = f"Layout: {f['layout']}. Length: about {length.get('typical', '?')} {length.get('unit', 'words')}."
    if engine == "echo":
        blocks = [f"Here are {len(pieces)} of my {f['name']} pieces:"]
        blocks += [f'<post situation="{p["label"]}">\n{p["text"]}\n</post>' for p in pieces]
        blocks += [read(HOME / "formats" / format_id / "profile.md"), shape,
                   f"Write {task or f['name']} in my voice from these facts:", facts]
    else:
        blocks = [f"Write as {name}: {f['name']}" + (f". Task: {task}" if task else "."),
                  read(HOME / "core.md"), read(HOME / "formats" / format_id / "profile.md"), shape,
                  "Real pieces they wrote. Copy how they sound, never whole lines:"]
        blocks += [f'<example situation="{p["label"]}">\n{p["text"]}\n</example>' for p in pieces]
        blocks += ["Facts, in order. Use only these. Do not invent numbers, quotes, links, names or experiences:",
                   facts, OUTPUT_RULE]
    return "\n\n".join(b for b in blocks if b.strip())


# ---------- engines ----------

def claude(prompt, model=None, effort=None):
    if not shutil.which("claude"):
        raise EngineError("Claude Code is not installed (https://claude.com/claude-code)")
    env = dict(os.environ)
    env.pop("ECHO_API_KEY", None)
    env.pop("CLAUDECODE", None)
    # Inside some agent apps the parent routes Claude through a local proxy. Use the machine's own login.
    if any(h in env.get("ANTHROPIC_BASE_URL", "") for h in ("127.0.0.1", "localhost")):
        for name in ("ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CONFIG_DIR"):
            env.pop(name, None)
    # A parent Claude Code session's variables must not leak into the clean writer call.
    for name in list(env):
        if name.startswith("CLAUDE_CODE_") or name in ("CLAUDE_PID", "CLAUDE_EFFORT", "CLAUDE_AGENT_SDK_VERSION"):
            env.pop(name)
    if env.get("WLM_CLAUDE_CONFIG_DIR"):
        env["CLAUDE_CONFIG_DIR"] = env["WLM_CLAUDE_CONFIG_DIR"]
    models = [model] if model else [config().get("model", "claude-fable-5-2"), config().get("fallback_model", "opus")]
    last = ""
    for m in dict.fromkeys(models):
        cmd = ["claude", "-p", "--model", m, "--system-prompt", SYSTEM, "--tools", "",
               "--setting-sources", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--no-session-persistence", "--output-format", "text"]
        if effort:
            cmd += ["--effort", effort]
        with tempfile.TemporaryDirectory(prefix="wlm-") as cwd:
            try:
                proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=cwd, env=env, timeout=300)
            except subprocess.TimeoutExpired:
                last = f"{m} timed out"
                continue
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip(), m
        last = f"{m} exited {proc.returncode}"
    raise EngineError(f"Claude failed ({last}). Run `claude` once to log in, or set \"model\" in {HOME}/config.json")


def echo(prompt, effort="low"):
    key = os.environ.get("ECHO_API_KEY", "").strip()
    if not key:
        raise EngineError("Set ECHO_API_KEY to use Echo (echo.fulcrum.inc). Never paste the key into a file in this repo.")
    body = {"model": "echo", "reasoning_effort": effort, "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]}
    if config().get("echo_persona"):
        body["persona"] = config()["echo_persona"]
    req = urllib.request.Request(ECHO_URL + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            result = json.load(r)
        return result["choices"][0]["message"]["content"].strip(), "echo"
    except urllib.error.HTTPError as e:
        raise EngineError(f"Echo returned HTTP {e.code} (503 means their service is down; 402 means no credits)") from None
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        raise EngineError("Echo could not be reached or sent back nothing") from None


def unwrap(text):
    text = text.strip()
    m = re.fullmatch(r"```(?:text|markdown|md)?\s*\n(.*?)\n```", text, re.S)
    return m[1] if m else text


# ---------- lint ----------

def layout_issues(text, layout):
    lines = [l for l in text.splitlines() if l.strip()]
    if layout == "titles":
        return [l for l in lines if len(l) > 100]
    if layout == "thread":
        return [p.strip()[:60] + "..." for p in re.split(r"(?m)^---\s*$", text) if len(p.strip()) > 280]
    if layout == "teleprompter":
        issues = [l for l in lines if re.match(r"^\s*(?:[-*+]\s|\d+[.)]\s)", l)]
        spoken = re.sub(r"(?m)^\*\*[^\n]+\*\*\s*$", "\n", text)
        for para in re.split(r"\n\s*\n", spoken):
            sentences = [s for s in re.split(r"[.!?]+(?:\s+|$)", para.strip()) if s.strip()]
            if len(para.split()) > 45 or len(sentences) > 2:
                issues.append(para.strip()[:60] + "...")
        return issues
    return []


def check(format_id, text):
    f = fmt(format_id)
    words, chars = len(text.split()), len(text)
    result = {"ok": True, "errors": [], "warnings": [], "stats": {"words": words, "chars": chars}}
    for rule in rules(format_id):
        hits, kind = [], rule["type"]
        flags = re.I if "i" in rule.get("flags", "") else 0
        if kind == "regex":
            hits = [m[0] for m in re.finditer(rule["pattern"], text, flags | re.M)]
        elif kind == "phrases":
            for p in rule["phrases"]:
                hits += [m[0] for m in re.finditer(r"(?<!\w)" + re.escape(p) + r"(?!\w)", text, re.I)]
        elif kind == "length":
            ln = f.get("length", {})
            n = chars if ln.get("unit") == "chars" else words
            if n < ln.get("min", 0) * 0.85 or n > ln.get("max", 10**9) * 1.15:
                hits = [f"{n} {ln.get('unit', 'words')}, want {ln.get('min')} to {ln.get('max')}"]
        elif kind == "layout":
            hits = layout_issues(text, f["layout"])
        if hits:
            issue = {"id": rule["id"], "message": rule.get("message", ""), "excerpt": "; ".join(hits)[:200]}
            result["warnings" if rule.get("severity") == "warn" else "errors"].append(issue)
    result["ok"] = not result["errors"]
    return result


# ---------- write ----------

def generate(format_id, facts, task=None, engine=None, model=None, effort=None, pieces=None):
    engine = engine or config().get("engine", "claude")
    prompt = assemble(format_id, facts, task, engine, pieces)
    if engine == "brief":
        return {"engine": "brief", "text": prompt, "check": None}
    run = (lambda p: echo(p)) if engine == "echo" else (lambda p: claude(p, model, effort))
    text, used = run(prompt)
    text = unwrap(text)
    result = check(format_id, text)
    if not result["ok"]:
        errors = "\n".join(f"- {e['message']} ({e['excerpt']})" for e in result["errors"])
        try:
            fixed, used = run(prompt + "\n\nRepair this piece, keep every fact:\n<piece>\n" + text +
                              "\n</piece>\nFix these problems:\n" + errors + "\nReturn only the fixed piece.")
            text, result = unwrap(fixed), check(format_id, unwrap(fixed))
        except EngineError as e:
            print(f"repair failed, keeping the first draft: {e}", file=sys.stderr)
    return {"engine": used, "text": text, "check": result}


# ---------- blind test ----------

FACTS_PROMPT = """Turn this piece of writing into plain neutral notes, the way someone would brief a ghostwriter.
First line: task: <what it is and about how long>. Then one bullet per fact, in order. If it answers someone, add
- Situation: <what they said>. Keep every fact, number and name. Use none of the writer's own phrasing, jokes or style.
Return only the notes.

<piece>
{piece}
</piece>"""

JUDGE_PROMPT = """Two pieces below were written from the same facts. One was written by a real person, {name}.
The other was written by an AI imitating them. Here are other real pieces by {name}, for reference:

{refs}

Piece A:
<a>
{a}
</a>

Piece B:
<b>
{b}
</b>

Which one did the real person write? Answer with exactly one letter, A or B, then one short sentence on why."""


def blind_test(format_id, rounds, model=None):
    pieces = examples(format_id)
    if len(pieces) < 3:
        sys.exit(f"{format_id} needs at least 3 real examples for a blind test (it has {len(pieces)}).")
    rounds = min(rounds, len(pieces))
    fooled, rows = 0, []
    name = config().get("name", "the writer")
    for i in range(rounds):
        held = pieces[-(i + 1)]
        rest = [p for p in pieces if p is not held]
        notes, _ = claude(FACTS_PROMPT.format(piece=held["text"]), model)
        fake = generate(format_id, notes, pieces=rest, model=model)["text"]
        real_first = random.random() < 0.5
        a, b = (held["text"], fake) if real_first else (fake, held["text"])
        refs = "\n\n".join(f"<example>\n{p['text']}\n</example>" for p in rest[:4])
        verdict, _ = claude(JUDGE_PROMPT.format(name=name, refs=refs, a=a, b=b), model)
        picked_real = verdict.strip().upper().startswith("A") == real_first
        fooled += 0 if picked_real else 1
        rows.append({"held_out": held["label"], "judge_fooled": not picked_real, "judge_said": verdict.strip()[:200],
                     "generated": fake})
        print(f"round {i + 1}: {'FOOLED' if not picked_real else 'caught'}  ({held['label']})", file=sys.stderr)
    out = HOME / "tests" / f"{format_id}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"format": format_id, "fooled": fooled, "rounds": rounds, "rows": rows}, indent=1))
    return fooled, rounds, out


# ---------- commands ----------

def cmd_init(args):
    HOME.mkdir(parents=True, exist_ok=True)
    reg = json.loads((TEMPLATES / "formats.json").read_text())
    chosen = set(args.formats.split(",")) if args.formats else None
    if chosen:
        reg["formats"] = [f for f in reg["formats"] if f["id"] in chosen]
    if not (HOME / "formats.json").exists() or args.force:
        (HOME / "formats.json").write_text(json.dumps(reg, indent=1))
    for name in ("core.md", "lint.json"):
        if not (HOME / name).exists():
            shutil.copy(TEMPLATES / name, HOME / name)
    if not (HOME / "config.json").exists():
        (HOME / "config.json").write_text(json.dumps(
            {"name": args.name or "me", "model": "claude-fable-5-2", "fallback_model": "opus", "engine": "claude"}, indent=1))
    for f in reg["formats"]:
        d = HOME / "formats" / f["id"]
        d.mkdir(parents=True, exist_ok=True)
        if not (d / "profile.md").exists():
            shutil.copy(TEMPLATES / "formats" / f["id"] / "profile.md", d / "profile.md")
        if not (d / "examples.md").exists():
            (d / "examples.md").write_text(
                f"# {f['name']}: your real pieces, best first\n\n"
                "<!-- One piece per '## label' heading. Only words you wrote yourself: no AI drafts, no ghostwriters.\n"
                "Keep your typos and quirks. Remove phone numbers and other people's emails. -->\n")
    print(f"Voice folder ready: {HOME}")
    print("Next: add your real writing to formats/<format>/examples.md, then fill core.md and each profile.md.")


def cmd_formats(args):
    need_home()
    for f in registry():
        n = len(examples(f["id"]))
        status = "ready" if n >= 5 else ("thin" if n else "empty")
        print(f"{f['id']:<22} {n:>3} examples  {status:<6} {f['summary']}")


def facts_arg(args):
    if args.facts == "-":
        return sys.stdin.read()
    return Path(args.facts).read_text(encoding="utf-8")


def cmd_write(args):
    need_home()
    try:
        out = generate(args.format, facts_arg(args), args.task, args.engine, args.model, args.effort)
    except EngineError as e:
        sys.exit(str(e))
    if args.out:
        Path(args.out).write_text(out["text"] + "\n")
    print(out["text"])
    print(f"engine: {out['engine']}", file=sys.stderr)
    if out["check"] is not None:
        print(json.dumps(out["check"], ensure_ascii=False), file=sys.stderr)


def cmd_brief(args):
    need_home()
    print(assemble(args.format, facts_arg(args), args.task))


def cmd_check(args):
    need_home()
    result = check(args.format, Path(args.file).read_text(encoding="utf-8"))
    print(json.dumps(result, indent=1, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)


def cmd_test(args):
    need_home()
    try:
        fooled, rounds, path = blind_test(args.format, args.rounds, args.model)
    except EngineError as e:
        sys.exit(str(e))
    print(f"{args.format}: the judge took Claude's piece for yours {fooled} of {rounds} times. Details: {path}")


def cmd_doctor(args):
    print(f"voice folder: {HOME} ({'ok' if (HOME / 'formats.json').exists() else 'missing, run init'})")
    print(f"claude: {'found' if shutil.which('claude') else 'missing'}")
    print(f"echo:   {'ECHO_API_KEY set' if os.environ.get('ECHO_API_KEY') else 'no key (optional)'}")


def cmd_pack(args):
    need_home()
    import zipfile
    out = Path(args.out).expanduser()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in SKILL_DIR.rglob("*"):
            rel = f.relative_to(SKILL_DIR)
            if f.is_file() and rel.parts[0] != "voice" and "__pycache__" not in rel.parts:
                z.write(f, Path("write-like-me") / rel)
        for f in HOME.rglob("*"):
            rel = f.relative_to(HOME)
            if f.is_file() and rel.parts[0] != "tests":
                z.write(f, Path("write-like-me/voice") / rel)
    print(f"Wrote {out}. Upload it in Claude: Settings, Capabilities, Skills.")


def main():
    p = argparse.ArgumentParser(prog="wlm", description="Claude writes in your voice.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--name"); s.add_argument("--formats"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("formats"); s.set_defaults(fn=cmd_formats)
    for name, fn in (("write", cmd_write), ("brief", cmd_brief)):
        s = sub.add_parser(name); s.add_argument("format"); s.add_argument("--facts", required=True, help="notes file, or - for stdin")
        s.add_argument("--task"); s.set_defaults(fn=fn)
        if name == "write":
            s.add_argument("--engine", choices=["claude", "echo", "brief"]); s.add_argument("--model")
            s.add_argument("--effort", choices=["low", "medium", "high"]); s.add_argument("--out")
    s = sub.add_parser("check"); s.add_argument("format"); s.add_argument("file"); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("test"); s.add_argument("format"); s.add_argument("--rounds", type=int, default=3); s.add_argument("--model"); s.set_defaults(fn=cmd_test)
    s = sub.add_parser("doctor"); s.set_defaults(fn=cmd_doctor)
    s = sub.add_parser("pack"); s.add_argument("--out", default=str(Path.home() / "Desktop" / "write-like-me-skill.zip")); s.set_defaults(fn=cmd_pack)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
