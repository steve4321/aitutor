async def seed_database():
    from scripts.seed_data import seed

    await seed()
