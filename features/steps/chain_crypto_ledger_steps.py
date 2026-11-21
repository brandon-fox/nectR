"""Behave step definitions for chain_crypto_ledger (Phase 1 RED pending)."""

from __future__ import annotations

from behave import given, then, when


@given('an Ed25519 keypair for Bee "{bee_id}" and a canonicalized barter payload')
def step_given_ed25519_keypair(context: object, bee_id: str) -> None:
    raise NotImplementedError("RED: adopt-ed25519-and-pymerkle not yet implemented")


@when("the transaction is committed into a BlockHeader via merklelib")
def step_when_committed_merklelib(context: object) -> None:
    raise NotImplementedError("RED: adopt-ed25519-and-pymerkle not yet implemented")


@then("the Ed25519 signature and Merkle inclusion proof verify deterministically")
def step_then_verify_inclusion(context: object) -> None:
    raise NotImplementedError("RED: adopt-ed25519-and-pymerkle not yet implemented")
