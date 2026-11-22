"""Cryptographic primitives, Hybrid PoUW-PoW block mining, and ledger verification for nectR."""

from __future__ import annotations

import time

from pydantic import BaseModel, ConfigDict, Field

from nectr.chain.crypto import (
    CanonicalPayload,
    Ed25519Signer,
    Ed25519Verifier,
    SignedTransaction,
    compute_sha256,
)
from nectr.chain.merkle import (
    MerkleInclusionProof,
    TransactionLike,
    compute_merkle_root,
    compute_tx_leaf_hash,
)


class UsefulComputeProof(BaseModel):
    """Proof-of-Useful-Work (PoUW) committing the trailing epoch's Knowledge Graph & Collusion Matrix."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    epoch: int
    active_bees: int
    total_directional_edges: int
    collusion_discounted_velocity: float
    gini_coefficient: float
    graph_state_hash: str

    def to_commitment_hash(self) -> str:
        """Return the canonical SHA-256 hex commitment over this UsefulComputeProof."""
        return CanonicalPayload.hash_hex(self)


class BlockHeader(BaseModel):
    """Block header committing both cryptographic PoW and Useful Compute (Knowledge Graph root)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    hive_id: str
    height: int
    prev_hash: str
    merkle_root: str
    knowledge_graph_root: str
    difficulty: int
    nonce: int
    timestamp: float

    def block_hash(self) -> str:
        """Return the canonical SHA-256 hex digest of this BlockHeader."""
        return CanonicalPayload.hash_hex(self)


class Block(BaseModel):
    """Immutable Hive block containing directional service-barter & governance transactions."""

    model_config = ConfigDict(extra="forbid")

    header: BlockHeader
    useful_compute_proof: UsefulComputeProof
    transactions: list[SignedTransaction] = Field(default_factory=list)
    inclusion_proofs: list[MerkleInclusionProof] = Field(default_factory=list)
    proposer_public_key: str | None = None
    proposer_signature: str | None = None

    @property
    def block_hash(self) -> str:
        return self.header.block_hash()


class HiveBlockchain:
    """Private closed-loop PoUW-PoW blockchain for a localized campus Hive."""

    def __init__(self, hive_id: str, difficulty: int = 2) -> None:
        if difficulty < 0:
            raise ValueError("difficulty must be non-negative.")
        self.hive_id = hive_id
        self.difficulty = difficulty
        self.chain: list[Block] = []
        self.mempool: list[SignedTransaction] = []
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
        self.chain.append(
            Block(
                header=header,
                useful_compute_proof=genesis_proof,
                transactions=[],
                inclusion_proofs=[],
            )
        )

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

    def submit_transaction(self, tx: SignedTransaction) -> None:
        """Queue a verified Ed25519-signed transaction into the Hive mempool."""
        if not isinstance(tx, SignedTransaction):
            raise TypeError(
                "submit_transaction requires a verified SignedTransaction; unsigned dicts are prohibited."
            )
        if not tx.verify_signature():
            raise ValueError("Invalid Ed25519 signature on SignedTransaction.")
        self.mempool.append(tx)

    def submit_signed_transaction(self, tx: SignedTransaction) -> None:
        """Verify and queue an Ed25519-signed transaction into the Hive mempool."""
        self.submit_transaction(tx)

    def mine_block(
        self,
        useful_compute_proof: UsefulComputeProof,
        timestamp: float | None = None,
        proposer_signer: Ed25519Signer | None = None,
    ) -> Block:
        """Mine a new PoUW-PoW block committing queued transactions and the Knowledge Graph proof."""
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
        inclusion_proofs = [MerkleInclusionProof.from_transactions(txs, i) for i in range(len(txs))]
        proposer_public_key: str | None = None
        proposer_signature: str | None = None
        if proposer_signer is not None:
            proposer_public_key = proposer_signer.public_key_hex
            proposer_signature = proposer_signer.sign_hex(header)

        block = Block(
            header=header,
            useful_compute_proof=useful_compute_proof,
            transactions=txs,
            inclusion_proofs=inclusion_proofs,
            proposer_public_key=proposer_public_key,
            proposer_signature=proposer_signature,
        )
        self.chain.append(block)
        return block

    def get_inclusion_proof(self, block_height: int, tx_index: int) -> MerkleInclusionProof:
        """Retrieve or construct the Merkle inclusion proof for ``tx_index`` at ``block_height``."""
        if block_height < 0 or block_height >= len(self.chain):
            raise IndexError(f"Block height {block_height} out of range.")
        block = self.chain[block_height]
        if block.inclusion_proofs and 0 <= tx_index < len(block.inclusion_proofs):
            return block.inclusion_proofs[tx_index]
        return MerkleInclusionProof.from_transactions(block.transactions, tx_index)

    def verify_chain(self) -> bool:
        """Verify PoW, hash links, Merkle roots, inclusion proofs, Ed25519 signatures, and PoUW."""
        if not self.chain:
            return False
        prefix = "0" * self.difficulty
        for idx, block in enumerate(self.chain):
            if block.header.hive_id != self.hive_id or block.header.height != idx:
                return False
            if block.header.difficulty != self.difficulty:
                return False
            try:
                current_block_hash = block.block_hash
                expected_merkle_root = compute_merkle_root(block.transactions)
                expected_kg_root = block.useful_compute_proof.to_commitment_hash()
            except (ValueError, TypeError):
                return False
            if not current_block_hash.startswith(prefix):
                return False
            if block.header.merkle_root != expected_merkle_root:
                return False

            if not block.transactions and block.inclusion_proofs:
                return False
            for tx in block.transactions:
                if not isinstance(tx, SignedTransaction):
                    return False
                try:
                    if not tx.verify_signature():
                        return False
                except (ValueError, TypeError):
                    return False
            if block.inclusion_proofs:
                if len(block.inclusion_proofs) != len(block.transactions):
                    return False
                expected_leaf_count = len(block.transactions)
                for tx_idx, (proof, tx) in enumerate(
                    zip(block.inclusion_proofs, block.transactions, strict=True)
                ):
                    if proof.index != tx_idx or proof.leaf_count != expected_leaf_count:
                        return False
                    try:
                        if not proof.verify_transaction(tx, expected_root=block.header.merkle_root):
                            return False
                    except (ValueError, TypeError):
                        return False

            if block.header.knowledge_graph_root != expected_kg_root:
                return False
            if idx == 0 and block.header.prev_hash != "0" * 64:
                return False
            if idx > 0:
                try:
                    prev_block_hash = self.chain[idx - 1].block_hash
                except (ValueError, TypeError):
                    return False
                if block.header.prev_hash != prev_block_hash:
                    return False

            if block.proposer_public_key is not None or block.proposer_signature is not None:
                if block.proposer_public_key is None or block.proposer_signature is None:
                    return False
                try:
                    verifier = Ed25519Verifier.from_public_hex(block.proposer_public_key)
                    if not verifier.verify(block.header, block.proposer_signature):
                        return False
                except (ValueError, TypeError):
                    return False
        return True


__all__ = [
    "Block",
    "BlockHeader",
    "CanonicalPayload",
    "Ed25519Signer",
    "Ed25519Verifier",
    "HiveBlockchain",
    "MerkleInclusionProof",
    "SignedTransaction",
    "TransactionLike",
    "UsefulComputeProof",
    "compute_merkle_root",
    "compute_sha256",
    "compute_tx_leaf_hash",
]
