"""Init User and Coverage Table

Revision ID: 9fba5b95b94e
Revises: 
Create Date: 2023-04-15 13:50:17.514770

"""
from alembic import op
import sqlalchemy as sa

from models.utils import get_random_uuid_string

# revision identifiers, used by Alembic.
revision = '9fba5b95b94e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coverage",
        sa.Column("id", sa.String(length=50), primary_key=True, index=True, nullable=False, unique=True),
        sa.Column("name", sa.String(length=50), unique=True),
        sa.Column("db_schema", sa.String, unique=True, default=lambda x: "schema_" + get_random_uuid_string()),
    )

    op.create_table(
        "user",
        sa.Column("id", sa.String(length=50), primary_key=True, index=True, nullable=False, unique=True),
        sa.Column("email_id", sa.String, unique=True),
        sa.Column("password", sa.String),
        sa.Column("is_admin", sa.Boolean, default=False),
        sa.Column("coverage_id", sa.String(length=50), sa.ForeignKey("coverage.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user")
    op.drop_table("coverage")
