from sqlalchemy.ext.asyncio import create_async_engine


async_engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', echo=True)