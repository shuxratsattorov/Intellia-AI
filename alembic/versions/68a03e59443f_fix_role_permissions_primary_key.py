"""fix role_permissions primary key

Revision ID: 68a03e59443f
Revises: 80746b5cac69
Create Date: 2026-03-09 23:16:56.477962
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '68a03e59443f'
down_revision: Union[str, Sequence[str], None] = '80746b5cac69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("role_permissions_pkey", "role_permissions", type_="primary")
    op.drop_column("role_permissions", "id")
    op.create_primary_key(
        "role_permissions_pkey",
        "role_permissions",
        ["role_id", "permission_id"],
    )

    op.drop_constraint("user_roles_pkey", "user_roles", type_="primary")
    op.drop_column("user_roles", "id")
    op.create_primary_key(
        "user_roles_pkey",
        "user_roles",
        ["user_id", "role_id"],
    )


def downgrade() -> None:
    op.drop_constraint("user_roles_pkey", "user_roles", type_="primary")
    op.add_column("user_roles", sa.Column("id", sa.Integer(), nullable=False))
    op.create_primary_key(
        "user_roles_pkey",
        "user_roles",
        ["user_id", "role_id", "id"],
    )

    op.drop_constraint("role_permissions_pkey", "role_permissions", type_="primary")
    op.add_column("role_permissions", sa.Column("id", sa.Integer(), nullable=False))
    op.create_primary_key(
        "role_permissions_pkey",
        "role_permissions",
        ["role_id", "permission_id", "id"],
    )
