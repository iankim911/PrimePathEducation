# Test Data Cleanup Management Command

## Overview
The `clean_test_data` management command helps clean up test and QA data from the database that accumulates during development and testing phases.

## Usage

### Basic Commands

```bash
# Dry run to see what would be deleted (recommended first)
python manage.py clean_test_data --dry-run

# Clean all categories of test data older than 7 days
python manage.py clean_test_data

# Clean specific categories only
python manage.py clean_test_data --category=users
python manage.py clean_test_data --category=students
python manage.py clean_test_data --category=subprograms
python manage.py clean_test_data --category=exams
python manage.py clean_test_data --category=sessions

# Clean test data older than specific number of days
python manage.py clean_test_data --days-old=30
```

## What Gets Cleaned

### Test Users (`--category=users`)
- Usernames containing: test, demo, sample, temp, phase, nav_test, points_test, etc.
- Only deletes users older than specified days
- **Found in current system**: 19 test users

### Test Students (`--category=students`) 
- Students linked to test users
- Students with "test" in their name
- Respects age cutoff if Student model has created_at field

### Test SubPrograms (`--category=subprograms`)
- SubPrograms identified as test data by curriculum validation
- Examples: "Test SubProgram", "SHORT Answer Test SubProgram", etc.
- Uses `core.curriculum_constants.is_test_subprogram()` function

### Test Exams (`--category=exams`)
- Exams with "test" in the name
- Respects age cutoff if available

### Old Sessions (`--category=sessions`)
- Very old test sessions (30+ days beyond cutoff)
- Sessions from test users
- Helps reduce database bloat

## Safety Features

1. **Dry Run Mode**: Always use `--dry-run` first to preview changes
2. **Age Protection**: Only deletes old data (default: 7 days)
3. **Transaction Safety**: Uses database transactions for consistency
4. **Logging**: Actions are logged for audit trail
5. **Preview**: Shows examples of what will be deleted

## Example Output

```
--- Cleaning Test Users ---
Found 19 test users older than 2025-08-21
  - phase9test (created: 2025-08-13)
  - points_test_user (created: 2025-08-14)
  - testuser (created: 2025-08-17)
  ... and 16 more
```

## Recommended Usage

1. **Weekly Cleanup**: Run as part of regular maintenance
   ```bash
   python manage.py clean_test_data --dry-run
   python manage.py clean_test_data --days-old=14
   ```

2. **Pre-Production**: Before deploying to production
   ```bash
   python manage.py clean_test_data --category=all --days-old=1
   ```

3. **Development Reset**: When test data gets out of hand
   ```bash
   python manage.py clean_test_data --category=users --days-old=1
   python manage.py clean_test_data --category=sessions --days-old=1
   ```

## Related Commands

- `cleanup_expired_assignments` - Cleans expired teacher assignments
- `cleanup_sessions` - General session cleanup

## Notes

- Test subprogram filtering is also handled in views via `core/curriculum_constants.py`
- This command physically removes data from database
- Always backup database before running without `--dry-run`
- Command respects model field availability (created_at, etc.)