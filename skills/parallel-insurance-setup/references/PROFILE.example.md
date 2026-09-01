# Your insurance profile

Captured once during setup (`parallel-insurance-setup`) and read by every skill, so you
don't re-enter your context on every run. Setup writes this to `PROFILE.md` (which is
gitignored, your details stay local and are never committed). Edit it anytime.

Fill these in (setup does it for you, inferred from your organization and confirmed with you):

- **org:** <your organization name>
- **domain:** <yourorg.com>
- **org_type:** <e.g. carrier, MGA / MGU, TPA, broker, or reinsurer>
- **lines:** <lines of business: commercial property, P&C, workers' comp, specialty, etc.>
- **workflows:** <what you run: claims research, submission / underwriting, KYB / KYC, book monitoring>
- **rules_source:** <where your claim / underwriting rules live, so line-by-line research can apply them>
- **jurisdictions:** <the states / regions and any regulatory constraints that bound your book>

Example (illustrative, not a real organization):

- **org:** Harborline Specialty
- **domain:** harborline.example
- **org_type:** MGA / MGU
- **lines:** commercial property and light-manufacturing P&C, coastal-exposed
- **workflows:** submission triage, P&C underwriting risk profiles, contents-claim like-kind-and-quality research, book-wide catastrophe and sanctions monitoring
- **rules_source:** internal underwriting guidelines and claim-handling rules (referenced, not stored here)
- **jurisdictions:** Gulf and Southeast US; wind / flood exposure is the dominant driver
