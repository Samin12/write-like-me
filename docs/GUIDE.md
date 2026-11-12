# write-like-me: the setup guide

This takes about 20 minutes the first time. Most of it is gathering your own writing. Claude does the rest.

## Before you start

- **Claude Code**, logged in with your Claude subscription. Check with `claude --version`. Install: [claude.com/claude-code](https://claude.com/claude-code).
- **Python 3.** Already on every Mac. On Windows, install it from python.org.
- Optional: **yt-dlp** for YouTube transcripts (`brew install yt-dlp`).

## Step 1. Install the plugin

Open Claude Code anywhere and run:

```text
/plugin marketplace add Samin12/write-like-me
/plugin install write-like-me@write-like-me
```

Restart Claude Code if the commands don't show up yet.

## Step 2. Start setup

```text
/write-like-me:setup
```

Claude asks two things:

1. **Your name**, the way you sign things.
2. **Which formats you write.** Pick only what you actually write. You can add more later.

It creates your voice folder at `~/.write-like-me/`.

## Step 3. Give it your real writing

This is the part that matters. The voice is only as good as the examples.

**The one rule: only words you wrote yourself.** No ChatGPT drafts, no posts your VA or agency wrote, no AI-polished emails, even if they went out under your name. If you're not sure, leave it out.

**Keep the mess.** Typos, missing capitals, run-on sentences, "lol" at the end. That's your voice. Cleaning it up teaches Claude to write cleaner than you, which is exactly what gives AI away.

Aim for **5 to 20 pieces per format**, your most typical ones first. 3 is the minimum to run a test.

Where to find your writing:

| Format | Where it lives | How to get it |
|---|---|---|
| YouTube scripts and intros | Your videos | Give Claude the URLs. It runs `yt-dlp --skip-download --write-auto-subs <url>` and keeps only your talking. Or paste a script you wrote. |
| YouTube titles | YouTube Studio | Paste your last 20 titles. Your best performers first. |
| YouTube descriptions | YouTube Studio | Paste 3 to 5 recent ones. |
| Skool / community posts | Your community | Open your profile, copy your own posts, paste them in. |
| Comments | Your community | Copy 10 or so of your replies to members. |
| X posts, replies, threads | X | Settings → Your account → Download an archive. Point Claude at `data/tweets.js`. Or paste them. |
| LinkedIn | LinkedIn | Settings → Data privacy → Get a copy of your data → Posts. |
| Newsletter | Your email tool | Paste 2 to 4 past issues. |
| Emails | Gmail sent folder | Paste emails you typed yourself, or let Claude read them if you have a Gmail connector. |
| DMs | Any app | Paste a few of your own messages. Leave the other person's messages out. |

Remove phone numbers, other people's email addresses and anything private before you hand it over.

Claude sorts everything into `~/.write-like-me/formats/<format>/examples.md`. Each piece gets a `## label` line that says what it was, like `## reply to a member asking about pricing`.

## Step 4. Claude writes your voice

From your examples, Claude fills in three things. You don't have to write them, but read them, because you'll spot anything wrong right away.

- **`core.md`**: how you sound everywhere. Your openers, how you join sentences, your favorite words, how you end, and the phrases you never use.
- **`formats/<format>/profile.md`**: what's specific to each format. Length, layout, greeting, sign-off, emoji, links.
- **`lint.json`**: the hard rules a draft gets checked against. Phrases you never use go here.

## Step 5. The blind test

Claude runs this on every format with 3 or more examples:

1. It holds back one piece you really wrote.
2. It turns that piece into plain notes, like a brief you'd give a ghostwriter.
3. It writes a new piece from those notes in your voice.
4. A fresh Claude, which hasn't seen any of this, gets both pieces and has to pick the real one.

You get "the judge took Claude's piece for yours N of 3 times" for each format. Then Claude compares the drafts with your real writing, fixes the profiles, and tests again.

What good looks like:

- **Titles, X posts, DMs, emails:** fooling the judge some of the time is great.
- **Long posts and scripts:** expect the judge to catch them. What you want is a draft you only need to touch up.

Don't chase a perfect score. Chase drafts you'd post after a quick read.

## Step 6. Write

Just ask Claude like you normally would. The skill picks it up:

```text
write a skool post about tonight's live call, 8pm EST, we're building a CRM with Claude
reply to this comment: "does this work on windows?" (yes, as long as you have python)
5 titles for my video about AI agents that trade stocks
```

Or be explicit:

```text
/write-like-me:write an X post about my new video on Claude Code hooks
```

You get the draft, the format it used, and whether it passed the check. It never posts or sends anything.

**Tip:** the more your request reads like facts and the less it reads like a style ("make it punchy!"), the more it sounds like you. Style comes from your examples, not the request.

## Step 7. Keep it learning

- **When you edit a draft**, paste your version back and say "learn from my edit". Claude saves the before and after to that format's profile, and turns patterns into rules.
- **When you write something yourself**, add it to that format's `examples.md`.
- **If a phrase keeps showing up** that you'd never say, tell Claude to add it to your lint rules.
- **Re-test** after big changes: `/write-like-me:test`.

## Using it in claude.ai or the Claude app

After setup, say "pack my voice for claude.ai". You get `write-like-me-skill.zip` on your Desktop with your voice inside. Upload it in Claude: Settings → Capabilities → Skills. Re-pack whenever you improve your voice.

## Troubleshooting

- **"Claude failed (... exited 1)"**: run `claude` once in a terminal and make sure you're logged in. If your plan doesn't have Claude Fable 5.2, set `"model": "opus"` in `~/.write-like-me/config.json`.
- **Drafts sound too clean**: add more raw examples (quick replies, dictated posts), and add your edits as before/after.
- **Wrong length**: change `length` for that format in `~/.write-like-me/formats.json`.
- **It keeps using a phrase you hate**: add it to the `ai-phrases` list in `~/.write-like-me/lint.json`.
- **Something else**: `python3 <skill folder>/scripts/wlm.py doctor`, or open an issue on GitHub.
