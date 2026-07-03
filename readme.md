# Tom Bird's Skill Files

A collection of personal [Claude](https://claude.com/claude-code) skill files I've built for my own workflows — reports, documentation, automation, and more. This readme is the index: browse the table, then jump into any skill's own page for the full details.

## Skills

| Skill | What it does | Trigger | Docs |
|---|---|---|---|
| **[doc-me](doc-me/readme.md)** | Turns a screen recording into a polished, non-technical, step-by-step Markdown guide with screenshots — automatically. | `/doc-me` (with a recording attached) | [readme](doc-me/readme.md) |
| **[lets-go](lets-go/readme.md)** | A trip-planning assistant that acts like a travel agent — turning a rough idea into a bookable plan covering transport, weather, lodging, activities, food, and budget. | `/lets-go` | [readme](lets-go/readme.md) · [SKILL.md](lets-go/SKILL.md) |

---

### 📹 doc-me

Give it a screen recording and it detects every on-screen action, grabs a screenshot of each, transcribes any narration, and writes plain-language numbered steps — packaged into a single portable folder you can hand to anyone.

- **Best for:** SOPs, how-to guides, onboarding docs, and turning a Loom/Zoom/Scribe recording into written instructions.
- **Ships with scripts:** frame-diff screenshot extraction (OpenCV) and optional audio transcription (faster-whisper) — the whole folder must travel together.
- **Packaged skill:** [`doc-me.skill`](doc-me/doc-me.skill) for install via the Skills panel.

→ **[Full documentation](doc-me/readme.md)**

### ✈️ lets-go

Turns a trip idea into a confident, practical plan. It front-loads a short intake (location, date, transportation, duration), figures out the travel type (solo / couple / family / friends), then researches against live data and presents a structured plan with a real recommendation.

- **Best for:** weekend getaways, family trips, group trips with friends, and international travel planning.
- **Handles the edge cases:** international entry requirements, transport logistics, accessibility and dietary needs, seasonal timing, weather contingencies, and per-person cost-splitting for group trips.
- **Never invents facts:** uses live/current data or clearly-labeled estimates for weather, prices, and availability.

→ **[Full documentation](lets-go/readme.md)**

---

## Repository layout

```
claude-skills/
├── readme.md          # you are here — the index
├── doc-me/            # screen-recording → step-by-step guide
│   ├── readme.md
│   ├── doc-me.skill   # packaged skill
│   └── scripts/
└── lets-go/           # trip-planning assistant
    ├── readme.md
    └── SKILL.md
```

## Using these skills

Each skill folder is self-contained. To use one:

- **Copy the folder** into your own skills directory, or
- **Install a packaged `.skill` file** (where provided) via **Add** in the Claude Skills panel.

Then trigger it with its slash command (e.g. `/lets-go`), or just describe what you want — most skills also fire on a matching natural-language request.

## License / Usage

These skills are free and open to use however you like — copy them, modify them, adapt them for your own workflows, or use them as a starting point for something else. No attribution required, no restrictions. Use them any way you please.

## Disclaimer

These were built for my own personal use, so they may reference specific tools, IDs, or workflows that won't apply to your setup. Feel free to strip those out and adapt as needed.
