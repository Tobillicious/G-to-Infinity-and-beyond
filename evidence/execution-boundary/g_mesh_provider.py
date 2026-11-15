"""Offline G-Mesh provider registry / adapter research fixture.

Never performs HTTP, network, tool execution or external output publication.
A caller-supplied MOCK function may return untrusted text in tests. Real
provider integrations require separately enforced ingress/egress capabilities
and certified original-six actual-world obligations, not token filtering.
"""
from dataclasses import dataclass
import hashlib
import json

from g_mesh_protocol import GMeshState


@dataclass(frozen=True)
class ProviderConfig:
    provider_id: str
    provider_type: str
    default_model: str


def offline_request_digest(prompt, config):
    """Domain-separated authorization for one exact offline mock request."""
    if type(prompt) is not str or not isinstance(config, ProviderConfig):
        raise ValueError("invalid offline request")
    body = json.dumps(
        {"provider_id": config.provider_id, "provider_type": config.provider_type,
         "model": config.default_model, "prompt": prompt},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(b"g-mesh-offline-request-v0:" + body).hexdigest()


class GMeshProviderAdapter:
    def __init__(self, handler, config, offline_model):
        if not callable(offline_model):
            raise ValueError("offline injected model callable required")
        self.handler = handler
        self.config = config
        self.offline_model = offline_model

    def invoke_protected_model(self, prompt, handshake_payload, signature,
                               canonical=None):
        """Returns only an untrusted candidate, never a cleared real-world effect.

        A successful handshake authorizes an offline *test inference only*.
        No real provider endpoint can be attached via this interface.
        """
        if self.handler.state != GMeshState.IDLE:
            return False, "FAIL_CLOSED_local_hold"
        if type(prompt) is not str or len(prompt) > 8192:
            return False, "invalid_mock_prompt"
        if (type(handshake_payload) is not dict or
                handshake_payload.get("event_digest") !=
                offline_request_digest(prompt, self.config)):
            return False, "request_digest_mismatch"
        valid, reason = self.handler.process_handshake(
            handshake_payload, signature, canonical)
        if not valid:
            return False, reason
        if self.handler.state != GMeshState.IDLE:
            return False, "FAIL_CLOSED_local_hold"
        try:
            output = self.offline_model(prompt, self.config.default_model)
        except Exception:
            return False, "offline_mock_failed"
        # Recheck hold AFTER inference: a concurrent revocation must prevent
        # returning a candidate, even though this test still has no effects.
        if self.handler.state != GMeshState.IDLE:
            return False, "FAIL_CLOSED_local_hold"
        if type(output) is not str or len(output) > 32768:
            return False, "invalid_mock_output"
        return True, {"candidate": output, "verified_for_effects": False}


class GMeshProviderRegistry:
    def __init__(self, handler):
        self.handler = handler
        self.providers = {}

    def register_provider(self, config, offline_model):
        if not isinstance(config, ProviderConfig):
            raise TypeError("ProviderConfig required")
        if (not config.provider_id or not config.provider_type or
                not config.default_model or config.provider_id in self.providers):
            raise ValueError("invalid or duplicate provider")
        self.providers[config.provider_id] = GMeshProviderAdapter(
            self.handler, config, offline_model)

    def get_provider(self, provider_id):
        if provider_id not in self.providers:
            raise ValueError("unregistered provider")
        return self.providers[provider_id]
