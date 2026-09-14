# The Avengers — agent roster

Named agents that live in this repo. One file per agent, `<call-sign>.md`, with YAML
frontmatter (`name`, `description`, `tools`, `model`) followed by the agent's operating
instructions. Claude Code loads everything in this directory automatically, so a new
member is live as soon as the file lands — no registration step.

The `description` is the only thing the main thread reads when deciding whom to call, so
write it as a trigger — what the agent does *and* when to reach for it — not as a title.

| Call sign | Role | Reach for it when |
|---|---|---|
| **Eson** the Searcher | Prospecting. Sweeps Google, Facebook and public directories for businesses with no website, a Facebook-only presence, or a broken or dated site. Returns a verified, scored call sheet. | "Find me companies that need a website", "who in Marion County has no site", building a lead list for a town or trade |

## Working rules for the team

- **Nothing is invented.** Every factual claim an agent returns traces to a source. This
  is the rule the whole repo is built on — see `docs/PLAYBOOK.md` §1.
- **Public sources only.** No logged-in scraping, no bypassing robots.txt, no personal
  data.
- **State what was checked and what was not.** An unverified field is marked unverified,
  never filled with something plausible.

## Adding a member

1. Write `.claude/agents/<call-sign>.md` with the frontmatter above.
2. Give it a real methodology, not a job title — phases, the checks it must not skip, and
   the failure modes that will bite it.
3. If it produces structured output, give it a tool in `tools/` that validates and stores
   that output. An agent writing free-form prose into a file drifts; an agent feeding a
   schema does not.
4. Add a row to the table here.
