# Gate Cross-Hive Bridges with Guard Bee Status and Epoch FX

* Status: accepted
* Deciders: nectR Protocol & Cross-Hive Architecture
* Date: 2026-11-21

## Context and Problem Statement

Unconditional 1:1 cross-Hive transfers let weakly governed Hives drain healthy Combs, while continuous Bancor bonding curves proved overly complex and MEV-prone in real community currencies (Sarafu post-mortem).

## Considered Options

* **Guard Bee `Accepted Status` gate + once-per-epoch Comb-per-active-bee health exchange rate + monthly outflow cap**
* **Continuous per-trade Bancor Augmented Bonding Curve (ABC)**
* **Unconditional 1:1 cross-Hive parity peg**

## Decision Outcome

Chosen option: "Guard Bee `Accepted Status` gate + once-per-epoch Comb-per-active-bee health exchange rate + monthly outflow cap", because requiring visiting Bees to tutor host-Hive peers first mirrors honeybee nectar-laden drifter acceptance, steady epoch rates eliminate student UX confusion and sandwich attacks, and monthly export caps prevent sudden Comb capital flight.

### Consequences

* Good, because healthy Hives are insulated against external Sybil inflation while genuine migrating tutors retain purchasing power.
* Bad, because cross-Hive liquidity is intentionally throttled until local tutoring contribution is verified.
