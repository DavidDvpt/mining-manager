from sqlalchemy import text


async def test_migrated_postgres_database_is_available(test_db_session):
    current_database = await test_db_session.scalar(text("SELECT current_database()"))
    finder_count = await test_db_session.scalar(
        text("SELECT count(*) FROM finder")
    )

    assert current_database == "entropia_test"
    assert finder_count > 0
