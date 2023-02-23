from fastapi import Header


def user_headers(
    x_forwarded_user: str | None = Header(),
    x_forwarded_groups: str | None = Header(default=None),
    x_forwarded_email: str | None = Header(default=None),
    x_forwarded_preferred_username: str | None = Header(default=None),
):
    return {
        "X-Forwarded-User": x_forwarded_user,
        "X-Forwarded-Groups": x_forwarded_groups,
        "X-Forwarded-Email": x_forwarded_email,
        "X-Forwarded-Preferred-Username": x_forwarded_preferred_username,
    }
