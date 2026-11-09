# Emergency Handling Managed Agents Demo

A fictional household emergency exercise using Anthropic **Managed Agents**,
not a client-side simulation of agents. All code, inputs, skills, deployment IDs
and outputs live here. Only the root virtualenv, requirements and `.env` are shared.

## Run

From the repository root in PowerShell, with `ANTHROPIC_API_KEY` in the root
`.env` or process environment:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe emergency-handling/setup_demo.py
& .\.venv\Scripts\python.exe emergency-handling/run_emergency.py
```

The installed Anthropic SDK must expose `client.beta.agents`, `sessions`,
`environments` and `skills` (verified here with version 2.6.0). The API key must
have Managed Agents beta access. The root requirements now require this SDK minimum. Commands
also work from this directory using `..\.venv\Scripts\python.exe`.

Open `outputs/emergency-plan.html` directly in a browser; no server is needed.
The orchestrator returns the **entire HTML in its client message**, not just a
remote artifact. The client retrieves durable, paginated session events,
extracts that HTML, validates basic static structure, and atomically saves it.
Validation is a basic guard, not a comprehensive HTML security sanitizer.

## Team And Ordering

1. Coordinator delegates only to Emergency Researcher and waits for its dossier.
2. Coordinator gives that dossier and household input to Mental Support,
   Logistics and Survival, and Medical specialists, preferably in parallel.
3. After all replies, the coordinator reconciles them and returns one styled,
   responsive, printable HTML page with findings, action owners, mental support,
   medical FAQ, sources, resource calculations and unknowns.

Ordering is specified in managed-agent instructions, then checked against the
actual delegation/reply events before a report is accepted. This is not a
server-enforced dependency graph. A violation or missing reply fails the run;
it never silently presents an incomplete team result as success.

## Inputs And Research

`synthetic-data/household-flood.json` includes emergency description/types,
fictional location, four household members, accessibility and health needs,
inventory, expertise, priorities and unknowns. The demo combines flood, power
outage and water outage. Use `--input PATH` for another JSON input with the same
shape. Supported types: `power_outage`, `water_outage`, `flooding`, `wildfire`,
`earthquake`, `hurricane`, `zombie_apocalypse`.

`skills/emergency-research/` is uploaded as a custom skill attached only to the
researcher. It contains fictitious third-party municipal, utility and health
bulletins, plus general preparedness guidance for all supported types. The
other agents receive the researcher's structured dossier. If the incident ID
does not match, local conditions must be reported as unknown. Add matching
fictional research for a new scenario and rerun setup to publish a new version.
General official reference URLs are not live local research or current alerts.

## Configuration And Recovery

- `EMERGENCY_MODEL`: specialist model; default `claude-haiku-4-5-20251001` for low latency.
- `EMERGENCY_COORDINATOR_MODEL`: coordinator model; default `claude-sonnet-4-6`, with explicit low reasoning effort; rerun setup after changes.
- Sessions have no budget restriction. They consume paid API resources.
- `.state/deployment.json`: isolated cloud resource IDs; setup reuses and updates agents.
- `.state/last_session.json`: recover the latest session ID after interruption.
- `--session-id SESSION_ID`: collect an existing completed session without starting a new one.

```powershell
& .\.venv\Scripts\python.exe emergency-handling/run_emergency.py --session-id SESSION_ID
& .\.venv\Scripts\python.exe -m unittest discover -s emergency-handling -p test_emergency.py -v
```

Outputs include HTML, coordinator transcript, specialist findings, event history,
workflow audit, input snapshot and session usage metadata. Raw household/session
data and deployment IDs are gitignored. The demo HTML and audit are intentionally
visible to git; review them before committing any real household information.
On incomplete output or a workflow error, diagnostics remain and any previous
valid HTML remains unchanged. Research is limited to 500 words and other specialist
replies to 250 words each. Agents are instructed not to create intermediate files
or duplicate reports; only the coordinator returns the final HTML. A run sends
household input to Anthropic and consumes paid API resources. Setup creates
persistent cloud resources; remove those separately in the platform when done.

The runner explicitly announces when all specialists have replied and the
coordinator is composing HTML. The last specialist dispatched is not necessarily
the active bottleneck: in the first compact run, medical finished in about 14
seconds while final coordinator reasoning and HTML generation took about 261
seconds at medium effort. Low effort is now configured to reduce that reasoning
overhead; its end-to-end speed improvement has not yet been measured. Final HTML
arrives as a complete message, so a quiet interval does not imply medical is stuck.

## Assumptions And Limits

- This is a preparedness demo, not an emergency service, clinical service or
  source of real-time evacuation instructions. Fictional facts are prominently labelled.
- US context and 911 are explicit properties of the sample input, not universal defaults.
- No real injuries or acute symptoms are present at input time; the medical agent
  provides warning signs, precautions and escalation, not diagnosis or prescriptions.
- Live browsing is disabled by instructions, not by a network firewall. The
  environment uses the root demo's unrestricted networking pattern; the skill
  replaces live third-party research. Do not run with untrusted input or secrets.
- Zombies are handled only as a fictional, nonviolent preparedness exercise.
- A single combined-incident input demonstrates the complete workflow; background
  guidance covers the other types, but they do not have fabricated local alerts.
- No new packages are added; the root Anthropic SDK minimum is raised to 2.6.0.