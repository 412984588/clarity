# Database Migration Guide

**Version**: 1.0
**Last Updated**: 2025-12-22

This guide covers database migration procedures for the Clarity API using Alembic.

---

## Quick Commands

```bash
# Check current migration status
alembic current

# Check for multiple heads (should show only one)
alembic heads

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"
```

---

## Migration Workflow

### 1. Before Making Changes

```bash
cd clarity-api

# Ensure you're on latest
git pull origin main

# Check current migration state
poetry run alembic current
poetry run alembic heads  # Should show exactly 1 head
```

### 2. Create New Migration

```bash
# Make your model changes in app/models/

# Auto-generate migration
poetry run alembic revision --autogenerate -m "add_column_to_users"

# Review the generated file in alembic/versions/
# IMPORTANT: Always review auto-generated migrations!
```

### 3. Review Migration File

Check the generated migration for:
- [ ] `upgrade()` function has correct changes
- [ ] `downgrade()` function properly reverses changes
- [ ] No destructive operations on production data
- [ ] Indexes are created for frequently queried columns

### 4. Test Migration

```bash
# Apply migration
poetry run alembic upgrade head

# Run tests to verify
poetry run pytest -v

# If issues, rollback
poetry run alembic downgrade -1
```

### 5. Commit and Push

```bash
git add alembic/versions/
git commit -m "feat(db): add column to users table"
git push
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests pass locally
- [ ] Migration has been tested on staging
- [ ] Backup has been created
- [ ] Downgrade path has been tested
- [ ] Team has been notified of deployment window

### Deployment Steps

```bash
# 1. Create backup (use scripts/migrate.sh)
./scripts/migrate.sh backup

# 2. Apply migrations
./scripts/migrate.sh upgrade

# 3. Verify application health
curl https://api.clarity.app/health

# 4. If issues, rollback
./scripts/migrate.sh rollback
```

---

## Troubleshooting

### Multiple Heads Error

```
ERROR: Multiple head revisions are present
```

**Solution**: Merge the heads

```bash
# View the multiple heads
alembic heads

# Create merge migration
alembic merge -m "merge heads" <rev1> <rev2>

# Apply the merge
alembic upgrade head
```

### Migration Already Applied

```
ERROR: Target database is not up to date
```

**Solution**: Stamp the current revision

```bash
# Check current state
alembic current

# If migration was applied manually, stamp it
alembic stamp <revision>
```

### Column Already Exists

```
ERROR: column "xyz" of relation "table" already exists
```

**Solution**: Add existence check in migration

```python
def upgrade():
    # Check if column exists before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('table_name')]

    if 'xyz' not in columns:
        op.add_column('table_name', sa.Column('xyz', sa.String()))
```

### Foreign Key Constraint Violation

```
ERROR: insert or update on table violates foreign key constraint
```

**Solution**:
1. Ensure referenced rows exist
2. Add `nullable=True` initially, then populate data, then make non-nullable

---

## Best Practices

### DO

- ✅ Always include `downgrade()` function
- ✅ Test migrations on a copy of production data
- ✅ Create backups before production migrations
- ✅ Use batch operations for large tables
- ✅ Add indexes for foreign keys

### DON'T

- ❌ Delete columns with important data without backup
- ❌ Rename columns (add new, migrate data, drop old)
- ❌ Run migrations during peak traffic
- ❌ Skip the staging environment test

---

## Migration Script Usage

The `scripts/migrate.sh` script provides safe migration operations:

```bash
# Show current status
./scripts/migrate.sh status

# Create backup and upgrade
./scripts/migrate.sh upgrade

# Rollback last migration
./scripts/migrate.sh rollback

# Create backup only
./scripts/migrate.sh backup
```

---

## Emergency Rollback

If a migration causes production issues:

```bash
# 1. Immediately rollback
cd clarity-api
poetry run alembic downgrade -1

# 2. Restart application
# (depends on your deployment method)

# 3. Verify health
curl https://api.clarity.app/health

# 4. Investigate and fix before re-applying
```

---

## CI/CD Integration

Migrations are automatically applied in CI:

```yaml
# .github/workflows/backend.yml
- name: Run migrations
  run: poetry run alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Ensure `DATABASE_URL` is set in GitHub Secrets for CI to work.
