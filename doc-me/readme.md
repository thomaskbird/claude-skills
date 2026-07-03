# doc-me

Turns an uploaded screen recording into a polished, non-technical, step-by-step Markdown guide with screenshots — automatically.

## What it does

Give it a screen recording (any video format), and it will:

1. Detect every distinct on-screen action (clicks, typed text, page transitions) and grab a screenshot of each one
2. Try to transcribe any narration for extra context (falls back cleanly if that's not possible — see [Limitations](#limitations))
3. Write plain-language, numbered steps that match what's actually visible in each screenshot
4. Package everything into a single self-contained folder you can hand to anyone

No manual screenshotting, no narrating your own actions into a doc — you record once, and this does the write-up.

## Triggering it

Type `/doc-me` with a screen recording attached (or upload the recording first and follow up with `/doc-me`).

It will also fire without the slash command if you upload a screen recording and ask for something like:
- "turn this into a guide / SOP / how-to"
- "document this workflow"
- "write up the steps in this recording"
- "turn this Loom/Zoom/Scribe recording into instructions"

If you type `/doc-me` with nothing attached, it'll just ask you to upload the recording rather than guessing.

## Output structure

Every run produces a single self-contained folder:

```
<inferred-task-name>/
├── guide.md
└── screenshots/
    ├── step-01.png
    ├── step-02.png
    └── ...
```

`guide.md` uses relative image paths (`screenshots/step-01.png`), so the folder is portable — move it, zip it, or drop it in a wiki, and the images still resolve. The task name and step titles are inferred from what's actually in the recording; you don't need to supply a title upfront unless the recording is too ambiguous to tell.

## Required files

This skill is **not just `SKILL.md`** — it depends on two bundled scripts to actually do the work. `SKILL.md` tells Claude to run them by path, so all three files must ship together, in this exact layout:

```
doc-me/
├── SKILL.md
└── scripts/
    ├── extract_keyframes.py      # frame-diff based screenshot extraction (OpenCV)
    └── transcribe_audio.py       # optional narration transcription (faster-whisper)
```

If you clone/fork this into another repo or hand it to someone else, they need the whole folder — `SKILL.md` alone will trigger the skill but every step will fail trying to call scripts that aren't there.

## How the extraction actually works

`extract_keyframes.py` samples the video and looks for moments where the screen changes and then *stabilizes* — i.e. right after a click or transition finishes, not mid-animation. It captures one screenshot per stabilization point.

**Important calibration note:** the diff threshold is tuned against real recorded software UI, not intuition. A meaningful UI change (a typed character, a new row appearing in a list) typically shifts the full-frame mean color diff by only **0.2–1.6**, because the changed region is usually a small fraction of the screen. Full-page navigations typically produce **5+**. The shipped defaults (`--change-thresh 0.5`, `--min-gap-seconds 1.0`) reflect this. Earlier defaults calibrated on a synthetic full-screen test (threshold 6.0) silently missed nearly every real click in testing — if you ever see a run that captures suspiciously few screenshots for a long recording, threshold miscalibration is the first thing to check.

Tuning knobs if a specific recording needs it:
| Symptom | Fix |
|---|---|
| Too many near-duplicate screenshots (busy/animated UI) | raise `--change-thresh` and/or `--min-gap-seconds` |
| Missing real actions (sparse output) | lower `--change-thresh` further |
| Long recording getting cut off | raise `--max-frames` (default 60) |

## Limitations

- **Transcription needs internet access to Hugging Face.** `transcribe_audio.py` uses `faster-whisper`, whose model weights download from `huggingface.co`. In network-restricted sandboxes (this includes Claude's default compute environment, whose allowlist doesn't include Hugging Face) transcription will fail and the skill silently falls back to visual-only documentation. This is by design — not a bug — but worth knowing if narration seems to be getting ignored. In an environment with broader network access, transcription works automatically with no changes needed.
- **It won't include speech it can't transcribe.** If you narrate important context that never appears on screen, that context is lost when transcription is unavailable.
- **It uses judgment on messy recordings.** Repetitive actions (e.g. adding six users one at a time) get written up once with a "repeat for each X" note, not as six near-identical steps. Incidental detours (wrong clicks, backtracking, a browser autofill popup) are left out of the polished guide rather than documented as if intentional. This means the output is a *clean tutorial*, not a literal transcript of the recording — if you need a literal record of exactly what happened, this isn't the right tool.
- **Very long recordings (10+ min) get capped** at 60 extracted steps by default rather than silently truncated — the skill should flag this and offer to split into multiple guides or focus on a section.

## Requirements

- `ffmpeg` and `ffprobe` (audio/video handling)
- Python 3 with `opencv-python`, `numpy`, `pillow` (screenshot extraction)
- `faster-whisper` (optional, auto-installed on first transcription attempt if network access allows)

All of the above except `faster-whisper`'s model download are already available in Claude's standard compute environment — no setup needed there.

## Packaging / distribution

To share this skill or move it to another environment, package it as a `.skill` file rather than copying `SKILL.md` alone, so the bundled scripts travel with it:

```bash
python3 -m scripts.package_skill /path/to/doc-me /path/to/output/dir
```
(using Anthropic's `skill-creator` packaging script). The resulting `.skill` file can be installed via **Add** in the Skills panel.
