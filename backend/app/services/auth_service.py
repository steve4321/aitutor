async def register_user(email: str | None, phone: str | None, name: str, password: str, role: str):
    raise NotImplementedError


async def authenticate_user(login: str, password: str):
    raise NotImplementedError
