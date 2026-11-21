"""Strict TDD unit and invariant tests for nectr.chain (ADR-0008 / R2)."""

from __future__ import annotations

import hashlib

import pytest


def test_canonical_payload_determinism_and_non_finite_float_rejection() -> None:
    from nectr.chain import BlockHeader, CanonicalPayload, UsefulComputeProof, compute_sha256

    nested_a = {"z": 1, "a": {"d": 4, "b": [True, 2.5, "ok"]}}
    nested_b = {"a": {"b": [True, 2.5, "ok"], "d": 4}, "z": 1}

    assert CanonicalPayload.encode(nested_a) == CanonicalPayload.encode(nested_b)
    assert CanonicalPayload.hash_hex(nested_a) == CanonicalPayload.hash_hex(nested_b)
    cp = CanonicalPayload.from_data(nested_a)
    assert cp.sha256_hex() == CanonicalPayload.hash_hex(nested_b)
    assert cp.sha256_digest() == CanonicalPayload.hash_bytes(nested_a)

    uproof = UsefulComputeProof(
        epoch=1,
        active_bees=4,
        total_directional_edges=3,
        collusion_discounted_velocity=12.5,
        gini_coefficient=0.25,
        graph_state_hash=compute_sha256("graph-1"),
    )
    assert uproof.to_commitment_hash() == CanonicalPayload.hash_hex(uproof)

    header = BlockHeader(
        hive_id="HIVE_TEST",
        height=1,
        prev_hash="0" * 64,
        merkle_root="0" * 64,
        knowledge_graph_root=uproof.to_commitment_hash(),
        difficulty=2,
        nonce=7,
        timestamp=1700000001.0,
    )
    assert header.block_hash() == CanonicalPayload.hash_hex(header)

    for bad_float in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            CanonicalPayload.encode({"bad": bad_float})
        with pytest.raises(ValueError):
            UsefulComputeProof(
                epoch=1,
                active_bees=1,
                total_directional_edges=0,
                collusion_discounted_velocity=bad_float,
                gini_coefficient=0.0,
                graph_state_hash="0" * 64,
            ).to_commitment_hash()
        with pytest.raises(ValueError):
            BlockHeader(
                hive_id="HIVE_TEST",
                height=1,
                prev_hash="0" * 64,
                merkle_root="0" * 64,
                knowledge_graph_root="0" * 64,
                difficulty=2,
                nonce=0,
                timestamp=bad_float,
            ).block_hash()


def test_ed25519_signer_verifier_lifecycle_and_redaction() -> None:
    from nectr.chain import Ed25519Signer, Ed25519Verifier

    seed = b"\x01" * 32
    signer_a = Ed25519Signer.from_seed(seed)
    signer_b = Ed25519Signer.from_seed(seed)
    signer_rand = Ed25519Signer.generate()

    assert signer_a.public_key_bytes == signer_b.public_key_bytes
    assert signer_a.public_key_hex == signer_b.public_key_hex
    assert signer_a.public_key_bytes != signer_rand.public_key_bytes

    # Private seed bytes/hex must never appear in __repr__ or __str__.
    assert seed.hex() not in repr(signer_a)
    assert seed.hex() not in str(signer_a)

    payload = {"action": "BARTER", "amount": 10.0}
    sig_bytes = signer_a.sign(payload)
    sig_hex = signer_a.sign_hex(payload)
    assert sig_bytes == signer_b.sign(payload)
    assert len(sig_bytes) == 64

    verifier = signer_a.verifier
    assert verifier == Ed25519Verifier.from_public_bytes(signer_a.public_key_bytes)
    assert verifier == Ed25519Verifier.from_public_hex(signer_a.public_key_hex)
    assert verifier.verify(payload, sig_bytes) is True
    assert verifier.verify(payload, sig_hex) is True
    assert verifier.verify(b"raw-bytes-msg", signer_a.sign(b"raw-bytes-msg")) is True

    # Tampered payload, wrong key, truncated/corrupted signature return False.
    assert verifier.verify({"action": "BARTER", "amount": 99.0}, sig_bytes) is False
    assert signer_rand.verifier.verify(payload, sig_bytes) is False
    assert verifier.verify(payload, sig_bytes[:-1]) is False
    assert verifier.verify(payload, "not-valid-hex") is False

    # Invalid seeds/keys raise ValueError.
    with pytest.raises(ValueError):
        Ed25519Signer.from_seed(b"short")
    with pytest.raises(ValueError):
        Ed25519Signer.from_private_bytes(b"short")
    with pytest.raises(ValueError):
        Ed25519Verifier.from_public_bytes(b"short")
    with pytest.raises(ValueError):
        Ed25519Verifier.from_public_hex("zzzz")
    with pytest.raises(ValueError):
        Ed25519Verifier.from_public_hex("00" * 16)


def test_signed_transaction_create_verify_and_tamper_rejection() -> None:
    from nectr.chain import Ed25519Signer, SignedTransaction

    signer = Ed25519Signer.from_seed(b"\x03" * 32)
    other_signer = Ed25519Signer.from_seed(b"\x04" * 32)

    tx = SignedTransaction.create(
        {"session_id": "s1", "tutor": "w1", "learner": "l1", "amount": 5.0},
        signer=signer,
        signer_id="w1",
    )
    assert tx.verify_signature() is True
    assert len(tx.canonical_bytes()) > 0

    tampered_payload = tx.model_copy(update={"payload": {**tx.payload, "amount": 500.0}})
    assert tampered_payload.verify_signature() is False

    tampered_sig = tx.model_copy(update={"signature": "00" * 64})
    assert tampered_sig.verify_signature() is False

    swapped_key = tx.model_copy(update={"signer_public_key": other_signer.public_key_hex})
    assert swapped_key.verify_signature() is False

    malformed_key = tx.model_copy(update={"signer_public_key": "bad-hex"})
    assert malformed_key.verify_signature() is False


def test_merkle_inclusion_proof_edges_and_remerkleable_trees() -> None:
    from nectr.chain import (
        Ed25519Signer,
        MerkleInclusionProof,
        SignedTransaction,
        compute_merkle_root,
        compute_sha256,
        compute_tx_leaf_hash,
    )

    assert compute_merkle_root([]) == compute_sha256("EMPTY_BLOCK")
    with pytest.raises(ValueError):
        MerkleInclusionProof.from_transactions([], 0)

    txs_base: list[SignedTransaction | dict[str, object]] = [
        {"idx": i, "amount": float(i + 1)} for i in range(7)
    ]
    txs_base[2] = SignedTransaction.create(
        {"idx": 2, "signed": True},
        signer=Ed25519Signer.from_seed(b"\x05" * 32),
        signer_id="bee_2",
    )

    with pytest.raises(ValueError):
        MerkleInclusionProof.from_transactions(txs_base[:3], -1)
    with pytest.raises(ValueError):
        MerkleInclusionProof.from_transactions(txs_base[:3], 3)

    # 1-leaf tree: depth == 0, forged index=1 must fail verification.
    one_tx = [txs_base[0]]
    one_root = compute_merkle_root(one_tx)
    one_proof = MerkleInclusionProof.from_transactions(one_tx, 0)
    assert len(one_proof.branch) == 0
    assert one_proof.verify(one_root) is True
    assert one_proof.verify_transaction(one_tx[0], one_root) is True
    assert one_proof.model_copy(update={"index": 1}).verify(one_root) is False
    assert one_proof.verify_transaction({"idx": 999}, one_root) is False

    # Domain separation: 0x00-prefixed leaf hash vs unprefixed SHA-256 of canonical tx.
    leaf_digest = compute_tx_leaf_hash(txs_base[0])
    assert len(leaf_digest) == 32
    assert leaf_digest == hashlib.sha256(b"\x00" + b'{"amount":1.0,"idx":0}').digest()

    # Multi-leaf trees (odd and even counts).
    for count in (2, 3, 4, 5, 7):
        subset = txs_base[:count]
        root = compute_merkle_root(subset)
        for idx, tx in enumerate(subset):
            proof = MerkleInclusionProof.from_transactions(subset, idx)
            assert proof.verify(root) is True
            assert proof.verify_transaction(tx, root) is True

    # Tamper & boundary rejection checks on a 5-leaf proof.
    five_subset = txs_base[:5]
    five_root = compute_merkle_root(five_subset)
    proof_5 = MerkleInclusionProof.from_transactions(five_subset, 3)

    assert proof_5.model_copy(update={"leaf_hash": "ff" * 32}).verify(five_root) is False
    tampered_branch = ("00" * 32, *proof_5.branch[1:])
    assert proof_5.model_copy(update={"branch": tampered_branch}).verify(five_root) is False
    assert proof_5.model_copy(update={"index": 2}).verify(five_root) is False
    assert proof_5.verify("ff" * 32) is False
    assert proof_5.model_copy(update={"branch": proof_5.branch[:-1]}).verify(five_root) is False
    assert proof_5.model_copy(update={"leaf_hash": "not-hex"}).verify(five_root) is False
    bad_hex_branch = ("zzzz" * 16, *proof_5.branch[1:])
    assert proof_5.model_copy(update={"branch": bad_hex_branch}).verify(five_root) is False


def test_hive_blockchain_dict_and_signed_tx_and_verify_chain_tamper_branches() -> None:
    from nectr.chain import (
        Ed25519Signer,
        HiveBlockchain,
        SignedTransaction,
        UsefulComputeProof,
        compute_merkle_root,
        compute_sha256,
    )

    def make_proof(epoch: int) -> UsefulComputeProof:
        return UsefulComputeProof(
            epoch=epoch,
            active_bees=5,
            total_directional_edges=epoch * 2,
            collusion_discounted_velocity=20.0 * epoch,
            gini_coefficient=0.15,
            graph_state_hash=compute_sha256(f"graph:{epoch}"),
        )

    def remine_header(header_obj: object, difficulty: int) -> object:
        nonce = 0
        prefix = "0" * difficulty
        while True:
            candidate = header_obj.model_copy(update={"nonce": nonce, "difficulty": difficulty})  # type: ignore[attr-defined]
            if candidate.block_hash().startswith(prefix):
                return candidate
            nonce += 1

    proposer = Ed25519Signer.from_seed(b"\x07" * 32)
    tx_signer = Ed25519Signer.from_seed(b"\x08" * 32)

    chain = HiveBlockchain(hive_id="HIVE_CHAIN_TEST", difficulty=2)
    assert chain.verify_chain() is True

    # Empty block mining still verifies.
    chain.mine_block(useful_compute_proof=make_proof(1), timestamp=1700000010.0)
    assert chain.verify_chain() is True

    # Forged SignedTransaction rejected at submit_transaction without polluting mempool.
    valid_signed = SignedTransaction.create(
        {"type": "SERVICE_BARTER", "session": "s1", "amount": 10.0},
        signer=tx_signer,
        signer_id="tutor_1",
    )
    forged_signed = valid_signed.model_copy(update={"signature": "00" * 64})
    with pytest.raises(ValueError):
        chain.submit_transaction(forged_signed)
    assert chain.mempool == []

    # Mixed backward-compatible dict + SignedTransaction + proposer signature.
    chain.submit_transaction({"type": "SEED_COMB", "amount": 100.0})
    chain.submit_signed_transaction(valid_signed)
    block2 = chain.mine_block(
        useful_compute_proof=make_proof(2),
        timestamp=1700000020.0,
        proposer_signer=proposer,
    )
    assert chain.verify_chain() is True
    proof_0 = chain.get_inclusion_proof(2, 0)
    proof_1 = chain.get_inclusion_proof(2, 1)
    assert proof_0.verify_transaction(block2.transactions[0], block2.header.merkle_root) is True
    assert proof_1.verify_transaction(valid_signed, block2.header.merkle_root) is True

    # 1. Tampered nonce / broken PoW
    orig_b2 = chain.chain[2]
    bad_nonce = orig_b2.header.nonce + 1
    while orig_b2.header.model_copy(update={"nonce": bad_nonce}).block_hash().startswith("00"):
        bad_nonce += 1
    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"nonce": bad_nonce})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 2. Lowered difficulty even if block hash still starts with fewer zeros
    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"difficulty": 1})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 3. Tampered header merkle_root
    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"merkle_root": "ff" * 32})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 4. Tampered dict transaction inside block
    tampered_dict_txs = [{"type": "SEED_COMB", "amount": 9999.0}, orig_b2.transactions[1]]
    chain.chain[2] = orig_b2.model_copy(update={"transactions": tampered_dict_txs})
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 5. Invalid SignedTransaction signature even after recomputing merkle_root and re-mining PoW
    forged_in_block = [orig_b2.transactions[0], forged_signed]
    recomputed_root = compute_merkle_root(forged_in_block)
    remined_header = remine_header(
        orig_b2.header.model_copy(update={"merkle_root": recomputed_root}),
        difficulty=2,
    )
    chain.chain[2] = orig_b2.model_copy(
        update={
            "header": remined_header,
            "transactions": forged_in_block,
            "inclusion_proofs": [],
            "proposer_public_key": None,
            "proposer_signature": None,
        }
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 6. Tampered inclusion proof
    tampered_proofs = [
        orig_b2.inclusion_proofs[0].model_copy(update={"leaf_hash": "aa" * 32}),
        orig_b2.inclusion_proofs[1],
    ]
    chain.chain[2] = orig_b2.model_copy(update={"inclusion_proofs": tampered_proofs})
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 7. Tampered useful_compute_proof / knowledge_graph_root
    chain.chain[2] = orig_b2.model_copy(update={"useful_compute_proof": make_proof(99)})
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 8. Broken prev_hash
    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"prev_hash": "ab" * 32})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 9. Tampered hive_id / height
    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"hive_id": "EVIL_HIVE"})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    chain.chain[2] = orig_b2.model_copy(
        update={"header": orig_b2.header.model_copy(update={"height": 99})}
    )
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    # 10. Tampered proposer_signature or missing proposer_public_key
    chain.chain[2] = orig_b2.model_copy(update={"proposer_signature": "00" * 64})
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2.model_copy(update={"proposer_public_key": None})
    assert chain.verify_chain() is False
    chain.chain[2] = orig_b2

    assert chain.verify_chain() is True


def test_chain_additional_edge_cases_and_json_roundtrip() -> None:
    from nectr.chain import (
        Block,
        CanonicalPayload,
        Ed25519Signer,
        HiveBlockchain,
        SignedTransaction,
        UsefulComputeProof,
        compute_sha256,
    )

    with pytest.raises(ValueError):
        HiveBlockchain(hive_id="BAD_DIFF", difficulty=-1)

    with pytest.raises(TypeError):
        CanonicalPayload.encode(["not", "a", "mapping"])  # type: ignore[arg-type]

    proposer = Ed25519Signer.from_seed(b"\x09" * 32)
    chain = HiveBlockchain(hive_id="HIVE_ROUNDTRIP", difficulty=1)
    tx = SignedTransaction.create({"k": "v"}, signer=proposer, signer_id="bee_rt")
    chain.submit_signed_transaction(tx)
    proof = UsefulComputeProof(
        epoch=1,
        active_bees=1,
        total_directional_edges=1,
        collusion_discounted_velocity=1.0,
        gini_coefficient=0.0,
        graph_state_hash=compute_sha256("rt"),
    )
    block = chain.mine_block(useful_compute_proof=proof, proposer_signer=proposer)

    # Pydantic JSON roundtrip preserves SignedTransaction inside Block.transactions.
    rehydrated = Block.model_validate_json(block.model_dump_json())
    assert isinstance(rehydrated.transactions[0], SignedTransaction)
    assert rehydrated.transactions[0].verify_signature() is True

    with pytest.raises(IndexError):
        chain.get_inclusion_proof(99, 0)

    # Inclusion proof length mismatch & empty-block with non-empty proofs & bad proposer key hex.
    orig_b1 = chain.chain[1]
    chain.chain[1] = orig_b1.model_copy(update={"inclusion_proofs": []})
    assert chain.verify_chain() is True  # merkle_root still checked
    assert isinstance(chain.get_inclusion_proof(1, 0).branch, tuple)
    chain.chain[1] = orig_b1.model_copy(
        update={"inclusion_proofs": [orig_b1.inclusion_proofs[0]] * 2}
    )
    assert chain.verify_chain() is False
    chain.chain[1] = orig_b1.model_copy(update={"proposer_public_key": "not-hex"})
    assert chain.verify_chain() is False
    chain.chain[1] = orig_b1

    # Genesis block with corrupted prev_hash or spurious inclusion proof fails.
    orig_b0 = chain.chain[0]
    chain.chain[0] = orig_b0.model_copy(
        update={"header": orig_b0.header.model_copy(update={"prev_hash": "11" * 32})}
    )
    assert chain.verify_chain() is False
    chain.chain[0] = orig_b0.model_copy(update={"inclusion_proofs": [orig_b1.inclusion_proofs[0]]})
    assert chain.verify_chain() is False
    chain.chain[0] = orig_b0

    empty_chain = HiveBlockchain(hive_id="HIVE_EMPTY", difficulty=1)
    empty_chain.chain.clear()
    assert empty_chain.verify_chain() is False


def test_verification_paths_reject_nan_inf_bytes_without_crashing() -> None:
    import json

    from pydantic import ValidationError

    from nectr.chain import (
        Block,
        CanonicalPayload,
        Ed25519Signer,
        HiveBlockchain,
        SignedTransaction,
        UsefulComputeProof,
        compute_sha256,
    )

    signer = Ed25519Signer.from_seed(b"\x12" * 32)
    valid_tx = SignedTransaction.create({"k": "v"}, signer=signer, signer_id="bee_1")

    with pytest.raises(ValidationError):
        SignedTransaction(
            payload={"x": float("nan")},
            signer_public_key=signer.public_key_hex,
            signature=valid_tx.signature,
        )
    with pytest.raises(ValidationError):
        SignedTransaction(
            payload={"x": float("inf")},
            signer_public_key=signer.public_key_hex,
            signature=valid_tx.signature,
        )
    with pytest.raises(ValidationError):
        SignedTransaction(
            payload={"x": b"raw-bytes"},
            signer_public_key=signer.public_key_hex,
            signature=valid_tx.signature,
        )

    stx_nan = valid_tx.model_copy(update={"payload": {"x": float("nan")}})
    assert stx_nan.verify_signature() is False
    with pytest.raises(ValueError):
        CanonicalPayload.encode(stx_nan)

    stx_bytes = valid_tx.model_copy(update={"payload": {"x": b"raw-bytes"}})
    assert stx_bytes.verify_signature() is False

    assert signer.verifier.verify({"x": float("nan")}, valid_tx.signature) is False
    assert signer.verifier.verify({"x": b"raw-bytes"}, valid_tx.signature) is False

    chain = HiveBlockchain(hive_id="HIVE_NAN", difficulty=1)
    chain.submit_transaction({"type": "DICT_TX", "val": 1.0})
    block = chain.mine_block(
        useful_compute_proof=UsefulComputeProof(
            epoch=1,
            active_bees=1,
            total_directional_edges=0,
            collusion_discounted_velocity=0.0,
            gini_coefficient=0.0,
            graph_state_hash=compute_sha256("nan-test"),
        ),
        timestamp=1700000050.0,
    )
    nan_block_dict = block.model_dump()
    nan_block_dict["transactions"][0]["val"] = float("nan")
    nan_block = Block.model_validate_json(json.dumps(nan_block_dict, allow_nan=True))
    chain.chain[1] = nan_block
    assert chain.verify_chain() is False

    # Non-finite float injected into header or UsefulComputeProof also returns False cleanly.
    chain.chain[1] = block.model_copy(
        update={"header": block.header.model_copy(update={"timestamp": float("nan")})}
    )
    assert chain.verify_chain() is False
    chain.chain[1] = block.model_copy(
        update={
            "useful_compute_proof": block.useful_compute_proof.model_copy(
                update={"gini_coefficient": float("inf")}
            )
        }
    )
    assert chain.verify_chain() is False


def test_merkle_proof_binds_leaf_count_and_rejects_zero_slot_forgery() -> None:
    from nectr.chain import MerkleInclusionProof, compute_merkle_root

    txs_3 = [{"i": 0}, {"i": 1}, {"i": 2}]
    root_3 = compute_merkle_root(txs_3)
    p3_0 = MerkleInclusionProof.from_transactions(txs_3, 0)
    p3_2 = MerkleInclusionProof.from_transactions(txs_3, 2)

    forged_zero_slot = MerkleInclusionProof(
        leaf_hash="00" * 32,
        index=3,
        branch=(p3_2.leaf_hash, p3_2.branch[1]),
        merkle_root=root_3,
        leaf_count=4,
    )
    assert forged_zero_slot.verify(root_3) is False
    assert p3_0.model_copy(update={"leaf_count": 4}).verify(root_3) is False

    txs_5 = [{"i": i} for i in range(5)]
    root_5 = compute_merkle_root(txs_5)
    p5_4 = MerkleInclusionProof.from_transactions(txs_5, 4)
    assert p5_4.model_copy(update={"leaf_count": 8}).verify(root_5) is False

    # 1-leaf depth == 0 continues to verify while rejecting zero-slot leaf_hash.
    one_root = compute_merkle_root([{"i": 0}])
    one_proof = MerkleInclusionProof.from_transactions([{"i": 0}], 0)
    assert len(one_proof.branch) == 0
    assert one_proof.verify(one_root) is True
    assert one_proof.model_copy(update={"leaf_hash": "00" * 32}).verify(one_root) is False


def test_strict_canonical_lowercase_hex_rejects_uppercase_and_whitespace() -> None:
    from pydantic import ValidationError

    from nectr.chain import (
        Ed25519Signer,
        Ed25519Verifier,
        HiveBlockchain,
        MerkleInclusionProof,
        SignedTransaction,
        UsefulComputeProof,
        compute_merkle_root,
        compute_sha256,
    )

    signer = Ed25519Signer.from_seed(b"\x13" * 32)
    pk = signer.public_key_hex
    ws_pk = " ".join(pk[i : i + 2] for i in range(0, len(pk), 2))
    payload = {"action": "HEX_TEST", "amount": 1.0}
    valid_stx = SignedTransaction.create(payload, signer=signer, signer_id="bee_hex")
    sig = valid_stx.signature
    ws_sig = " ".join(sig[i : i + 2] for i in range(0, len(sig), 2))

    for bad_pk in (pk.upper(), ws_pk, f"{pk}\n"):
        with pytest.raises(ValueError):
            Ed25519Verifier.from_public_hex(bad_pk)
        with pytest.raises(ValidationError):
            SignedTransaction(payload=payload, signer_public_key=bad_pk, signature=sig)

    for bad_sig in (sig.upper(), ws_sig, f"{sig}\n"):
        assert signer.verifier.verify(payload, bad_sig) is False
        with pytest.raises(ValidationError):
            SignedTransaction(payload=payload, signer_public_key=pk, signature=bad_sig)

    stx_upper = valid_stx.model_copy(update={"signature": sig.upper()})
    stx_ws = valid_stx.model_copy(update={"signature": ws_sig})
    stx_upper_pk = valid_stx.model_copy(update={"signer_public_key": pk.upper()})
    assert stx_upper.verify_signature() is False
    assert stx_ws.verify_signature() is False
    assert stx_upper_pk.verify_signature() is False

    chain = HiveBlockchain(hive_id="HIVE_HEX", difficulty=1)
    with pytest.raises(ValueError):
        chain.submit_transaction(stx_upper)
    with pytest.raises(ValueError):
        chain.submit_transaction(stx_ws)

    # Even if forced into a mined block, verify_chain rejects non-canonical hex variants.
    chain.mempool.append(stx_upper)
    chain.mine_block(
        useful_compute_proof=UsefulComputeProof(
            epoch=1,
            active_bees=1,
            total_directional_edges=1,
            collusion_discounted_velocity=1.0,
            gini_coefficient=0.0,
            graph_state_hash=compute_sha256("hex"),
        )
    )
    assert chain.verify_chain() is False

    txs = [{"a": 1}, {"a": 2}]
    root = compute_merkle_root(txs)
    proof = MerkleInclusionProof.from_transactions(txs, 0)
    ws_leaf = " ".join(proof.leaf_hash[i : i + 2] for i in range(0, len(proof.leaf_hash), 2))
    with pytest.raises(ValidationError):
        MerkleInclusionProof(
            leaf_hash=proof.leaf_hash.upper(),
            index=0,
            branch=proof.branch,
            merkle_root=root,
            leaf_count=2,
        )
    with pytest.raises(ValidationError):
        MerkleInclusionProof(
            leaf_hash=proof.leaf_hash,
            index=0,
            branch=(proof.branch[0].upper(),),
            merkle_root=root,
            leaf_count=2,
        )
    with pytest.raises(ValidationError):
        MerkleInclusionProof(
            leaf_hash=proof.leaf_hash,
            index=0,
            branch=proof.branch,
            merkle_root=root.upper(),
            leaf_count=2,
        )
    assert proof.model_copy(update={"leaf_hash": ws_leaf}).verify(root) is False
    assert proof.model_copy(update={"branch": (proof.branch[0].upper(),)}).verify(root) is False


def test_recursive_normalize_payload_for_nested_basemodel_in_mapping_and_sequence() -> None:
    from pydantic import BaseModel

    from nectr.chain import CanonicalPayload

    class Inner(BaseModel):
        b: int
        a: str

    class Outer(BaseModel):
        inner: Inner
        items: list[Inner]

    model_instance = Outer(inner=Inner(b=2, a="x"), items=[Inner(b=1, a="y")])
    mapping_with_models = {"items": (Inner(b=1, a="y"),), "inner": Inner(b=2, a="x")}
    plain_mapping = {"inner": {"a": "x", "b": 2}, "items": [{"a": "y", "b": 1}]}

    encoded_model = CanonicalPayload.encode(model_instance)
    assert CanonicalPayload.encode(mapping_with_models) == encoded_model
    assert CanonicalPayload.encode(plain_mapping) == encoded_model

    with pytest.raises(TypeError):
        CanonicalPayload.encode({"nested": {"raw": b"bytes"}})
    with pytest.raises(ValueError):
        CanonicalPayload.encode({"nested": [{"bad": float("nan")}]})


def test_verify_chain_rejects_duplicate_transaction_proof_swapping() -> None:
    from nectr.chain import (
        Ed25519Signer,
        HiveBlockchain,
        SignedTransaction,
        UsefulComputeProof,
        compute_sha256,
    )

    signer = Ed25519Signer.from_seed(b"\x14" * 32)
    tx = SignedTransaction.create({"dup": True, "amt": 3.0}, signer=signer, signer_id="bee_dup")
    chain = HiveBlockchain(hive_id="HIVE_DUP", difficulty=1)
    chain.submit_signed_transaction(tx)
    chain.submit_signed_transaction(tx)
    block = chain.mine_block(
        useful_compute_proof=UsefulComputeProof(
            epoch=1,
            active_bees=2,
            total_directional_edges=2,
            collusion_discounted_velocity=3.0,
            gini_coefficient=0.0,
            graph_state_hash=compute_sha256("dup"),
        ),
        timestamp=1700000060.0,
    )
    assert chain.verify_chain() is True

    # Duplicating proof_0 across both identical transactions must be rejected.
    swapped_proofs = [block.inclusion_proofs[0], block.inclusion_proofs[0]]
    chain.chain[1] = block.model_copy(update={"inclusion_proofs": swapped_proofs})
    assert chain.verify_chain() is False

    # Reversing [proof_1, proof_0] must also be rejected.
    reversed_proofs = [block.inclusion_proofs[1], block.inclusion_proofs[0]]
    chain.chain[1] = block.model_copy(update={"inclusion_proofs": reversed_proofs})
    assert chain.verify_chain() is False
