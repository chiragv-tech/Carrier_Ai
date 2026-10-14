from core.auth import hash_password, verify_password

def test_password_hash_verification():
    encoded = hash_password("correct-horse-battery")
    assert encoded != "correct-horse-battery"
    assert verify_password("correct-horse-battery", encoded)
    assert not verify_password("wrong-password", encoded)
