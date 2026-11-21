# Smart Contracts Specification

All 5 smart contracts reside in `src/nectr/contracts/` and execute deterministically on every block:

1. **`TokenStateAndCombContract`**
   - State machine for `RAW_POLLEN` (restricted school seed voucher), `LIQUID_NECTR` (peer-to-peer currency), and `ROYAL_COMB_RESERVE` (Hive treasury).
2. **`DirectionalServiceBarterContract`**
   - 3-phase tutoring state machine: `INTENT_ESCROWED` $\rightarrow$ `SESSION_CO_SIGNED` $\rightarrow$ `SETTLED` (0% fee) or `DISPUTED_TO_QUEEN` (Comb fee).
   - Supports `0-nectR` mutual skill-for-skill time-locked barters.
3. **`QueenGovernanceContract`**
   - Enforces the Queen Separation of Powers (`QUEEN_ROLE` cannot act as `Tutor`).
   - Collects certification, arbitration, and bounty facilitation fees into the Comb and calculates Royal Jelly dividends.
4. **`KnowledgeGraphAndPolicingContract`**
   - Records directional tutoring edges $(u \xrightarrow{\text{subject}} v)$, calculates downstream **Learn-then-Teach** lineage, and enforces Worker Policing pairwise decay.
5. **`GuardBeeCrossHiveBridgeContract`**
   - Tracks visiting Bee contributions toward **Accepted Status** in a host Hive and executes Comb-to-Comb liquidity swaps.
