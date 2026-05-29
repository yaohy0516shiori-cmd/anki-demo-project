# test core user flow: register, login, create note, study

import pytest


def test_register_user_creates_user_and_default_deck(core_services):
    user_id = core_services.user.register_user(
        email="test@example.com",
        username="tester",
        password="Password123",
    )

    user = core_services.user.get_user(user_id)

    assert user.user_id == user_id
    assert user.email == "test@example.com"
    assert user.username == "tester"
    assert user.password_hash != "Password123"

    decks = core_services.deck.get_all_decks(user_id)

    assert len(decks) == 1
    assert decks[0].user_id == user_id
    assert decks[0].deck_name == "Default"
    assert decks[0].is_default is True


def test_register_user_normalizes_email_and_rejects_duplicate_email(core_services):
    user_id = core_services.user.register_user(
        email="  Test@Example.com  ",
        username="tester1",
        password="Password123",
    )

    user = core_services.user.get_user(user_id)

    assert user.email == "test@example.com"

    with pytest.raises(ValueError, match="Email already exists"):
        core_services.user.register_user(
            email="TEST@example.com",
            username="tester2",
            password="Password123",
        )


def test_login_accepts_correct_password_and_rejects_wrong_password(core_services):
    user_id = core_services.user.register_user(
        email="login@example.com",
        username="login_user",
        password="Password123",
    )

    user = core_services.user.login(
        email="login@example.com",
        password="Password123",
    )

    assert user.user_id == user_id
    assert user.email == "login@example.com"

    with pytest.raises(ValueError):
        core_services.user.login(
            email="login@example.com",
            password="WrongPassword",
        )


def test_login_rejects_unknown_user(core_services):
    with pytest.raises(ValueError):
        core_services.user.login(
            email="missing@example.com",
            password="Password123",
        )


def test_reset_password_by_email_changes_login_password(core_services):
    user_id = core_services.user.register_user(
        email="reset@example.com",
        username="reset_user",
        password="OldPassword123",
    )

    updated_user = core_services.user.reset_password_by_email(
        email="reset@example.com",
        new_password="NewPassword123",
    )

    assert updated_user.user_id == user_id

    with pytest.raises(ValueError):
        core_services.user.login(
            email="reset@example.com",
            password="OldPassword123",
        )

    user = core_services.user.login(
        email="reset@example.com",
        password="NewPassword123",
    )

    assert user.user_id == user_id


def test_change_password_requires_correct_old_password(core_services):
    user_id = core_services.user.register_user(
        email="change@example.com",
        username="change_user",
        password="OldPassword123",
    )

    with pytest.raises(ValueError, match="Old password is incorrect"):
        core_services.user.change_password(
            user_id=user_id,
            old_password="WrongOldPassword",
            new_password="NewPassword123",
        )

    core_services.user.change_password(
        user_id=user_id,
        old_password="OldPassword123",
        new_password="NewPassword123",
    )

    with pytest.raises(ValueError):
        core_services.user.login(
            email="change@example.com",
            password="OldPassword123",
        )

    user = core_services.user.login(
        email="change@example.com",
        password="NewPassword123",
    )

    assert user.user_id == user_id