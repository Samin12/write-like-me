# Example outputs

Everything shown in the README images, as text. All written in Samin's voice by his own version of this system (Claude Fable 5.2), from the facts below. Nothing was edited by hand.

## The facts

```text
task: announce a free open-source tool to the community
- Fulcrum released Echo on Sep 30, a writing model that copies anyone's style. It beat frontier models at style imitation and cost under $5K to train.
- Echo was paid only: you bought credits on their site, and the service was down a lot.
- On Nov 9 Fulcrum open-sourced the weights. It is a small add-on (a LoRA) for Kimi K3.
- Kimi K3 is 2.8 trillion parameters, over a terabyte even compressed. You cannot run it at home, not even on a Mac Studio with 256 GB.
- Echo's trick is that the base model already knows how people write. Their training just teaches it to use that, by pairing an outline with the real post.
- I did the same trick on top of Claude, using the Claude subscription you already pay for. No new model, a small skill.
- You give it your own writing, it builds a separate voice for each format: YouTube scripts, titles, Skool posts, X posts, emails, DMs.
- It writes, then checks the draft against your rules (no em dashes, phrases you never use) and fixes it.
- On my own writing, blind judges picked the AI title over my real one about half the time.
- It's called write-like-me, free on GitHub, installs as a Claude Code plugin in two commands.
```

## x-post

```text
Fulcrum open sourced Echo but its a LoRA for Kimi K3 and you cant run that at home

So I did the same trick on top of claude with the subscription you already pay for

Its called write-like-me, free on GitHub and installs as a claude code plugin in two commands
```

## youtube-title

```text
Claude's New Writing Skill Is Insane! (Free Tutorial)
Claude Just Changed AI Writing Forever! (Tutorial)
How to Make Claude Write Like You Better Than 99% of People
DON'T Pay for Echo, Make Claude Write Like You! (Free)
Claude Can Now Write Exactly Like You! (Free Open Source)
```

## skool-post

```text
Title: I built a free skill that writes like you

Hey guys, so Fulcrum released Echo on Sep 30. It's a writing model that copies anyone's style. It beat the frontier models at style imitation and cost under $5K to train. But it was paid only, you had to buy credits on their site and it was down a lot.

On Nov 9 they open sourced the weights. The problem is it's a small add-on, a LoRA, for Kimi K3, and Kimi K3 is 2.8 trillion parameters. That's over a terabyte even compressed. You can't run that at home, not even on a Mac Studio with 256 GB.

The trick with Echo is the base model already knows how people write. Their training just teaches it to use that, by pairing an outline with the real post. So I did the same trick on top of Claude, with the Claude subscription you already pay for. No new model, it's just a small skill.

You give it your own writing and it builds a separate voice for each format, so YouTube scripts, titles, Skool posts, X posts, emails, DMs. It writes the draft, then checks it against your rules, like no em dashes or phrases you never use, and fixes it.

I ran it on my own writing and blind judges picked the AI title over my real one about half the time.

It's called write-like-me. It's free on GitHub and installs as a Claude Code plugin in two commands
```

## x-thread

```text
Made a free tool that gets Claude to write like you. It's called write-like-me and it's open source on GitHub

---

Fulcrum released Echo on Sep 30, a writing model that copies anyone's style. Beat the frontier models at it and cost under $5K to train

But it was paid only, you bought credits on their site and it was down a lot

---

On Nov 9 they open sourced the weights

But its a small LoRA for Kimi K3, which is 2.8 trillion parameters and over a terabyte even compressed. You cant run that at home, not even on a Mac Studio with 256 GB

---

The trick is the base model already knows how people write. Their training just teaches it to use that by pairing an outline with the real post

So I did the same thing on top of Claude, with the subscription you already pay for. No new model, just a small skill

---

You give it your own writing and it builds a separate voice for each format. YouTube scripts, titles, Skool posts, X posts, emails, DMs

It writes, then checks the draft against your rules like no em dashes or phrases you never use, and fixes it

---

On my own writing blind judges picked the AI title over my real one about half the time

Installs as a Claude Code plugin in two commands
```

## youtube-intro

```text
Fulcrum just open sourced Echo, their writing model that copies anyone's style, and I took the same trick it uses and built a free version that runs on the Claude subscription you're already paying for.

So, Echo came out on September 30th, and it beat the frontier models at style imitation, and it cost them under 5 thousand dollars to train.

But it was paid only, so you had to buy credits on their site, and the service was down a lot.

Then on November 9th, they open sourced the weights.

But Echo is just a small add-on called a LoRA that sits on top of Kimi K3.

And Kimi K3 is 2.8 trillion parameters, which is over a terabyte even compressed.

So you can't run it at home, not even on a Mac Studio with 256 gigs.

And the trick behind Echo is that the base model already knows how people write, and their training just teaches it to use that by pairing an outline with the real post.

So, I did the same thing on top of Claude, and there's no new model, it's just a small skill.

You give it your own writing, and it builds a separate voice for each format, so YouTube scripts, titles, Skool posts, X posts, emails and DMs.

Then it writes, checks the draft against your rules, like no em dashes or phrases you never use, and fixes it.

And on my own writing, blind judges picked the AI title over my real one about half the time.

It's called write-like-me, it's free on GitHub, and it installs as a Claude Code plugin in two commands.

So, in this video, I'm going to be showing you how it works and how to get it set up.

Let's get into it.
```

## Reply facts

```text
task: reply, about 25 words
- Situation: a Claude Club member asked if they need to pay for Echo to use write-like-me
- No. It runs on your Claude subscription.
- Echo is optional if you already have credits.
```

## skool-comment

```text
nope you dont need to pay for echo it just runs on your claude subscription. echo is optional if you already have credits
```

## email-personal

```text
Hey no you dont need to pay for Echo, it just runs on your claude subscription. Echo is optional if you already have credits
```

## For comparison: plain Claude, no write-like-me

Prompt: "Write an X post as Samin Yasar (YouTuber who makes Claude tutorials and runs the Claude Club community on Skool), in his voice, from these facts." Same model, same facts.

```text
Fulcrum just open-sourced Echo, the writing model that copies anyone's style.

Quick backstory: Echo came out Sep 30. It beat frontier models at style imitation and cost under $5K to train. But it was paid only. You bought credits on their site, and the service was down a lot.

On Nov 9 they released the weights. Sounds great, except there's a catch.

Echo is a small add-on (a LoRA) for Kimi K3. Kimi K3 is 2.8 trillion parameters. That's over a terabyte even compressed. You can't run it at home, not even on a Mac Studio with 256 GB.

So I looked at how Echo actually works, and the trick is simple. The base model already knows how people write. Their training just teaches it to use that, by pairing an outline with the real post.

I did the same trick on top of Claude, using the Claude subscription you already pay for. No new model, just a small skill.

It's called write-like-me. Here's what it does:

1. You give it your own writing
2. It builds a separate voice for each format: YouTube scripts, titles, Skool posts, X posts, emails, DMs
3. It writes a draft, checks it against your rules (no em dashes, phrases you never use), and fixes it

I tested it on my own writing. Blind judges picked the AI title over my real one about half the time.

It's free on GitHub and installs as a Claude Code plugin in two commands.

Link below 👇
```
