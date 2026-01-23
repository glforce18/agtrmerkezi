#!/usr/bin/env python3
"""
AGTR Merkezi - Health Check & Validation Script
Database-Model sync, API tests, data integrity checks
"""

import sys
import os
sys.path.insert(0, '/var/www/agtrmerkezi')

import json
import requests
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

# Setup Django-style settings
os.environ.setdefault('ENV', 'production')

from app.models.connection import get_db, engine
from app.models.database import (
    Base, User, ForumTopic, ForumReply, ForumCategory,
    Payment, GameServer
)

# ANSI Colors
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")

def print_ok(text: str):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {text}")

def print_warn(text: str):
    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_error(text: str):
    print(f"  {Colors.RED}✗{Colors.RESET} {text}")

def print_info(text: str):
    print(f"  {Colors.BLUE}ℹ{Colors.RESET} {text}")


# ==================== DATABASE-MODEL SYNC CHECK ====================

def check_model_database_sync() -> Tuple[int, int]:
    """Check if SQLAlchemy models match database tables"""
    print_header("DATABASE-MODEL SYNC CHECK")

    errors = 0
    warnings = 0

    inspector = inspect(engine)

    # Models to check
    models = [
        (User, 'users'),
        (ForumTopic, 'forum_topics'),
        (ForumReply, 'forum_replies'),
        (ForumCategory, 'forum_categories'),
        (Payment, 'payments'),
        (GameServer, 'game_servers'),
    ]

    for model, table_name in models:
        try:
            # Get database columns
            db_columns = {col['name']: col for col in inspector.get_columns(table_name)}

            # Get model columns
            model_columns = {c.name: c for c in model.__table__.columns}

            # Check for missing in model
            missing_in_model = set(db_columns.keys()) - set(model_columns.keys())
            if missing_in_model:
                print_error(f"{table_name}: Missing in model: {missing_in_model}")
                errors += len(missing_in_model)

            # Check for missing in database
            missing_in_db = set(model_columns.keys()) - set(db_columns.keys())
            if missing_in_db:
                print_warn(f"{table_name}: Missing in database: {missing_in_db}")
                warnings += len(missing_in_db)

            if not missing_in_model and not missing_in_db:
                print_ok(f"{table_name}: Model and database are in sync")

        except Exception as e:
            print_error(f"{table_name}: Error checking - {e}")
            errors += 1

    return errors, warnings


# ==================== DATA INTEGRITY CHECK ====================

def check_data_integrity() -> Tuple[int, int]:
    """Check for data integrity issues"""
    print_header("DATA INTEGRITY CHECK")

    errors = 0
    warnings = 0

    db = next(get_db())

    try:
        # Check negative likes on topics
        result = db.execute(text("SELECT COUNT(*) FROM forum_topics WHERE likes < 0")).scalar()
        if result > 0:
            print_error(f"Topics with negative likes: {result}")
            errors += 1
        else:
            print_ok("No topics with negative likes")

        # Check negative likes on replies
        result = db.execute(text("SELECT COUNT(*) FROM forum_replies WHERE likes < 0")).scalar()
        if result > 0:
            print_error(f"Replies with negative likes: {result}")
            errors += 1
        else:
            print_ok("No replies with negative likes")

        # Check orphaned forum_likes (likes without topic/reply)
        result = db.execute(text("""
            SELECT COUNT(*) FROM forum_likes fl
            LEFT JOIN forum_topics ft ON fl.content_type = 'topic' AND fl.content_id = ft.id
            LEFT JOIN forum_replies fr ON fl.content_type = 'reply' AND fl.content_id = fr.id
            WHERE ft.id IS NULL AND fr.id IS NULL
        """)).scalar()
        if result > 0:
            print_warn(f"Orphaned likes (content deleted): {result}")
            warnings += 1
        else:
            print_ok("No orphaned likes")

        # Check likes count accuracy
        mismatched_topics = db.execute(text("""
            SELECT t.id, t.likes as stored, COUNT(fl.id) as actual
            FROM forum_topics t
            LEFT JOIN forum_likes fl ON fl.content_type = 'topic' AND fl.content_id = t.id
            GROUP BY t.id
            HAVING stored != actual
        """)).fetchall()

        if mismatched_topics:
            print_warn(f"Topics with mismatched like counts: {len(mismatched_topics)}")
            for row in mismatched_topics[:5]:
                print_info(f"  Topic #{row[0]}: stored={row[1]}, actual={row[2]}")
            warnings += 1
        else:
            print_ok("All topic like counts are accurate")

        # Check for users with negative balance
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE balance_coin < 0")).scalar()
        if result > 0:
            print_error(f"Users with negative balance: {result}")
            errors += 1
        else:
            print_ok("No users with negative balance")

        # Check for orphaned replies (topic deleted)
        result = db.execute(text("""
            SELECT COUNT(*) FROM forum_replies r
            LEFT JOIN forum_topics t ON r.topic_id = t.id
            WHERE t.id IS NULL
        """)).scalar()
        if result > 0:
            print_warn(f"Orphaned replies (topic deleted): {result}")
            warnings += 1
        else:
            print_ok("No orphaned replies")

    except Exception as e:
        print_error(f"Data integrity check error: {e}")
        errors += 1
    finally:
        db.close()

    return errors, warnings


# ==================== API ENDPOINT CHECK ====================

def check_api_endpoints() -> Tuple[int, int]:
    """Check if critical API endpoints are responding"""
    print_header("API ENDPOINT CHECK")

    errors = 0
    warnings = 0

    base_url = "http://localhost:8000"

    endpoints = [
        ("GET", "/api/health", 200),
        ("GET", "/api/forum/categories", 200),
        ("GET", "/api/servers", 200),
        ("GET", "/api/leaderboard", 200),
        ("GET", "/api/tournaments", 200),
    ]

    for method, path, expected_status in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{base_url}{path}", timeout=5)
            else:
                resp = requests.post(f"{base_url}{path}", timeout=5)

            if resp.status_code == expected_status:
                print_ok(f"{method} {path} -> {resp.status_code}")
            elif resp.status_code < 500:
                print_warn(f"{method} {path} -> {resp.status_code} (expected {expected_status})")
                warnings += 1
            else:
                print_error(f"{method} {path} -> {resp.status_code}")
                errors += 1
        except requests.exceptions.ConnectionError:
            print_error(f"{method} {path} -> Connection refused")
            errors += 1
        except Exception as e:
            print_error(f"{method} {path} -> {e}")
            errors += 1

    return errors, warnings


# ==================== SECURITY CHECK ====================

def check_security() -> Tuple[int, int]:
    """Check for common security issues"""
    print_header("SECURITY CHECK")

    errors = 0
    warnings = 0

    # Check .env file permissions
    env_path = "/var/www/agtrmerkezi/.env"
    if os.path.exists(env_path):
        mode = oct(os.stat(env_path).st_mode)[-3:]
        if mode in ['600', '400']:
            print_ok(f".env file permissions: {mode}")
        else:
            print_warn(f".env file permissions too open: {mode} (should be 600)")
            warnings += 1

    # Check for debug mode
    from app.core.config import settings
    if hasattr(settings, 'DEBUG') and settings.DEBUG:
        print_warn("DEBUG mode is enabled in production!")
        warnings += 1
    else:
        print_ok("DEBUG mode is disabled")

    # Check CORS settings
    if hasattr(settings, 'CORS_ORIGINS'):
        if '*' in str(settings.CORS_ORIGINS):
            print_warn("CORS allows all origins (*)")
            warnings += 1
        else:
            print_ok("CORS is properly configured")

    return errors, warnings


# ==================== PERFORMANCE CHECK ====================

def check_performance() -> Tuple[int, int]:
    """Check for performance issues"""
    print_header("PERFORMANCE CHECK")

    errors = 0
    warnings = 0

    db = next(get_db())

    try:
        # Check for missing indexes on foreign keys
        # This is a simplified check

        # Check table sizes
        tables = ['users', 'forum_topics', 'forum_replies', 'forum_likes', 'payments']
        for table in tables:
            try:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print_info(f"{table}: {count:,} rows")
            except:
                pass

        # Check for slow queries (if slow_query_log is enabled)
        print_ok("Table sizes checked")

    except Exception as e:
        print_error(f"Performance check error: {e}")
        errors += 1
    finally:
        db.close()

    return errors, warnings


# ==================== FIX FUNCTIONS ====================

def fix_like_counts():
    """Fix mismatched like counts"""
    print_header("FIXING LIKE COUNTS")

    db = next(get_db())

    try:
        # Fix topic likes
        db.execute(text("""
            UPDATE forum_topics t
            SET likes = (
                SELECT COUNT(*) FROM forum_likes
                WHERE content_type = 'topic' AND content_id = t.id
            )
        """))

        # Fix reply likes
        db.execute(text("""
            UPDATE forum_replies r
            SET likes = (
                SELECT COUNT(*) FROM forum_likes
                WHERE content_type = 'reply' AND content_id = r.id
            )
        """))

        db.commit()
        print_ok("Like counts synchronized from forum_likes table")

    except Exception as e:
        db.rollback()
        print_error(f"Fix failed: {e}")
    finally:
        db.close()


def fix_negative_values():
    """Fix negative values in database"""
    print_header("FIXING NEGATIVE VALUES")

    db = next(get_db())

    try:
        # Fix negative likes
        result = db.execute(text("UPDATE forum_topics SET likes = 0 WHERE likes < 0"))
        print_ok(f"Fixed {result.rowcount} topics with negative likes")

        result = db.execute(text("UPDATE forum_replies SET likes = 0 WHERE likes < 0"))
        print_ok(f"Fixed {result.rowcount} replies with negative likes")

        # Fix negative balances
        result = db.execute(text("UPDATE users SET balance_coin = 0 WHERE balance_coin < 0"))
        print_ok(f"Fixed {result.rowcount} users with negative balance")

        db.commit()

    except Exception as e:
        db.rollback()
        print_error(f"Fix failed: {e}")
    finally:
        db.close()


# ==================== MAIN ====================

def main():
    print(f"\n{Colors.BOLD}AGTR Merkezi Health Check{Colors.RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_errors = 0
    total_warnings = 0

    # Run checks
    e, w = check_model_database_sync()
    total_errors += e
    total_warnings += w

    e, w = check_data_integrity()
    total_errors += e
    total_warnings += w

    e, w = check_api_endpoints()
    total_errors += e
    total_warnings += w

    e, w = check_security()
    total_errors += e
    total_warnings += w

    e, w = check_performance()
    total_errors += e
    total_warnings += w

    # Summary
    print_header("SUMMARY")

    if total_errors == 0 and total_warnings == 0:
        print(f"  {Colors.GREEN}{Colors.BOLD}All checks passed!{Colors.RESET}")
    else:
        if total_errors > 0:
            print(f"  {Colors.RED}Errors: {total_errors}{Colors.RESET}")
        if total_warnings > 0:
            print(f"  {Colors.YELLOW}Warnings: {total_warnings}{Colors.RESET}")

    print()

    # Return exit code
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='AGTR Merkezi Health Check')
    parser.add_argument('--fix-likes', action='store_true', help='Fix like counts')
    parser.add_argument('--fix-negative', action='store_true', help='Fix negative values')
    parser.add_argument('--fix-all', action='store_true', help='Fix all issues')

    args = parser.parse_args()

    if args.fix_all or args.fix_likes:
        fix_like_counts()

    if args.fix_all or args.fix_negative:
        fix_negative_values()

    if not (args.fix_all or args.fix_likes or args.fix_negative):
        sys.exit(main())
