# Your productivity profile

Captured once during setup (`parallel-productivity-setup`) and read by every skill, so you
don't re-enter your context on every run. Setup writes this to `PROFILE.md` (which is gitignored,
your details stay local and are never committed). Edit it anytime.

Fill these in (setup does it for you, inferred from your product and confirmed with you):

- **product:** <your product name>
- **domain:** <yourproduct.com>
- **product_type:** <e.g. AI assistant, agent, note-taker, workspace / knowledge tool, or companion app>
- **surfaces:** <where research shows up: an inline chat answer, a doc, a meeting brief, a feed, a notification>
- **entities:** <the people, companies, places, and topics your product touches most>
- **latency_need:** <in the request path (sub-2s) for inline answers, or async for background enrichment>
- **keep_current:** <the topics, sources, and entities your users want kept fresh>

Example (illustrative, not a real product):

- **product:** Cadence AI
- **domain:** cadence.example
- **product_type:** AI assistant / workspace with meeting notes
- **surfaces:** inline chat answers, auto-generated meeting briefs, and a per-account live feed
- **entities:** the companies and people in a user's accounts and calendar
- **latency_need:** sub-2s for inline answers; async for meeting briefs and feed updates
- **keep_current:** job changes, fundraises, and major announcements for the companies each user tracks
