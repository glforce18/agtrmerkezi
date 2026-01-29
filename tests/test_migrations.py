"""
Database Migration Tests
"""

import pytest

from alembic import command
from alembic.config import Config


@pytest.mark.slow
def test_migrations_can_upgrade_and_downgrade():
    """Test that migrations can upgrade and downgrade successfully"""
    alembic_cfg = Config("alembic.ini")

    # Test upgrade to head
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Migration upgrade failed: {e}")

    # Test downgrade by one revision
    try:
        command.downgrade(alembic_cfg, "-1")
    except Exception as e:
        pytest.fail(f"Migration downgrade failed: {e}")

    # Upgrade back to head
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Migration re-upgrade failed: {e}")


@pytest.mark.slow
def test_migration_has_no_duplicate_revision_ids():
    """Test that there are no duplicate revision IDs"""
    alembic_cfg = Config("alembic.ini")
    script = command.ScriptDirectory.from_config(alembic_cfg)

    revisions = set()
    for revision in script.walk_revisions():
        if revision.revision in revisions:
            pytest.fail(f"Duplicate revision ID found: {revision.revision}")
        revisions.add(revision.revision)
