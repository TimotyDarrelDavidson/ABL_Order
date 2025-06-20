# alembic_mysql/env.py (Proposed and Corrected)
from __future__ import with_statement
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

# Add the parent directory of 'orders' (the top-level orders folder) to sys.path
# so that 'orders.models' can be imported.
# Assuming this env.py is in orders/alembic_mysql/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your Base.metadata from your new models.py file
from orders.models import Base # Corrected import path based on your image

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata # Using the Base from your orders.models

def get_url():
    # Use MySQL connection string
    # Ensure these environment variables are passed to your Docker container
    db_user = os.getenv("DB_USER", "root") # Matches your docker-compose.yml for mysql user
    db_pass = os.getenv("DB_PASSWORD", "") # Matches your docker-compose.yml for mysql root password
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306") # MySQL default port
    db_name = os.getenv("DB_NAME", "abl_order") # Matches your database name

    return (
        f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:"
        f"{db_port}/{db_name}"
    )

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(get_url())
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()