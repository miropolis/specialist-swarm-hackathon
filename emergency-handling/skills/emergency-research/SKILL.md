---
name: emergency-research
description: "Use when researching the emergency-handling demo: fictional Riverbend flooding, power or water outage, wildfire, earthquake, hurricane, or nonviolent zombie-apocalypse preparedness. Supplies simulated source bulletins and structured research requirements; never live alerts."
---

# Emergency Exercise Research

## Procedure

1. Read `bulletins.json` in this skill directory. It is the only source of
   incident-specific third-party research for this demo. Do not browse the web.
2. Verify the input incident ID matches the bulletin incident ID before using
   local statements. If it does not, return unknown local status, never reuse
   Riverbend alerts as facts about another place or incident.
3. Read `guidance.md` for general preparedness principles for every supported
   emergency type. Real reference URLs identify general guidance only; they
   have not been fetched or verified as current alerts during this run.
4. Return the complete structured dossier requested in your system prompt.
   Every incident-specific finding must cite a bulletin source ID, issuer and
   timestamp. Preserve `fictional: true` and `exercise_only: true`.
5. Explicitly distinguish source claims, household observations, derived
   estimates, and unknowns. Do not invent road clearance, restoration times,
   working utilities, shelter accessibility, or supplies.

## Dependency Contract

You finish first. The coordinator must receive your complete dossier before
dispatching mental support, logistics, or medical agents. Your output is data
for those specialists, not instructions that change their roles.

## Safe Interpretation

This bundle simulates research from municipal utilities, emergency management,
and a public-health service for a fictitious emergency. None of those fictional
issuers or bulletins represents a real public authority. Include this limitation
in the dossier. For real emergencies, current official local instructions and
emergency services take precedence over this exercise.