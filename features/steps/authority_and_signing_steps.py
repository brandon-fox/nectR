"""Behave step definitions for authority_and_signing."""

from __future__ import annotations

import hashlib
from typing import Any

from behave import given, then, when
from fastapi.testclient import TestClient

from nectr.chain import Ed25519Signer, SignedTransaction
from nectr.contracts import BeeRole
from nectr.services import HiveServiceLayer
from nectr.services.api import create_app


def _signer(bee_id: str) -> Ed25519Signer:
    return Ed25519Signer.from_seed(hashlib.sha256(f"bdd:{bee_id}".encode()).digest())


@given('a bootstrapped Hive "{hive_id}" with a bootstrap Queen and key registry')
def step_given_bootstrapped_hive_for_auth(context: Any, hive_id: str) -> None:
    queen_signer = _signer("queen_1")
    worker_signer = _signer("worker_1")
    service = HiveServiceLayer(hive_id=hive_id, difficulty=1)
    boot_tx = SignedTransaction.create(
        {
            "action": "BOOTSTRAP_HIVE",
            "hive_id": hive_id,
            "queen_id": "queen_1",
            "seed_comb_amount": 200.0,
            "queen_public_keys": {"queen_1": queen_signer.public_key_hex},
            "certified_workers": {"worker_1": ["CS-101"]},
            "worker_public_keys": {"worker_1": worker_signer.public_key_hex},
            "nonce": 1,
        },
        signer=queen_signer,
        signer_id="queen_1",
    )
    service.bootstrap_sponsored_hive(boot_tx)
    context.hive_id = hive_id
    context.service = service
    context.client = TestClient(create_app(service))
    context.queen_signer = queen_signer
    context.worker_signer = worker_signer
    context.last_error = None


@given('a bootstrapped Hive "{hive_id}" with a registered Learner "{learner_id}"')
def step_given_bootstrapped_hive_with_learner(context: Any, hive_id: str, learner_id: str) -> None:
    step_given_bootstrapped_hive_for_auth(context, hive_id)
    learner_signer = _signer(learner_id)
    reg_tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": hive_id,
            "bee_id": learner_id,
            "role": BeeRole.LEARNER_BEE.value,
            "nonce": 1,
        },
        signer=learner_signer,
        signer_id=learner_id,
    )
    context.service.register_bee(reg_tx)
    context.learner_id = learner_id
    context.learner_signer = learner_signer


@when('a Bee "{bee_id}" submits a self-signed register command requesting role "{role}"')
def step_when_self_signed_role_escalation(context: Any, bee_id: str, role: str) -> None:
    rogue_signer = _signer(bee_id)
    tx = SignedTransaction.create(
        {
            "action": "REGISTER_BEE",
            "hive_id": context.hive_id,
            "bee_id": bee_id,
            "role": role,
            "nonce": 1,
        },
        signer=rogue_signer,
        signer_id=bee_id,
    )
    context.rogue_bee_id = bee_id
    try:
        context.service.register_bee(tx)
    except Exception as exc:  # noqa: BLE001
        context.last_error = exc
    context.api_response = context.client.post("/bees", json=tx.model_dump(mode="json"))


@then('the command is rejected with an authorization error and "{bee_id}" is not registered')
def step_then_rejected_with_authorization_error(context: Any, bee_id: str) -> None:
    assert isinstance(context.last_error, PermissionError)
    assert context.api_response.status_code == 403
    assert bee_id not in context.service.contracts.accounts
    assert bee_id not in context.service.bee_public_keys


@when("an unsigned dictionary or invalid-signature write is submitted to the API or blockchain")
def step_when_unsigned_write_submitted(context: Any) -> None:
    context.unsigned_api_res = context.client.post(
        "/pollen/allocate",
        json={"queen_id": "queen_1", "learner_id": context.learner_id, "amount": 10.0},
    )
    bad_sig_tx = SignedTransaction(
        payload={
            "action": "ALLOCATE_RAW_POLLEN",
            "hive_id": context.hive_id,
            "queen_id": "queen_1",
            "learner_id": context.learner_id,
            "amount": 10.0,
            "nonce": 2,
        },
        signer_public_key=context.queen_signer.public_key_hex,
        signature="00" * 64,
        signer_id="queen_1",
    )
    context.bad_sig_api_res = context.client.post(
        "/pollen/allocate", json=bad_sig_tx.model_dump(mode="json")
    )
    context.dict_chain_error = None
    try:
        context.service.blockchain.submit_transaction({"action": "UNSIGNED", "amount": 10.0})
    except (TypeError, ValueError) as exc:
        context.dict_chain_error = exc


@then("the API rejects bad signatures with 401 and the blockchain rejects unsigned transactions")
def step_then_unsigned_writes_rejected(context: Any) -> None:
    assert context.unsigned_api_res.status_code == 422
    assert context.bad_sig_api_res.status_code == 401
    assert context.dict_chain_error is not None
    assert context.service.contracts.accounts[context.learner_id].raw_pollen_balance == 0.0


@when(
    "the Queen executes a signed pollen allocation at nonce {nonce:d} "
    "and replays the same signed command"
)
def step_when_queen_allocates_and_replays(context: Any, nonce: int) -> None:
    tx = SignedTransaction.create(
        {
            "action": "ALLOCATE_RAW_POLLEN",
            "hive_id": context.hive_id,
            "queen_id": "queen_1",
            "learner_id": context.learner_id,
            "amount": 15.0,
            "nonce": nonce,
        },
        signer=context.queen_signer,
        signer_id="queen_1",
    )
    context.first_result = context.service.allocate_raw_pollen(tx)
    context.replay_error = None
    try:
        context.service.allocate_raw_pollen(tx)
    except Exception as exc:  # noqa: BLE001
        context.replay_error = exc


@then(
    "the first allocation succeeds and the replayed command is rejected without modifying balances"
)
def step_then_replay_rejected_balances_preserved(context: Any) -> None:
    assert context.first_result["amount"] == 15.0
    assert context.replay_error is not None
    assert context.service.contracts.accounts[context.learner_id].raw_pollen_balance == 15.0
    assert context.service.contracts.comb_reserve == 185.0
