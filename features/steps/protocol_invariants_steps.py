"""Step definitions for Core nectR Protocol Invariants BDD feature."""

from __future__ import annotations

from behave import given, then, when

from nectr.contracts import (
    BeeRole,
    ContractViolationError,
    HiveContractEngine,
    TokenState,
)


@given('a Hive "{hive_id}" with seed comb {seed_amount:f}')
def step_given_hive(context, hive_id: str, seed_amount: float) -> None:
    context.engine = HiveContractEngine(hive_id=hive_id)
    context.engine.inject_sponsored_seed_comb(seed_amount)
    context.last_error = None


@given('a registered Queen "{queen_id}" and Learner "{learner_id}" with {pollen:f} RAW_POLLEN')
def step_given_queen_and_learner(context, queen_id: str, learner_id: str, pollen: float) -> None:
    context.engine.register_bee(queen_id, role=BeeRole.QUEEN)
    context.engine.register_bee(learner_id, role=BeeRole.LEARNER_BEE)
    context.engine.allocate_raw_pollen_to_learner(queen_id, learner_id, pollen)


@given(
    'a registered Queen "{queen_id}", Learner "{learner_id}" with {pollen:f} RAW_POLLEN, '
    'and uncertified peer "{peer_id}"'
)
def step_given_queen_learner_peer(
    context, queen_id: str, learner_id: str, pollen: float, peer_id: str
) -> None:
    context.engine.register_bee(queen_id, role=BeeRole.QUEEN)
    context.engine.register_bee(learner_id, role=BeeRole.LEARNER_BEE)
    context.engine.register_bee(peer_id, role=BeeRole.LEARNER_BEE)
    context.engine.allocate_raw_pollen_to_learner(queen_id, learner_id, pollen)


@given(
    'a registered Queen "{queen_id}", Learner "{learner_id}" with {pollen:f} RAW_POLLEN, '
    'and Certified Worker "{worker_id}" for "{subject_id}"'
)
def step_given_queen_learner_worker(
    context, queen_id: str, learner_id: str, pollen: float, worker_id: str, subject_id: str
) -> None:
    context.engine.register_bee(queen_id, role=BeeRole.QUEEN)
    context.engine.register_bee(learner_id, role=BeeRole.LEARNER_BEE)
    context.engine.register_bee(worker_id, role=BeeRole.LEARNER_BEE)
    context.engine.certify_worker_bee(queen_id, worker_id, subject_id)
    context.engine.allocate_raw_pollen_to_learner(queen_id, learner_id, pollen)


@given(
    'a Hive "{hive_id}" with seed comb {seed_amount:f}, Queen "{queen_id}", '
    'Certified Worker "{worker_id}" for "{subject_id}", and Learner "{learner_id}" with {pollen:f} RAW_POLLEN'
)
def step_given_full_dispute_hive(
    context,
    hive_id: str,
    seed_amount: float,
    queen_id: str,
    worker_id: str,
    subject_id: str,
    learner_id: str,
    pollen: float,
) -> None:
    context.engine = HiveContractEngine(hive_id=hive_id)
    context.engine.inject_sponsored_seed_comb(seed_amount)
    context.engine.register_bee(queen_id, role=BeeRole.QUEEN)
    context.engine.register_bee(worker_id, role=BeeRole.LEARNER_BEE)
    context.engine.register_bee(learner_id, role=BeeRole.LEARNER_BEE)
    context.engine.certify_worker_bee(queen_id, worker_id, subject_id)
    context.engine.allocate_raw_pollen_to_learner(queen_id, learner_id, pollen)
    context.last_error = None


@when(
    '"{tutor_id}" attempts to create a tutoring escrow for "{learner_id}" in "{subject_id}" '
    "for {amount:f} RAW_POLLEN"
)
def step_when_tutor_attempts_escrow(
    context, tutor_id: str, learner_id: str, subject_id: str, amount: float
) -> None:
    try:
        context.engine.create_service_barter_escrow(
            session_id="bdd_illegal_escrow",
            tutor_id=tutor_id,
            learner_id=learner_id,
            subject_id=subject_id,
            duration_hours=1.0,
            amount=amount,
            token_state=TokenState.RAW_POLLEN,
        )
    except ContractViolationError as exc:
        context.last_error = exc


@when(
    '"{learner_id}" attempts to escrow {amount:f} RAW_POLLEN with "{tutor_id}" for "{subject_id}"'
)
def step_when_learner_attempts_escrow(
    context, learner_id: str, amount: float, tutor_id: str, subject_id: str
) -> None:
    try:
        context.engine.create_service_barter_escrow(
            session_id="bdd_bad_pollen",
            tutor_id=tutor_id,
            learner_id=learner_id,
            subject_id=subject_id,
            duration_hours=1.0,
            amount=amount,
            token_state=TokenState.RAW_POLLEN,
        )
    except ContractViolationError as exc:
        context.last_error = exc


@when(
    '"{learner_id}" escrows and settles {amount:f} RAW_POLLEN with "{tutor_id}" for "{subject_id}"'
)
def step_when_escrow_and_settle(
    context, learner_id: str, amount: float, tutor_id: str, subject_id: str
) -> None:
    context.engine.create_service_barter_escrow(
        session_id="bdd_good_pollen",
        tutor_id=tutor_id,
        learner_id=learner_id,
        subject_id=subject_id,
        duration_hours=1.0,
        amount=amount,
        token_state=TokenState.RAW_POLLEN,
    )
    context.engine.settle_co_signed_session("bdd_good_pollen", 1.0, "bdd_hash_ok")


@when(
    '"{learner_id}" escrows {amount:f} RAW_POLLEN with "{tutor_id}" for "{subject_id}" '
    'and "{queen_id}" resolves the dispute at {tutor_share:f} tutor share and {fee_rate:f} fee rate'
)
def step_when_escrow_and_dispute(
    context,
    learner_id: str,
    amount: float,
    tutor_id: str,
    subject_id: str,
    queen_id: str,
    tutor_share: float,
    fee_rate: float,
) -> None:
    context.engine.create_service_barter_escrow(
        session_id="bdd_disputed_sess",
        tutor_id=tutor_id,
        learner_id=learner_id,
        subject_id=subject_id,
        duration_hours=1.0,
        amount=amount,
        token_state=TokenState.RAW_POLLEN,
    )
    context.engine.resolve_disputed_session(
        queen_id=queen_id,
        session_id="bdd_disputed_sess",
        tutor_share_ratio=tutor_share,
        service_fee_rate=fee_rate,
    )


@then('the contract raises a violation matching "{expected_text}"')
def step_then_violation(context, expected_text: str) -> None:
    assert context.last_error is not None, "Expected ContractViolationError, but none was raised"
    assert expected_text in str(context.last_error), (
        f"Expected '{expected_text}' in '{context.last_error}'"
    )


@then('"{bee_id}" still has {expected:f} RAW_POLLEN')
@then('"{bee_id}" has {expected:f} RAW_POLLEN')
def step_then_raw_pollen(context, bee_id: str, expected: float) -> None:
    assert context.engine.accounts[bee_id].raw_pollen_balance == expected


@then('"{bee_id}" has {expected:f} LIQUID_NECTR')
def step_then_liquid_nectr(context, bee_id: str, expected: float) -> None:
    assert context.engine.accounts[bee_id].liquid_nectr_balance == expected


@then("the Hive comb reserve is {expected:f}")
def step_then_comb_reserve(context, expected: float) -> None:
    assert context.engine.comb_reserve == expected
