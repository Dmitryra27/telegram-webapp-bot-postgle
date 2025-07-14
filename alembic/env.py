import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from db_utils import Base

# Получаем URL из переменной окружения
config = context.config
db_url = os.getenv("DATABASE_URL")

# Передаём URL в конфиг Alembic
config.set_main_option("sqlalchemy.url", db_url)

#
# Interpret the config file for Python logging.
fileConfig(config.config_file_name)


def run_migrations_online():
    connectable = config.attributes.get("connection", None)
    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ВНИЗУ ФАЙЛА

target_metadata = Base.metadata
