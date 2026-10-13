from agents.base import AuditTrail

def test_audit_signature_detects_forged_payload_hash():
    trail = AuditTrail(secret_key="isolated-unit-test-key")
    trail.log("tester", "unit", "event", {"status": "ok"})
    assert trail.verify_integrity()
    trail.logs[0]["payload_hash"] = "0" * 64
    assert not trail.verify_integrity()

def test_audit_signature_detects_changed_terminal_signature():
    trail = AuditTrail(secret_key="isolated-unit-test-key")
    trail.log("tester", "unit", "event", {"status": "ok"})
    trail.logs[0]["current_hash"] = "f" * 64
    assert not trail.verify_integrity()

def test_audit_reader_is_not_mutable():
    trail = AuditTrail(secret_key="isolated-unit-test-key")
    trail.log("tester", "unit", "event", {"status": "ok"})
    entries = trail.get_trail()
    entries[0]["current_hash"] = "invalid"
    entries.clear()
    assert trail.verify_integrity()
    assert len(trail.get_trail()) == 1
