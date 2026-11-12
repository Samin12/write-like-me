---
name: write-like-me
description: Write in the user's own voice, with a separate tested voice for each format (YouTube script, intro, titles, description, community/Skool post, comment, X post, reply, thread, LinkedIn post, newsletter, business email, personal email, DM). Use whenever the user asks to draft or rewrite anything that goes out under their name, asks to "write like me" or "in my voice", or wants to set up, test or improve their voice. Also use to check a draft against their voice.
---

# write-like-me

The user's voice lives in a plain folder: `~/.write-like-me` (or `$WLM_HOME`). Everything runs through one script:

```bash
WLM="python3 <this skill's base directory>/scripts/wlm.py"
```

`scripts/wlm.py` sits next to this SKILL.md (Python 3, standard library only). Below, `$WLM` means that command. Run `$WLM doctor` first if unsure what is set up.

## If the voice folder does not exist yet: set it up

Walk the user through this. Do the work yourself; ask only for what only they can give.

1. **Init.** Ask their name (how they sign things) and which formats they actually write. `$WLM init --name "<name>" --formats youtube-script,x-post,...` (all 14 if they are unsure). `$WLM formats` lists them.
2. **Collect their real writing.** 5 to 20 pieces per format is the target; 3 is the minimum for a test. Good sources:
   - YouTube: transcripts of their own videos (`yt-dlp --skip-download --write-auto-subs --sub-format vtt <url>`), their past titles and descriptions.
   - X: their archive export (`data/tweets.js`), or pasted posts. Skip retweets and quotes of others.
   - Skool / Circle / Discord: paste their own posts and comments.
   - Email: sent mail they typed themselves (a Gmail connector, an export, or pastes).
   - LinkedIn: the posts export. Newsletters: past issues.
   Only words the user wrote. Leave out anything written by AI, an assistant, an agency or a ghostwriter, even if it went out under their name: ask when unsure. Keep typos, slang, missing capitals and rough joins; those are the voice. Remove phone numbers, other people's email addresses and anything private.
3. **Write `formats/<id>/examples.md`.** One piece per `## <label>` heading, best and most typical first. The label says what it was ("reply to a member asking about pricing", "launch post"). It is shown to the writer as the situation, never copied.
4. **Write the voice.** Read all the examples, then fill in:
   - `core.md`: how they sound in every format. Concrete and quoted: their openers, joins, intensifiers, how they end, typed vs dictated register, and the phrases they never use.
   - each `formats/<id>/profile.md` under `## My patterns`: what is specific to that format (length, layout, greeting, sign-off or none, links, emoji). Every rule must be visible in their examples. Do not import generic "good writing" advice.
   - `lint.json`: add their never-phrases to the `ai-phrases` list, remove any phrase they genuinely use, and drop the hashtag or emoji rules if they use those.
5. **Blind test.** `$WLM test <format> --rounds 3` for each format with 3+ examples. It holds out one of their real pieces, turns it into neutral notes, writes a new piece from those notes, and asks a fresh Claude judge which one is real. Report "fooled N of M" per format. Then read the generated pieces in `~/.write-like-me/tests/<format>.json` against the real ones, tighten that `profile.md`, and test again. Two rounds is usually enough. Do not chase a perfect score: the goal is drafts they barely need to touch.

## Writing a piece

1. **Pick the format** from what they asked and who reads it. If two fit (business vs personal email), pick by the reader.
2. **Write the facts as plain notes** in a temp file: neutral bullets in order, no styling, none of your own phrasing for the voice to inherit. Keep their own words if they gave any. First line can be `task: <what and how long>`. For a reply add `- Situation: <what they said>`.
3. **Generate.** `$WLM write <format> --facts /tmp/facts.md` prints the piece, then the engine and the lint result on stderr. It is a clean `claude -p` call on the user's own subscription with no tools, memory or project files, so only the voice and the facts shape it. It repairs the draft once if lint finds errors.
4. **Check the facts yourself:** nothing invented, nothing that matters dropped. Fix small things by hand and re-run `$WLM check <format> draft.md`.
5. **Show the draft.** Say which format and engine wrote it. Writing is never publishing: do not post, send or schedule without the user's OK.

No `claude` CLI here (Claude desktop, claude.ai, another agent)? Use `$WLM brief <format> --facts f.md`. It prints the full prompt; write the piece yourself from it, following it exactly, then run `check`. In claude.ai the voice is the `voice/` folder packed inside this skill; the script finds it on its own.

To use the voice in claude.ai or Claude desktop, run `$WLM pack` (makes `~/Desktop/write-like-me-skill.zip` with the voice inside) and tell the user to upload it under Settings, Capabilities, Skills.

## Echo (optional)

Fulcrum's Echo (echo.fulcrum.inc) is a paid style-imitation model. If the user has credits, `export ECHO_API_KEY=...` in their own shell and use `$WLM write <format> --facts f.md --engine echo`. It sends the same examples and facts to Echo. Never write the key into a file in this repo. Echo is not needed: Claude is the default.

## Keep it learning

When the user edits a draft, put the before and after under `## Before and after` in that format's `profile.md`, and turn any pattern into a rule under `## My patterns`. When they write something new themselves, add it to `examples.md`. Re-run the blind test after a big change.
