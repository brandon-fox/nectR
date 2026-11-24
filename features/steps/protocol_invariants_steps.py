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


@given(
    'a Hive "{hive_id}" with seed comb {seed_amount:f} and registered Learners "{bee_a}" and "{bee_b}"'
)
def step_given_barter_hive(
    context, hive_id: str, seed_amount: float, bee_a: str, bee_b: str
) -> None:
    context.engine = HiveContractEngine(hive_id=hive_id)
    context.engine.inject_sponsored_seed_comb(seed_amount)
    context.engine.register_bee(bee_a, role=BeeRole.LEARNER_BEE)
    context.engine.register_bee(bee_b, role=BeeRole.LEARNER_BEE)
    context.last_error = None


@given(
    'a source Hive "{hive_a}" and target Hive "{hive_b}" with threshold {threshold:d} '
    'and Pollinator "{pollinator_id}" holding {amount:f} LIQUID_NECTR in "{home_hive}"'
)
def step_given_two_hives_for_bridge(
    context,
    hive_a: str,
    hive_b: str,
    threshold: int,
    pollinator_id: str,
    amount: float,
    home_hive: str,
) -> None:
    context.hive_a = HiveContractEngine(hive_id=hive_a, accepted_status_peer_threshold=threshold)
    context.hive_b = HiveContractEngine(hive_id=hive_b, accepted_status_peer_threshold=threshold)
    context.hive_a.inject_sponsored_seed_comb(500.0 + amount)
    context.hive_b.inject_sponsored_seed_comb(500.0)
    context.hive_a.register_bee("queen_a", role=BeeRole.QUEEN)
    context.hive_a.register_bee("learner_a", role=BeeRole.LEARNER_BEE)
    context.hive_a.register_bee(pollinator_id, role=BeeRole.LEARNER_BEE, home_hive_id=home_hive)
    context.hive_a.certify_worker_bee("queen_a", pollinator_id, "PHYS-201")
    context.hive_a.allocate_raw_pollen_to_learner("queen_a", "learner_a", amount)
    context.hive_a.create_service_barter_escrow(
        session_id="seed_pollinator_liquid",
        tutor_id=pollinator_id,
        learner_id="learner_a",
        subject_id="PHYS-201",
        duration_hours=1.0,
        amount=amount,
        token_state=TokenState.RAW_POLLEN,
    )
    context.hive_a.settle_co_signed_session("seed_pollinator_liquid", 1.0, "seed_hash")
    context.hive_b.register_bee(pollinator_id, home_hive_id=home_hive)
    context.hive_b.register_bee("host_peer_1", role=BeeRole.LEARNER_BEE)
    context.hive_b.register_bee("host_peer_2", role=BeeRole.LEARNER_BEE)
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
    context.engine.dispute_session(session_id="bdd_disputed_sess", caller_id=learner_id)
    context.engine.resolve_disputed_session(
        queen_id=queen_id,
        session_id="bdd_disputed_sess",
        tutor_share_ratio=tutor_share,
        service_fee_rate=fee_rate,
    )


@when(
    '"{learner_id}" attempts a 0.0 LIQUID_NECTR escrow with "{tutor_id}" for "{subject_id}" without a reciprocal subject'
)
def step_when_zero_nectr_without_reciprocal(
    context, learner_id: str, tutor_id: str, subject_id: str
) -> None:
    try:
        context.engine.create_service_barter_escrow(
            session_id="bdd_zero_no_recip",
            tutor_id=tutor_id,
            learner_id=learner_id,
            subject_id=subject_id,
            duration_hours=1.0,
            amount=0.0,
            token_state=TokenState.LIQUID_NECTR,
            reciprocal_subject_id=None,
        )
    except ContractViolationError as exc:
        context.last_error = exc


@when(
    '"{learner_id}" escrows and settles a 0.0 LIQUID_NECTR reciprocal barter with "{tutor_id}" '
    'for "{subject_id}" in exchange for "{reciprocal_subject}"'
)
def step_when_zero_nectr_with_reciprocal(
    context, learner_id: str, tutor_id: str, subject_id: str, reciprocal_subject: str
) -> None:
    context.engine.create_service_barter_escrow(
        session_id="bdd_zero_recip_ok",
        tutor_id=tutor_id,
        learner_id=learner_id,
        subject_id=subject_id,
        duration_hours=1.0,
        amount=0.0,
        token_state=TokenState.LIQUID_NECTR,
        reciprocal_subject_id=reciprocal_subject,
    )
    context.engine.settle_co_signed_session("bdd_zero_recip_ok", 0.95, "recip_hash_ok")


@when(
    '"{pollinator_id}" attempts to bridge {amount:f} LIQUID_NECTR from "{hive_a}" to "{hive_b}" before earning Accepted Status'
)
def step_when_bridge_before_accepted(
    context, pollinator_id: str, amount: float, hive_a: str, hive_b: str
) -> None:
    _ = hive_a, hive_b
    try:
        context.hive_a.bridge_nectr_to_target_hive(
            bee_id=pollinator_id,
            target_hive=context.hive_b,
            amount=amount,
        )
    except ContractViolationError as exc:
        context.last_error = exc


@when(
    '"{pollinator_id}" tutors 2 distinct peers in "{hive_b}" and bridges {amount:f} LIQUID_NECTR from "{hive_a}" to "{target_hive}"'
)
def step_when_tutor_and_bridge(
    context, pollinator_id: str, hive_b: str, amount: float, hive_a: str, target_hive: str
) -> None:
    _ = hive_b, hive_a, target_hive
    for idx, peer_id in enumerate(("host_peer_1", "host_peer_2"), start=1):
        sid = f"bdd_host_tutor_{idx}"
        context.hive_b.create_service_barter_escrow(
            session_id=sid,
            tutor_id=pollinator_id,
            learner_id=peer_id,
            subject_id="PHYS-201",
            duration_hours=1.0,
            amount=0.0,
            reciprocal_subject_id="CHEM-101",
        )
        context.hive_b.settle_co_signed_session(sid, 0.95, f"host_hash_{idx}")
    context.hive_a.bridge_nectr_to_target_hive(
        bee_id=pollinator_id,
        target_hive=context.hive_b,
        amount=amount,
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


@then('"{bee_id}" has tutored {expected_count:d} distinct peer in the Hive')
def step_then_distinct_peers_tutored(context, bee_id: str, expected_count: int) -> None:
    assert len(context.engine.accounts[bee_id].distinct_peers_tutored_in_hive) == expected_count


@then(
    '"{pollinator_id}" has {expected_a:f} LIQUID_NECTR in "{hive_a}" and {expected_b:f} LIQUID_NECTR in "{hive_b}"'
)
def step_then_bridged_balances(
    context,
    pollinator_id: str,
    expected_a: float,
    hive_a: str,
    expected_b: float,
    hive_b: str,
) -> None:
    _ = hive_a, hive_b
    assert context.hive_a.accounts[pollinator_id].liquid_nectr_balance == expected_a
    assert context.hive_b.accounts[pollinator_id].liquid_nectr_balance == expected_b


@when(
    '"{learner_id}" escrows {amount:f} RAW_POLLEN with "{tutor_id}" for "{subject_id}" '
    'and "{queen_id}" attempts to resolve without a dispute at {fee_rate:f} fee rate'
)
def step_when_queen_resolves_undisputed(
    context,
    learner_id: str,
    amount: float,
    tutor_id: str,
    subject_id: str,
    queen_id: str,
    fee_rate: float,
) -> None:
    context.engine.create_service_barter_escrow(
        session_id="bdd_undisputed_sess",
        tutor_id=tutor_id,
        learner_id=learner_id,
        subject_id=subject_id,
        duration_hours=1.0,
        amount=amount,
        token_state=TokenState.RAW_POLLEN,
    )
    try:
        context.engine.resolve_disputed_session(
            queen_id=queen_id,
            session_id="bdd_undisputed_sess",
            tutor_share_ratio=0.5,
            service_fee_rate=fee_rate,
        )
    except ContractViolationError as exc:
        context.last_error = exc


@when(
    '"{learner_id}" escrows {amount:f} RAW_POLLEN with "{tutor_id}" for "{subject_id}" '
    "at epoch {created:d} with expiry {expiry:d} and cancels at epoch {now_epoch:d}"
)
def step_when_learner_cancels_expired_escrow(
    context,
    learner_id: str,
    amount: float,
    tutor_id: str,
    subject_id: str,
    created: int,
    expiry: int,
    now_epoch: int,
) -> None:
    context.engine.create_service_barter_escrow(
        session_id="bdd_expired_sess",
        tutor_id=tutor_id,
        learner_id=learner_id,
        subject_id=subject_id,
        duration_hours=1.0,
        amount=amount,
        token_state=TokenState.RAW_POLLEN,
        created_at_epoch=created,
        expiry_epochs=expiry,
    )
    context.engine.cancel_expired_escrow(
        session_id="bdd_expired_sess",
        learner_id=learner_id,
        current_epoch=now_epoch,
    )
