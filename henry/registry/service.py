from henry.contracts.capability import CapabilityContract


class CapabilityNotFoundError(LookupError):
    pass


class InMemoryCapabilityRegistry:
    def __init__(self, capabilities: list[CapabilityContract] | None = None) -> None:
        self._capabilities = {capability.ref: capability for capability in capabilities or []}

    def publish(self, capability: CapabilityContract) -> None:
        self._capabilities[capability.ref] = capability

    def resolve(self, capability_ref: str) -> CapabilityContract:
        try:
            return self._capabilities[capability_ref]
        except KeyError as exc:
            raise CapabilityNotFoundError(capability_ref) from exc

    def discover(
        self,
        entitlements: frozenset[str],
        purpose: str,
    ) -> list[CapabilityContract]:
        return [
            capability
            for capability in self._capabilities.values()
            if capability.required_entitlements.issubset(entitlements)
            and (not capability.allowed_purposes or purpose in capability.allowed_purposes)
        ]
