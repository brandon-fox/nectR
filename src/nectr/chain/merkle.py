"""Typed Merkle tree root and inclusion proof adapter backed by ``remerkleable``."""

from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from remerkleable.tree import (  # type: ignore[import-untyped]
    Node,
    Root,
    RootNode,
    get_depth,
    gindex_bit_iter,
    merkle_hash,
    subtree_fill_to_contents,
    to_gindex,
)

from nectr.chain.crypto import CanonicalPayload, SignedTransaction, compute_sha256

TransactionLike = SignedTransaction | Mapping[str, Any]

_HEX_32_RE = re.compile(r"[0-9a-f]{64}")


def _decode_hex_32(value: str) -> bytes | None:
    if not isinstance(value, str) or _HEX_32_RE.fullmatch(value) is None:
        return None
    return bytes.fromhex(value)


def compute_tx_leaf_hash(tx: TransactionLike) -> bytes:
    """Compute a 0x00 domain-separated SHA-256 leaf digest over canonical transaction bytes."""
    canonical = CanonicalPayload.encode(tx)
    return hashlib.sha256(b"\x00" + canonical).digest()


def compute_merkle_root(transactions: Sequence[TransactionLike]) -> str:
    """Compute a deterministic Merkle tree root over an ordered sequence of transactions."""
    if not transactions:
        return compute_sha256("EMPTY_BLOCK")
    leaves: list[Node] = [RootNode(Root(compute_tx_leaf_hash(tx))) for tx in transactions]
    depth = int(get_depth(len(leaves)))
    tree: Node = subtree_fill_to_contents(leaves, depth)
    root_bytes = bytes(
        merkle_hash(tree.merkle_root(), Root(len(transactions).to_bytes(32, "little")))
    )
    return root_bytes.hex()


class MerkleInclusionProof(BaseModel):
    """Immutable Merkle inclusion proof constructed and verified via ``remerkleable``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    leaf_hash: str
    index: int
    branch: tuple[str, ...]
    merkle_root: str
    leaf_count: int

    @field_validator("leaf_hash", "merkle_root")
    @classmethod
    def _validate_hex_32(cls, value: str) -> str:
        if _HEX_32_RE.fullmatch(value) is None:
            raise ValueError("Expected 64 lowercase hexadecimal characters.")
        return value

    @field_validator("branch")
    @classmethod
    def _validate_branch(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            if _HEX_32_RE.fullmatch(item) is None:
                raise ValueError("Each branch hash must be 64 lowercase hexadecimal characters.")
        return value

    @classmethod
    def from_transactions(
        cls,
        transactions: Sequence[TransactionLike],
        index: int,
    ) -> MerkleInclusionProof:
        """Construct an inclusion proof for the transaction at ``index``."""
        leaf_count = len(transactions)
        if leaf_count == 0:
            raise ValueError("Cannot build MerkleInclusionProof for an empty transaction list.")
        if index < 0 or index >= leaf_count:
            raise ValueError(f"Transaction index {index} out of range for {leaf_count} leaves.")

        leaves: list[Node] = [RootNode(Root(compute_tx_leaf_hash(tx))) for tx in transactions]
        depth = int(get_depth(leaf_count))
        tree: Node = subtree_fill_to_contents(leaves, depth)
        root_hex = bytes(
            merkle_hash(tree.merkle_root(), Root(leaf_count.to_bytes(32, "little")))
        ).hex()

        gindex = to_gindex(index, depth)
        directions, bit_depth = gindex_bit_iter(gindex)
        if int(bit_depth) != depth:
            raise ValueError("Unexpected generalized index depth mismatch.")

        current: Node = tree
        top_down_siblings: list[str] = []
        for go_right in directions:
            if go_right:
                top_down_siblings.append(bytes(current.get_left().merkle_root()).hex())
                current = current.get_right()
            else:
                top_down_siblings.append(bytes(current.get_right().merkle_root()).hex())
                current = current.get_left()

        leaf_hex = bytes(current.merkle_root()).hex()
        return cls(
            leaf_hash=leaf_hex,
            index=index,
            branch=tuple(reversed(top_down_siblings)),
            merkle_root=root_hex,
            leaf_count=leaf_count,
        )

    def verify(self, expected_root: str | None = None) -> bool:
        """Verify this Merkle inclusion proof against ``expected_root`` (or ``self.merkle_root``)."""
        if self.leaf_count < 1 or self.index < 0 or self.index >= self.leaf_count:
            return False
        if self.leaf_hash == "00" * 32:
            return False

        expected_depth = int(get_depth(self.leaf_count))
        if len(self.branch) != expected_depth:
            return False
        if self.index >= (1 << expected_depth):
            return False

        leaf_bytes = _decode_hex_32(self.leaf_hash)
        self_root_bytes = _decode_hex_32(self.merkle_root)
        target_root_hex = self.merkle_root if expected_root is None else expected_root
        target_root_bytes = _decode_hex_32(target_root_hex)
        if leaf_bytes is None or self_root_bytes is None or target_root_bytes is None:
            return False
        if not hmac.compare_digest(self_root_bytes, target_root_bytes):
            return False

        current_root = Root(leaf_bytes)
        idx = self.index
        for sibling_hex in self.branch:
            sibling_bytes = _decode_hex_32(sibling_hex)
            if sibling_bytes is None:
                return False
            sibling_root = Root(sibling_bytes)
            if idx % 2 == 1:
                current_root = merkle_hash(sibling_root, current_root)
            else:
                current_root = merkle_hash(current_root, sibling_root)
            idx //= 2

        if idx != 0:
            return False

        computed_bytes = bytes(
            merkle_hash(current_root, Root(self.leaf_count.to_bytes(32, "little")))
        )
        return hmac.compare_digest(computed_bytes, target_root_bytes)

    def verify_transaction(
        self,
        tx: TransactionLike,
        expected_root: str | None = None,
    ) -> bool:
        """Verify that ``tx`` hashes to ``self.leaf_hash`` and passes Merkle inclusion."""
        try:
            tx_leaf = compute_tx_leaf_hash(tx)
        except (ValueError, TypeError):
            return False
        leaf_bytes = _decode_hex_32(self.leaf_hash)
        if leaf_bytes is None or not hmac.compare_digest(tx_leaf, leaf_bytes):
            return False
        return self.verify(expected_root=expected_root)
