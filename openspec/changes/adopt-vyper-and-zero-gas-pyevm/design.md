# Design: Vyper `.vy` Smart Contracts & Zero-Gas `py-evm` Orchestration (`adopt-vyper-and-zero-gas-pyevm`)

## 1. Five Modular Vyper (`.vy`) Contracts (`src/nectr/contracts/vyper/`)
1. **`TokenStateAndComb.vy`:** Tracks `raw_pollen`, `liquid_nectr`, and `comb_reserve` in `uint256` `micro_nectr` (`DEC-017`), lazy demurrage (`~200 bps/month` above `safety_cushion` in Weeks 1–13, paused in Weeks 14–15, `DEC-001`), and 3-door Senior graduation sinks (`4000 / 3500 / 2500 bps`, `DEC-004`).
2. **`DirectionalServiceBarter.vy`:** Enforces `duration_minutes >= 25` (`DEC-011`), `0%` P2P settlement fee (`gas_price = 0`), EIP-712 learner/tutor co-signature verification (`ecrecover`), direct on-chain learner attestation scores (`0..10,000 bps`, `DEC-018`), and Waggle `60%` Comb surge co-pay (`DEC-002`).
3. **`QueenGovernance.vy`:** Enforces three-tier `BEEKEEPER`, `QUEEN`, and `CERTIFIED_WORKER_BEE` RBAC (`ADR-0003`), cryptographically blocking `QUEEN` addresses from tutoring (`D-02`) and routing `100%` of certification/dispute fees to `TokenStateAndComb.vy` (`D-03`).
4. **`KnowledgeGraphAndPolicing.vy`:** Computes deterministic integer pairwise decay `10_000 * 10_000 / (10_000 + alpha_bps * prior_pair_txs)` (`alpha_bps = 15_000`) and Learn-then-Teach lineage (`gamma_bps = 5_000`, `DEC-003`), emitting typed EVM logs (`SessionSettled`, `AcceptedStatusGranted`) for off-chain CQRS projection (`ADR-0014`).
5. **`GuardBeeCrossHiveBridge.vy`:** Verifies host-Hive `Accepted Status` (`>= K` distinct peers tutored, `D-04`) and executes Comb-to-Comb burn/mint settlement at clamped `[5_000, 20_000] bps` (`[0.5x, 2.0x]`) epoch FX with a `500 bps` (`5%`) source Comb toll (`ADR-0005`).

## 2. Invariants
- **Exact Integer Conservation:** `comb_reserve + sum(raw_pollen) + sum(liquid_nectr) + sum(escrow_locked) == total_minted_supply` holds with `0` wei/micro-unit rounding error.
- **Native `msg.sender` & `PoUW-PoW` Anchoring:** Every state-mutating call is signed by the acting Bee/Queen's `eth-account` (`secp256k1`) keypair (`DEC-019`), and each `PoUW-PoW` block commits `evm_state_root` alongside `knowledge_graph_root`.
