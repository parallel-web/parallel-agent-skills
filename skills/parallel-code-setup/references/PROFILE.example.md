# Your code profile

Captured once during setup (`parallel-code-setup`) and read by every skill, so you don't
re-enter your stack on every run. Setup writes this to `PROFILE.md` (which is gitignored, your
details stay local and are never committed). Edit it anytime.

Fill these in (setup does it for you, inferred from your product and confirmed with you):

- **product:** <your product name>
- **domain:** <yourproduct.com>
- **product_type:** <e.g. coding agent, app builder / codegen platform, code-review tool, or an internal dev platform>
- **stack:** <the languages, frameworks, and key libraries you build on or generate>
- **integration:** <how you'd call Parallel: an agent tool, a build-step, a server-side API, or embedded per-user>
- **what_current_means:** <the release channels you track: stable only, latest minor, betas / RCs, or security patches>
- **priorities:** <what you most need to get right: no deprecated APIs, latest stable versions, CVE awareness, quotable citations>

Example (illustrative, not a real company):

- **product:** Foundry Labs
- **domain:** foundrylabs.example
- **product_type:** app builder / codegen platform (users describe an app, we generate it)
- **stack:** TypeScript, Next.js, React, Tailwind, Drizzle ORM, Postgres, Zod
- **integration:** a build-step plus an agent tool, called server-side on the user's behalf
- **what_current_means:** latest stable minor for framework deps; security patches applied promptly
- **priorities:** generated apps must resolve against current library versions and avoid deprecated APIs, every fix cites a live source
