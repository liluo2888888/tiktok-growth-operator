# RPA And Account-Farming Boundaries

This file records the platform-adjacent topics that are intentionally documented but not implemented inside `tiktok-growth-operator.skill`.

## Documented Only

The following topics may appear in source materials, enterprise sales copy, or operator requests, but they are not implemented here:

- cloud-phone publishing
- Airtest or Appium mobile RPA
- account warm-up or `养号`
- fingerprint spoofing
- anti-detection tuning
- mass engagement automation
- inbox or follower mutation at scale
- risky notification-clearing or account-state mutation loops

## Why They Are Not Implemented

- they require external infrastructure not present in this workspace
- they are not necessary for reproducing the safe operator value of the public platform
- several of them create abuse, spam, or platform-evasion risk

## Safe Replacements In This Package

- publish-prep packs instead of cloud-phone publishing
- live-assist and account-ops-assist packs instead of unsafe auto-reply loops
- creative-production-handoff packs instead of pretending a render farm or agent studio already exists
- parity-audit and validation docs instead of overstating platform capability

## If The User Wants These Surfaces

The correct response is:

1. document the intended workflow
2. define inputs, outputs, and human approval gates
3. keep any future executor outside this package until there is an approved, safe runtime
