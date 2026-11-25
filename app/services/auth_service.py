# Logika US-5: rejestracja i logowanie e-mailem i hasłem.
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.repositories import user_repository as repo

MIN_PASSWORD_LENGTH = 8


class AuthError(Exception):
    pass


def normalize_email(email):
    return (email or "").strip().lower()


def register(name, email, password):
    name = (name or "").strip()
    email = normalize_email(email)
    if not name:
        raise AuthError("Podaj imię.")
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise AuthError("Podaj poprawny adres e-mail.")
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise AuthError(f"Hasło musi mieć co najmniej {MIN_PASSWORD_LENGTH} znaków.")
    if repo.get_by_email(email) is not None:
        raise AuthError("Konto z tym adresem e-mail już istnieje.")

    user = User(name=name, email=email)
    user.set_password(password)  # NFR-4: w bazie tylko hash hasła
    try:
        return repo.save(user)
    except IntegrityError:
        # równoległa rejestracja tego samego e-maila (unikalność w bazie)
        repo.rollback()
        raise AuthError("Konto z tym adresem e-mail już istnieje.")


def authenticate(email, password):
    user = repo.get_by_email(normalize_email(email))
    if user is None or not user.check_password(password or ""):
        # ten sam komunikat, żeby nie zdradzać, czy konto istnieje
        raise AuthError("Nieprawidłowy e-mail lub hasło.")
    return user


def get_user(user_id):
    return repo.get_user(user_id) if user_id else None


def default_member_id(user_id):
    # pierwszy wyjazd użytkownika; konkretny wyjazd wybiera parametr ?wyjazd=
    member = repo.first_membership(user_id) if user_id else None
    return member.id if member else None
