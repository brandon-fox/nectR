"""Cryptographic primitives, Hybrid PoUW-PoW block mining, and ledger verification for nectR."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


def compute_sha256(payload: str) -> str:
    """Compute a deterministic SHA-256 hex digest."""
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_merkle_root(transactions: list[dict[str, Any]]) -> str:
    """Compute a deterministic Merkle tree root over an ordered list of transactions."""
    if not transactions:
        return compute_sha256("EMPTY_BLOCK")
    layer = [
        compute_sha256(json.dumps(tx, sort_keys=True, separators=(",", ":")))
        for tx in transactions
    ]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [
            compute_sha256(layer[i] + layer[i + 1])
            for i in range(0, len(layer), 2)
        ]
    return layer[0]


@dataclass(frozen=True)
class UsefulComputeProof:
    """Proof-of-Useful-Work (PoUW) committing the trailing epoch's Knowledge Graph & Collusion Matrix."""

    epoch: int
    active_bees: int
    total_directional_edges: int
    collusion_discounted_velocity: float
    gini_coefficient: float
    graph_state_hash: str

    def to_commitment_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return compute_sha256(payload)


@dataclass(frozen=True)
class BlockHeader:
    """Block header committing both cryptographic PoW and Useful Compute (Knowledge Graph root)."""

    hive_id: str
    height: int
    prev_hash: str
    merkle_root: str
    knowledge_graph_root: str
    difficulty: int
    nonce: int
    timestamp: float

    def block_hash(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return compute_sha256(payload)


@dataclass
class Block:
    """Immutable Hive block containing directional service-barter & governance transactions."""

    header: BlockHeader
    useful_compute_proof: UsefulComputeProof
    transactions: list[dict[str, Any]] = field(default_factory=list)

    @property
    def block_hash(self) -> str:
        return self.header.block_hash()


class HiveBlockchain:
    """Private closed-loop PoUW-PoW blockchain for a localized campus Hive."""

    def __init__(self, hive_id: str, difficulty: int = 2) -> None:
        self.hive_id = hive_id
        self.difficulty = difficulty
        self.chain: list[Block] = []
        self.mempool: list[dict[str, Any]] = []
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        genesis_proof = UsefulComputeProof(
            epoch=0,
            active_bees=0,
            total_directional_edges=0,
            collusion_discounted_velocity=0.0,
            gini_coefficient=0.0,
            graph_state_hash=compute_sha256(f"GENESIS_GRAPH:{self.hive_id}"),
        )
        header = self._mine_header(
            height=0,
            prev_hash="0" * 64,
            merkle_root=compute_merkle_root([]),
            knowledge_graph_root=genesis_proof.to_commitment_hash(),
            timestamp=1700000000.0,
        )
        self.chain.append(Block(header=header, useful_compute_proof=genesis_proof, transactions=[]))

    def _mine_header(
        self,
        height: int,
        prev_hash: str,
        merkle_root: str,
        knowledge_graph_root: str,
        timestamp: float | None = None,
    ) -> BlockHeader:
        ts = time.time() if timestamp is None else timestamp
        prefix = "0" * self.difficulty
        nonce = 0
        while True:
            candidate = BlockHeader(
                hive_id=self.hive_id,
                height=height,
                prev_hash=prev_hash,
                merkle_root=merkle_root,
                knowledge_graph_root=knowledge_graph_root,
                difficulty=self.difficulty,
                nonce=nonce,
                timestamp=ts,
            )
            if candidate.block_hash().startswith(prefix):
                return candidate
            nonce += 1

    def submit_transaction(self, tx: dict[str, Any]) -> None:
        """Queue a verified contract transaction into the Hive mempool."""
        self.mempool.append(tx)

    def mine_block(
        self,
        useful_compute_proof: UsefulComputeProof,
        timestamp: float | None = None,
    ) -> Block:
        """Mine a new PoUW-PoW block committing all queued transactions and the Knowledge Graph proof."""
        prev_block = self.chain[-1]
        txs = list(self.mempool)
        self.mempool.clear()

        merkle_root = compute_merkle_root(txs)
        kg_root = useful_compute_proof.to_commitment_hash()
        header = self._mine_header(
            height=len(self.chain),
            prev_hash=prev_block.block_hash,
            merkle_root=merkle_root,
            knowledge_graph_root=kg_root,
            timestamp=timestamp,
        )
        block = Block(
            header=header,
            useful_compute_proof=useful_compute_proof,
            transactions=txs,
        )
        self.chain.append(block)
        return block

    def verify_chain(self) -> bool:
        """Verify cryptographic PoW, hash links, Merkle roots, and PoUW graph commitments."""
        prefix = "0" * self.difficulty
        for idx, block in enumerate(self.chain):
            if not block.block_hash.startswith(prefix):
                return False
            if block.header.merkle_root != compute_merkle_root(block.transactions):
                return False
            if block.header.knowledge_graph_root != block.useful_compute_proof.to_commitment_hash():
                return False
            if idx > 0 and block.header.prev_hash != self.chain[idx - 1].block_hash:
                return False
        return True
