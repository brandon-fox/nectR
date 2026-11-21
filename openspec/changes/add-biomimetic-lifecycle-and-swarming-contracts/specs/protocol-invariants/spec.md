# Specification Delta: Biomimetic Lifecycle, Demurrage, Waggle/Tremble & Reproductive Swarming (`protocol-invariants`)

## Linked Behavior & Executable Steps
- **Feature File:** [features/protocol_invariants.feature](../../../../../features/protocol_invariants.feature)
- **Step Definitions:** [features/steps/protocol_invariants_steps.py](../../../../../features/steps/protocol_invariants_steps.py)

## Requirements

### Requirement: ADDED — Lazy Demurrage Above Student Safety Cushion & Finals Pause (D-06 / DEC-001)
`TokenStateAndCombContract` SHALL apply lazy epoch demurrage (`~2%/month` default) exclusively to idle `LIQUID_NECTR` balances exceeding a protected student safety cushion during Weeks 1–13, pause demurrage during Finals (Weeks 14–15), and route 100% of decayed units to `comb_reserve` while conserving total Hive supply.
- **Linked Scenario:** `Queen dispute resolution routes 100% of fees to Comb and conserves supply` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L26-L31)

### Requirement: ADDED — Waggle 60% Comb Surge Co-Pay, Tremble Latency Ramp & Stop-Signals (DEC-002 / DEC-013)
`DirectionalServiceBarterContract` and `TokenStateAndCombContract` SHALL support counter-cyclical Midterm/Finals Waggle surge bounties (where the Comb co-pays `60%` of `2.2x` peak tutor payouts), linear Tremble fee reallocation as validation latency rises from `20s` to `80s`, and cross-inhibitory Stop-Signals.
- **Linked Scenario:** `RAW_POLLEN refines into LIQUID_NECTR when settled with a Certified Worker Bee` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L19-L24)

### Requirement: ADDED — Reproductive Swarming Bivouac Escrow, 15-Scout Quorum & 3-Door Senior Sinks (D-08 / DEC-004 / DEC-012)
`QueenGovernanceContract` and `TokenStateAndCombContract` SHALL clear Senior graduation surpluses across the 3-door off-ramp (`40%` Credentials/Swarming, `35%` Campus Perks, `25%` Freshman Pay-It-Forward + dormant alumni Comb sweeps) and SHALL gate daughter-Hive reproductive swarming on `>= 90%` Comb congestion, QMP attenuation, tutor surplus, a `15-scout` (`30%`) quorum with a `1-hour` piping timelock, and a `6.25x–8.0x` Honey-to-Wax infrastructure burn.
- **Linked Scenario:** `Guard Bee blocks unaccepted Pollinator bridge and permits Accepted Status bridge with Comb toll` in [protocol_invariants.feature](../../../../../features/protocol_invariants.feature#L42-L51)
