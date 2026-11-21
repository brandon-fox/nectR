"""Mutation-hardening tests for PoUW-PoW blockchain, Merkle root, and chain verification."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from nectr.chain import (
    Block,
    BlockHeader,
    HiveBlockchain,
    UsefulComputeProof,
    compute_merkle_root,
    compute_sha256,
)


def _sample_proof(epoch: int = 1) -> UsefulComputeProof:
    return UsefulComputeProof(
        epoch=epoch,
        active_bees=4,
        total_directional_edges=2,
        collusion_discounted_velocity=15.0,
        gini_coefficient=0.25,
        graph_state_hash=compute_sha256(f"graph:{epoch}"),
    )


def test_merkle_root_and_proof_commitments() -> None:
    assert compute_merkle_root([]) == compute_sha256("EMPTY_BLOCK")
    tx1 = {"id": "1", "amount": 5}
    tx2 = {"id": "2", "amount": 7}
    tx3 = {"id": "3", "amount": 9}

    r1 = compute_merkle_root([tx1])
    assert len(r1) == 64
    assert r1 != compute_merkle_root([tx2])

    r_even = compute_merkle_root([tx1, tx2])
    assert r_even != compute_merkle_root([tx2, tx1])

    # Odd count duplicates final leaf hash
    h1 = compute_sha256('{"amount":5,"id":"1"}')
    h2 = compute_sha256('{"amount":7,"id":"2"}')
    h3 = compute_sha256('{"amount":9,"id":"3"}')
    left = compute_sha256(h1 + h2)
    right = compute_sha256(h3 + h3)
    assert compute_merkle_root([tx1, tx2, tx3]) == compute_sha256(left + right)

    proof = _sample_proof()
    with pytest.raises(ValidationError):
        proof.epoch = 2  # type: ignore[misc]


def test_genesis_mining_and_verify_chain_tamper_detection() -> None:
    chain = HiveBlockchain(hive_id="HIVE_CHAIN", difficulty=2)
    assert len(chain.chain) == 1
    genesis = chain.chain[0]
    assert genesis.header.height == 0
    assert genesis.header.prev_hash == "0" * 64
    assert genesis.header.timestamp == 1700000000.0
    assert genesis.header.difficulty == 2
    assert genesis.header.nonce >= 0
    assert genesis.block_hash.startswith("00")
    assert genesis.useful_compute_proof.epoch == 0
    assert genesis.useful_compute_proof.graph_state_hash == compute_sha256(
        "GENESIS_GRAPH:HIVE_CHAIN"
    )

    tx = {"contract": "DirectionalServiceBarterContract", "amount": 10.0}
    chain.submit_transaction(tx)
    assert len(chain.mempool) == 1
    blk = chain.mine_block(_sample_proof(1), timestamp=1700000100.0)
    assert chain.mempool == []
    assert blk.header.height == 1
    assert blk.header.prev_hash == genesis.block_hash
    assert blk.header.timestamp == 1700000100.0
    assert blk.block_hash.startswith("00")
    assert chain.verify_chain() is True

    # 1. Tamper PoW prefix check (bad nonce -> non-matching prefix)
    bad_nonce = next(
        cand
        for cand in (-1, -2, -3, -4)
        if not blk.header.model_copy(update={"nonce": cand}).block_hash().startswith("00")
    )
    bad_pow_hdr = blk.header.model_copy(update={"nonce": bad_nonce})
    chain.chain[1] = Block(
        header=bad_pow_hdr,
        useful_compute_proof=blk.useful_compute_proof,
        transactions=list(blk.transactions),
    )
    assert chain.verify_chain() is False

    # 2. Tamper transactions while preserving valid PoW (Merkle mismatch)
    tampered_txs = [{"contract": "Fake", "amount": 999.0}]
    chain.chain[1] = Block(
        header=blk.header,
        useful_compute_proof=blk.useful_compute_proof,
        transactions=tampered_txs,
    )
    assert chain.verify_chain() is False

    # 3. Tamper UsefulComputeProof while preserving valid PoW & Merkle root (KG root mismatch)
    chain.chain[1] = Block(
        header=blk.header,
        useful_compute_proof=_sample_proof(epoch=99),
        transactions=list(blk.transactions),
    )
    assert chain.verify_chain() is False

    # 4. Tamper prev_hash and re-mine header so PoW/Merkle/KG pass, testing prev_hash link branch
    remined_hdr: BlockHeader = chain._mine_header(
        height=1,
        prev_hash="f" * 64,
        merkle_root=blk.header.merkle_root,
        knowledge_graph_root=blk.header.knowledge_graph_root,
        timestamp=blk.header.timestamp,
    )
    chain.chain[1] = Block(
        header=remined_hdr,
        useful_compute_proof=blk.useful_compute_proof,
        transactions=list(blk.transactions),
    )
    assert chain.verify_chain() is False
