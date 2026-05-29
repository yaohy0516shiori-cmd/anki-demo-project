# test redis email code service
# store code key in redis, code value is a dictionary with code, expires_at
# TTL 
# test generate_code, verify_code, __cleanup_expired
# register will not conflict with password reset.

import pytest

from backend.app.email_code_service import RedisEmailCodeService


def make_service(redis_client):
    return RedisEmailCodeService(
        redis=redis_client,
        ttl_seconds=300,
        cooldown_seconds=60,
    )


def test_generate_code_writes_code_and_cooldown_keys(redis_client):
    service = make_service(redis_client)

    email = "Test@Example.com"
    code = service.generate_code(email, purpose="register")

    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isdigit()

    code_key = "email_code:register:test@example.com"
    cooldown_key = "email_code_cooldown:register:test@example.com"

    assert redis_client.get(code_key) == code
    assert redis_client.get(cooldown_key) == "1"

    code_ttl = redis_client.ttl(code_key)
    cooldown_ttl = redis_client.ttl(cooldown_key)

    assert 0 < code_ttl <= 300
    assert 0 < cooldown_ttl <= 60


def test_generate_code_rejects_duplicate_request_during_cooldown(redis_client):
    service = make_service(redis_client)

    service.generate_code("test@example.com", purpose="register")

    with pytest.raises(ValueError):
        service.generate_code("test@example.com", purpose="register")


def test_verify_code_success_deletes_code_key(redis_client):
    service = make_service(redis_client)

    email = "test@example.com"
    code = service.generate_code(email, purpose="register")

    assert service.verify_code(email, purpose="register", code=code) is True

    assert redis_client.get("email_code:register:test@example.com") is None


def test_verify_code_wrong_code_does_not_delete_code_key(redis_client):
    service = make_service(redis_client)

    email = "test@example.com"
    right_code = service.generate_code(email, purpose="register")

    assert service.verify_code(email, purpose="register", code="000000") is False

    assert redis_client.get("email_code:register:test@example.com") == right_code


def test_register_and_password_reset_codes_do_not_conflict(redis_client):
    service = make_service(redis_client)

    email = "test@example.com"

    register_code = service.generate_code(email, purpose="register")
    reset_code = service.generate_code(email, purpose="password_reset")

    assert redis_client.get("email_code:register:test@example.com") == register_code
    assert redis_client.get("email_code:password_reset:test@example.com") == reset_code

    assert service.verify_code(email, purpose="register", code=register_code) is True
    assert service.verify_code(email, purpose="password_reset", code=reset_code) is True