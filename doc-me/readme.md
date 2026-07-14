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
├── analytics.json
└── screenshots/
    ├── step-01.png
    ├── step-02.png
    └── ...
```

`guide.md` uses relative image paths (`screenshots/step-01.png`), so the folder is portable — move it, zip it, or drop it in a wiki, and the images still resolve. The task name and step titles are inferred from what's actually in the recording; you don't need to supply a title upfront unless the recording is too ambiguous to tell.

## Run analytics

Every run also produces `analytics.json` (in the task folder, alongside `guide.md`) plus a short chat summary, covering what's actually measurable in this environment: total wall-clock run time, video duration/resolution, how many raw screenshots were extracted vs. how many made it into the final guide, whether transcription was available, and the output folder size.

**This does not include token or dollar-cost figures.** There's no tool available to a skill running inside a conversation that can introspect its own token usage — so rather than fabricate a number, it's left out. If you want real token/spend numbers, they exist at the org level: **Settings → Analytics** in claude.ai, visible to Team/Enterprise plan Owners and Primary Owners (per-user, per-model token consumption and spend, exportable as CSV) — just not queryable per-run from inside a skill.

Example `analytics.json`:
```json
{
  "task_name": "add-users-to-a-group",
  "generated_at": "2026-07-14T18:32:00Z",
  "video": {"duration_seconds": 133.6, "resolution": "1918x990", "fps": 30},
  "extraction": {"raw_keyframes": 42, "time_seconds": 6.1},
  "transcription": {"available": false, "reason": "no network access to model host", "time_seconds": 3.2},
  "guide": {"steps": 7, "keyframes_used": 7, "keyframes_dropped": 35},
  "output_size_bytes": 3182441,
  "total_run_time_seconds": 96.4
}
```

## Batch mode for long recordings

Recordings longer than **~6 minutes** are automatically processed in ~4-minute chunks instead of one single pass. This exists because a single pass on a long recording means extracting dozens of screenshots, viewing all of them, and writing the whole guide before anything is saved to disk — if the run gets interrupted partway (e.g. hitting a turn's tool-call budget), everything is lost. This isn't hypothetical: an early real-world test on a 58-minute recording hit exactly this failure mode and never finished.

How it works:
- Each chunk is extracted, transcribed (if available), viewed, and written up independently, then **appended** to a `guide_draft.md` working file
- Progress is checkpointed to `progress.json` after every chunk (chunks completed, next keyframe index, whether transcription is available)
- If a run has to stop before all chunks are done, it stops cleanly at a chunk boundary — never mid-chunk — and says so, rather than silently truncating
- The next message resumes from `progress.json` instead of redoing finished work
- `extract_keyframes.py` and `transcribe_audio.py` both support `--start-seconds`/`--end-seconds` for this, with `--index-start` (keyframes) and `--chunked` (transcription) to keep numbering and transcript segments unified across chunks rather than restarting at zero each time
- Once transcription fails on one chunk due to no model/network access, later chunks don't keep retrying it — that reason is recorded once and the rest of the run just proceeds visual-only

`progress.json` and `guide_draft.md` are working files only — they don't appear in the final delivered folder, which still looks exactly like the [Output structure](#output-structure) above regardless of whether batch mode ran.

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
- **Very long recordings are chunked automatically (see [Batch mode](#batch-mode-for-long-recordings)), not silently truncated** — `--max-frames` is still a per-chunk safety cap (default 60), not a whole-video cap, so a long recording no longer risks losing everything if a run gets interrupted.

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
