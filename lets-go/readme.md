# lets-go

A trip-planning assistant that acts like a practical travel agent — turning a rough idea into a confident, bookable plan covering transportation, weather, lodging, activities, food, budget, and the things you need to know before you go.

## What it does

Give it a trip idea, and once it has the essentials it will:

1. Confirm the four details it can't plan without (location, date, transportation, duration)
2. Research the trip against live/current web data instead of memorized facts
3. Work out the logistics — drive time and fuel or flight character, parking, and whether you'll need a car on-site
4. Pull a weather outlook (real forecast when close enough, clearly-labeled seasonal estimate otherwise) and flag weather risk with a backup
5. Recommend lodging, things to do, and dining tailored to who's traveling, with realistic price ranges
6. Build a right-sized itinerary — none for a day trip, a day-by-day plan for longer or multi-destination trips
7. Estimate total cost, compared against a budget if one was given
8. Cover the "before you go" details: what to book ahead, seasonal/event notes, and — for international trips — entry requirements, currency, and safety
9. Assemble it all into a structured write-up ending with a real recommendation

The upfront intake step exists on purpose: trip research is expensive to redo, so a brief check for missing details saves far more time than guessing wrong and throwing out the whole plan.

## Triggering it

Type `/lets-go`, or just describe a trip you want help planning ("plan a weekend in Asheville", "we want to drive somewhere warm next month").

If required details are missing, it asks only for the missing pieces — plus at most one smart follow-up when the answer would change the whole plan — in a single short message. It won't start researching until the four essentials are in hand.

## The 4 required details

Before any research happens, the skill needs all of these:

| Detail | What counts |
|---|---|
| **Location** | A destination, region, landmark, address, city/state, zip, or usable travel area (vague-but-directional like "somewhere warm within driving distance of X" is fine) |
| **Date/time** | At minimum a month/day, or a resolvable relative date ("this weekend", "next Friday") |
| **Transportation** | Car, plane, train, bus, walking, rideshare, transit, RV, cruise, etc. (inferred and confirmed when strongly implied) |
| **Duration** | Trip length or a clear date range (1 day, a weekend, 4 nights, a week) |

Vague-but-usable answers are accepted at face value. The skill only pushes back on genuinely un-actionable inputs like "somewhere fun" with no other anchor.

## Edge cases it handles

- **International & cross-border trips** — passport/visa/entry requirements, currency and tipping, language, time zone, power plugs, connectivity, vaccinations, and travel advisories (always pointing to official sources to verify)
- **Transportation logistics** — drive time and fuel/EV-charging cost, tolls, parking, flight routing, and whether a car is needed at the destination
- **Travel type** — inferred from what you say, or asked directly ("just you, a couple, a family, or a group of friends?") when unclear; solo, couple, family, friend group, and multi-household trips each get tailored lodging, activity, dining, and pace choices
- **Group cost-splitting** — *only* for friend groups and multi-household trips, and only after confirming you want it, it presents a **per-person** cost breakdown, separating shared costs (lodging, rental car, fuel) from individual ones, shows the split math, and flags costs that don't divide evenly. Solo, couple, and family trips get a single trip total
- **Stated needs as hard requirements** — accessibility, dietary restrictions/allergies, pets, and budget caps are planned around, not around
- **Weather contingencies** — flags heat, cold, storm/monsoon/hurricane season, and short daylight, with an indoor backup when weather is a real risk
- **Seasonal & timing awareness** — peak vs. off-peak, holidays and festivals, and seasonal closures
- **Special occasions** — honeymoons, milestones, and anniversaries get tailored tone and picks
- **Follow-ups & changes** — re-runs only the research a change affects and keeps the same structure so plans are easy to compare

## Default assumptions

If optional details aren't given, the skill assumes and then states explicitly:

- Travelers: 2 adults and 1 child
- Budget: mid-range
- Food: casual, family-friendly meals
- Lodging: clean, safe, good value, appropriate for the group
- Activities: practical and appropriate for the group
- Pace: relaxed, not packed

These are always surfaced in the final write-up so the user can correct any that don't apply.

## Output structure

Completed plans follow a consistent shape, including only the sections that apply to the trip:

```
## Trip Plan Summary

### Confirmed Details
### Weather Outlook
### Getting There & Around
### Best Lodging Options       (only if duration > 1 day)
### Suggested Itinerary        (only for multi-day trips)
### Top Things To Do
### Food & Dining
### Estimated Trip Cost        (single total; per-person breakdown only for cost-splitting groups)
### Before You Go              (bookings, seasonal notes, entry requirements, safety)
### Recommendation            (a real opinion, not a recap)
```

## Guardrails

A plan built on invented numbers is worse than no plan — it sets the user up for a closed attraction, a booked-out hotel, or a rainstorm. So the skill:

- Never researches until all 4 required fields are collected
- Never invents current prices, availability, forecasts, attraction hours, or entry/visa rules — it uses live data or a clearly-labeled estimate
- Never presents an estimate as confirmed pricing or availability
- Never treats visa, vaccination, or safety-advisory info as authoritative — it directs users to official sources
- Treats stated accessibility, dietary, budget, and traveler constraints as hard requirements
- Is honest about trade-offs — if the dates are bad, the budget is tight, or the destination is booked out, it says so and offers a better option

## Files

```
lets-go/
├── SKILL.md    # the skill instructions Claude follows
└── readme.md   # this file
```

`SKILL.md` is self-contained — there are no bundled scripts or external dependencies. Beyond that, the skill relies on live web access to research current weather, pricing, availability, and travel requirements.
