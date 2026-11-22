"""Behave step definitions for chain_crypto_ledger."""

from __future__ import annotations

from typing import Any

from behave import given, then, when


@given('an Ed25519 keypair for Bee "{bee_id}" and a canonicalized barter payload')
def step_given_ed25519_keypair(context: Any, bee_id: str) -> None:
    from nectr.chain import CanonicalPayload, Ed25519Signer, SignedTransaction

    signer = Ed25519Signer.from_seed(b"\x11" * 32)
    payload_a = {
        "session_id": "sess_bdd_1",
        "tutor_id": bee_id,
        "learner_id": "learner_1",
        "subject_id": "CS-101",
        "amount": 10.0,
        "meta": {"epoch": 1, "verified": True},
    }
    payload_b = {
        "meta": {"verified": True, "epoch": 1},
        "amount": 10.0,
        "subject_id": "CS-101",
        "learner_id": "learner_1",
        "tutor_id": bee_id,
        "session_id": "sess_bdd_1",
    }
    assert CanonicalPayload.encode(payload_a) == CanonicalPayload.encode(payload_b)
    context.signer = signer
    context.signed_tx = SignedTransaction.create(payload_a, signer=signer, signer_id=bee_id)
    context.secondary_tx = SignedTransaction.create(
        {"session_id": "sess_bdd_2", "tutor_id": "worker_2", "amount": 5.0},
        signer=Ed25519Signer.from_seed(b"\x22" * 32),
        signer_id="worker_2",
    )


@when("the transaction is committed into a BlockHeader via remerkleable")
def step_when_committed_remerkleable(context: Any) -> None:
    from nectr.chain import HiveBlockchain, UsefulComputeProof, compute_sha256

    blockchain = HiveBlockchain(hive_id="HIVE_BDD", difficulty=2)
    blockchain.submit_signed_transaction(context.signed_tx)
    blockchain.submit_signed_transaction(context.secondary_tx)

    proof = UsefulComputeProof(
        epoch=1,
        active_bees=3,
        total_directional_edges=2,
        collusion_discounted_velocity=15.0,
        gini_coefficient=0.1,
        graph_state_hash=compute_sha256("bdd_graph_state"),
    )
    block = blockchain.mine_block(useful_compute_proof=proof, proposer_signer=context.signer)
    context.blockchain = blockchain
    context.block = block
    context.inclusion_proof = blockchain.get_inclusion_proof(block.header.height, 0)


@then("the Ed25519 signature and Merkle inclusion proof verify deterministically")
def step_then_verify_inclusion(context: Any) -> None:
    from nectr.chain import compute_merkle_root

    assert context.signed_tx.verify_signature() is True
    assert context.blockchain.verify_chain() is True
    assert context.block.header.merkle_root == compute_merkle_root(context.block.transactions)
    assert context.inclusion_proof.verify_transaction(
        context.signed_tx,
        expected_root=context.block.header.merkle_root,
    )
