"""Deterministic canonical JSON serialization and Ed25519 cryptographic primitives."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

import canonicaljson
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from pydantic import BaseModel, ConfigDict

PayloadInput = Mapping[str, Any] | BaseModel


def compute_sha256(payload: str | bytes) -> str:
    """Compute a deterministic SHA-256 hex digest over text or raw bytes."""
    raw = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    return hashlib.sha256(raw).hexdigest()


def normalize_payload(data: PayloadInput) -> dict[str, Any]:
    """Normalize a Pydantic BaseModel or Mapping into a JSON-compatible dictionary."""
    if isinstance(data, BaseModel):
        return data.model_dump(mode="json")
    if isinstance(data, Mapping):
        return dict(data)
    raise TypeError("Payload must be a Mapping or Pydantic BaseModel.")


class CanonicalPayload(BaseModel):
    """Immutable canonical JSON representation backed by ``canonicaljson``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_bytes: bytes

    @classmethod
    def from_data(cls, data: PayloadInput) -> CanonicalPayload:
        """Encode a payload into a CanonicalPayload instance."""
        return cls(canonical_bytes=cls.encode(data))

    @staticmethod
    def encode(data: PayloadInput) -> bytes:
        """Serialize a mapping or Pydantic model into deterministic UTF-8 canonical JSON bytes."""
        normalized = normalize_payload(data)
        return bytes(canonicaljson.encode_canonical_json(normalized))

    @staticmethod
    def encode_str(data: PayloadInput) -> str:
        """Serialize a mapping or Pydantic model into deterministic canonical JSON text."""
        return CanonicalPayload.encode(data).decode("utf-8")

    @staticmethod
    def hash_bytes(data: PayloadInput) -> bytes:
        """Return the raw 32-byte SHA-256 digest of the canonicalized payload."""
        return hashlib.sha256(CanonicalPayload.encode(data)).digest()

    @staticmethod
    def hash_hex(data: PayloadInput) -> str:
        """Return the 64-char hex SHA-256 digest of the canonicalized payload."""
        return hashlib.sha256(CanonicalPayload.encode(data)).hexdigest()

    def sha256_digest(self) -> bytes:
        """Return the raw 32-byte SHA-256 digest of the stored canonical bytes."""
        return hashlib.sha256(self.canonical_bytes).digest()

    def sha256_hex(self) -> str:
        """Return the 64-char hex SHA-256 digest of the stored canonical bytes."""
        return hashlib.sha256(self.canonical_bytes).hexdigest()


class Ed25519Verifier:
    """Ed25519 signature verifier wrapping a 32-byte public key."""

    def __init__(self, public_key: Ed25519PublicKey | bytes | str) -> None:
        if isinstance(public_key, Ed25519PublicKey):
            self._public_key = public_key
        elif isinstance(public_key, (bytes, bytearray)):
            raw = bytes(public_key)
            if len(raw) != 32:
                raise ValueError("Ed25519 public key must be exactly 32 bytes.")
            self._public_key = Ed25519PublicKey.from_public_bytes(raw)
        elif isinstance(public_key, str):
            try:
                raw = bytes.fromhex(public_key)
            except ValueError as exc:
                raise ValueError("Ed25519 public key hex string is invalid.") from exc
            if len(raw) != 32:
                raise ValueError("Ed25519 public key must decode to exactly 32 bytes.")
            self._public_key = Ed25519PublicKey.from_public_bytes(raw)
        else:
            raise TypeError("Unsupported Ed25519 public key type.")

    @classmethod
    def from_public_bytes(cls, raw_public_key: bytes) -> Ed25519Verifier:
        """Construct a verifier from raw 32-byte Ed25519 public key material."""
        return cls(raw_public_key)

    @classmethod
    def from_public_hex(cls, hex_public_key: str) -> Ed25519Verifier:
        """Construct a verifier from a 64-char hex-encoded Ed25519 public key."""
        return cls(hex_public_key)

    @property
    def public_key_bytes(self) -> bytes:
        """Return the raw 32-byte Ed25519 public key."""
        return self._public_key.public_bytes_raw()

    @property
    def public_key_hex(self) -> str:
        """Return the hex-encoded Ed25519 public key."""
        return self.public_key_bytes.hex()

    def verify(self, message: bytes | PayloadInput, signature: bytes | str) -> bool:
        """Verify an Ed25519 signature against raw bytes or a canonicalizable payload."""
        msg_bytes = (
            bytes(message)
            if isinstance(message, (bytes, bytearray))
            else CanonicalPayload.encode(message)
        )
        if isinstance(signature, str):
            try:
                sig_bytes = bytes.fromhex(signature)
            except ValueError:
                return False
        elif isinstance(signature, (bytes, bytearray)):
            sig_bytes = bytes(signature)
        else:
            return False

        if len(sig_bytes) != 64:
            return False
        try:
            self._public_key.verify(sig_bytes, msg_bytes)
        except InvalidSignature:
            return False
        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ed25519Verifier):
            return NotImplemented
        return self.public_key_bytes == other.public_key_bytes

    def __repr__(self) -> str:
        return f"Ed25519Verifier(public_key_hex={self.public_key_hex!r})"


class Ed25519Signer:
    """Ed25519 signer holding private key material with redacted string representations."""

    def __init__(self, private_key: Ed25519PrivateKey) -> None:
        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError("private_key must be an Ed25519PrivateKey instance.")
        self._private_key = private_key

    @classmethod
    def generate(cls) -> Ed25519Signer:
        """Generate a fresh random Ed25519 keypair."""
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_seed(cls, seed: bytes) -> Ed25519Signer:
        """Derive a deterministic Ed25519 signer from a 32-byte seed."""
        raw = bytes(seed)
        if len(raw) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes.")
        return cls(Ed25519PrivateKey.from_private_bytes(raw))

    @classmethod
    def from_private_bytes(cls, raw_key: bytes) -> Ed25519Signer:
        """Construct an Ed25519 signer from raw 32-byte private key bytes."""
        raw = bytes(raw_key)
        if len(raw) != 32:
            raise ValueError("Ed25519 private key must be exactly 32 bytes.")
        return cls(Ed25519PrivateKey.from_private_bytes(raw))

    @property
    def public_key_bytes(self) -> bytes:
        """Return the raw 32-byte Ed25519 public key."""
        return self._private_key.public_key().public_bytes_raw()

    @property
    def public_key_hex(self) -> str:
        """Return the hex-encoded Ed25519 public key."""
        return self.public_key_bytes.hex()

    @property
    def verifier(self) -> Ed25519Verifier:
        """Return the public verifier paired with this signer."""
        return Ed25519Verifier(self._private_key.public_key())

    def sign(self, message: bytes | PayloadInput) -> bytes:
        """Sign raw bytes or a canonicalizable payload with Ed25519."""
        msg_bytes = (
            bytes(message)
            if isinstance(message, (bytes, bytearray))
            else CanonicalPayload.encode(message)
        )
        return self._private_key.sign(msg_bytes)

    def sign_hex(self, message: bytes | PayloadInput) -> str:
        """Sign raw bytes or a canonicalizable payload and return a 128-char hex signature."""
        return self.sign(message).hex()

    def __repr__(self) -> str:
        return f"Ed25519Signer(public_key_hex={self.public_key_hex!r}, private_key='[REDACTED]')"

    def __str__(self) -> str:
        return repr(self)


class SignedTransaction(BaseModel):
    """Canonicalized ledger transaction authenticated with an Ed25519 signature."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    payload: dict[str, Any]
    signer_public_key: str
    signature: str
    signer_id: str | None = None

    @classmethod
    def create(
        cls,
        payload: PayloadInput,
        signer: Ed25519Signer,
        signer_id: str | None = None,
    ) -> SignedTransaction:
        """Canonicalize a payload and sign it with the provided Ed25519Signer."""
        normalized = normalize_payload(payload)
        sig_hex = signer.sign_hex(normalized)
        return cls(
            payload=normalized,
            signer_public_key=signer.public_key_hex,
            signature=sig_hex,
            signer_id=signer_id,
        )

    def verify_signature(self) -> bool:
        """Verify the Ed25519 signature over the canonicalized transaction payload."""
        try:
            verifier = Ed25519Verifier.from_public_hex(self.signer_public_key)
        except (ValueError, TypeError):
            return False
        return verifier.verify(self.payload, self.signature)

    def canonical_bytes(self) -> bytes:
        """Return the canonical JSON byte encoding of the full SignedTransaction."""
        return CanonicalPayload.encode(self)
