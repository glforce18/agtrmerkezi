#!/usr/bin/env python3
"""
AGTR Merkezi - Comprehensive Health Check & Validation Script
v2.0 - 50+ checks across security, performance, data integrity, and more
"""

import sys
import os
sys.path.insert(0, '/var/www/agtrmerkezi')

import json
import re
import glob
import subprocess
import requests
import hashlib
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Setup
os.environ.setdefault('ENV', 'production')

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

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
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")

def print_subheader(text: str):
    print(f"\n{Colors.MAGENTA}  [{text}]{Colors.RESET}")

def print_ok(text: str):
    print(f"    {Colors.GREEN}✓{Colors.RESET} {text}")

def print_warn(text: str):
    print(f"    {Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_error(text: str):
    print(f"    {Colors.RED}✗{Colors.RESET} {text}")

def print_info(text: str):
    print(f"    {Colors.BLUE}ℹ{Colors.RESET} {text}")

def print_skip(text: str):
    print(f"    {Colors.DIM}○ {text}{Colors.RESET}")


class HealthChecker:
    def __init__(self):
        self.errors = 0
        self.warnings = 0
        self.checks_passed = 0
        self.checks_total = 0
        self.results = {}

    def add_result(self, category: str, check: str, status: str, message: str = ""):
        self.checks_total += 1
        if status == "ok":
            self.checks_passed += 1
            print_ok(f"{check}" + (f" - {message}" if message else ""))
        elif status == "warn":
            self.warnings += 1
            print_warn(f"{check}" + (f" - {message}" if message else ""))
        elif status == "error":
            self.errors += 1
            print_error(f"{check}" + (f" - {message}" if message else ""))
        elif status == "skip":
            print_skip(f"{check}" + (f" - {message}" if message else ""))
        elif status == "info":
            print_info(f"{check}" + (f" - {message}" if message else ""))

    # ==================== 1. DATABASE-MODEL SYNC ====================
    def check_model_database_sync(self):
        print_header("1. DATABASE-MODEL SYNC CHECK")

        inspector = inspect(engine)
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
                db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
                model_columns = {c.name: c for c in model.__table__.columns}

                missing_in_model = set(db_columns.keys()) - set(model_columns.keys())
                missing_in_db = set(model_columns.keys()) - set(db_columns.keys())

                if missing_in_model:
                    self.add_result("sync", f"{table_name}", "error", f"Missing in model: {missing_in_model}")
                elif missing_in_db:
                    self.add_result("sync", f"{table_name}", "warn", f"Missing in DB: {missing_in_db}")
                else:
                    self.add_result("sync", f"{table_name}", "ok", "In sync")
            except Exception as e:
                self.add_result("sync", f"{table_name}", "error", str(e))

    # ==================== 2. DATA INTEGRITY ====================
    def check_data_integrity(self):
        print_header("2. DATA INTEGRITY CHECK")
        db = next(get_db())

        try:
            print_subheader("Negative Values")

            # Negative likes - topics
            result = db.execute(text("SELECT COUNT(*) FROM forum_topics WHERE likes < 0")).scalar()
            if result > 0:
                self.add_result("integrity", "Topics negative likes", "error", f"{result} found")
            else:
                self.add_result("integrity", "Topics negative likes", "ok", "None")

            # Negative likes - replies
            result = db.execute(text("SELECT COUNT(*) FROM forum_replies WHERE likes < 0")).scalar()
            if result > 0:
                self.add_result("integrity", "Replies negative likes", "error", f"{result} found")
            else:
                self.add_result("integrity", "Replies negative likes", "ok", "None")

            # Negative balance
            result = db.execute(text("SELECT COUNT(*) FROM users WHERE balance_coin < 0")).scalar()
            if result > 0:
                self.add_result("integrity", "Users negative balance", "error", f"{result} found")
            else:
                self.add_result("integrity", "Users negative balance", "ok", "None")

            # Negative view count
            result = db.execute(text("SELECT COUNT(*) FROM forum_topics WHERE view_count < 0")).scalar()
            if result > 0:
                self.add_result("integrity", "Topics negative views", "error", f"{result} found")
            else:
                self.add_result("integrity", "Topics negative views", "ok", "None")

            print_subheader("Orphan Records")

            # Orphaned likes
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_likes fl
                LEFT JOIN forum_topics ft ON fl.content_type = 'topic' AND fl.content_id = ft.id
                LEFT JOIN forum_replies fr ON fl.content_type = 'reply' AND fl.content_id = fr.id
                WHERE ft.id IS NULL AND fr.id IS NULL
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Orphaned likes", "warn", f"{result} found")
            else:
                self.add_result("integrity", "Orphaned likes", "ok", "None")

            # Orphaned replies
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_replies r
                LEFT JOIN forum_topics t ON r.topic_id = t.id
                WHERE t.id IS NULL
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Orphaned replies", "warn", f"{result} found")
            else:
                self.add_result("integrity", "Orphaned replies", "ok", "None")

            # Orphaned topics (category deleted)
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_topics t
                LEFT JOIN forum_categories c ON t.category_id = c.id
                WHERE c.id IS NULL
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Orphaned topics", "warn", f"{result} found")
            else:
                self.add_result("integrity", "Orphaned topics", "ok", "None")

            print_subheader("Count Accuracy")

            # Like count accuracy
            mismatched = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT t.id FROM forum_topics t
                    LEFT JOIN (SELECT content_id, COUNT(*) as cnt FROM forum_likes WHERE content_type='topic' GROUP BY content_id) fl
                    ON t.id = fl.content_id
                    WHERE COALESCE(t.likes, 0) != COALESCE(fl.cnt, 0)
                ) x
            """)).scalar()
            if mismatched > 0:
                self.add_result("integrity", "Topic like count accuracy", "warn", f"{mismatched} mismatched")
            else:
                self.add_result("integrity", "Topic like count accuracy", "ok", "All accurate")

            # Reply count accuracy
            mismatched = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT t.id FROM forum_topics t
                    LEFT JOIN (SELECT topic_id, COUNT(*) as cnt FROM forum_replies WHERE is_active=1 GROUP BY topic_id) r
                    ON t.id = r.topic_id
                    WHERE COALESCE(t.reply_count, 0) != COALESCE(r.cnt, 0)
                ) x
            """)).scalar()
            if mismatched > 0:
                self.add_result("integrity", "Reply count accuracy", "warn", f"{mismatched} mismatched")
            else:
                self.add_result("integrity", "Reply count accuracy", "ok", "All accurate")

            print_subheader("Duplicate Detection")

            # Duplicate usernames
            result = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT LOWER(username), COUNT(*) as cnt FROM users GROUP BY LOWER(username) HAVING cnt > 1
                ) x
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Duplicate usernames", "error", f"{result} found")
            else:
                self.add_result("integrity", "Duplicate usernames", "ok", "None")

            # Duplicate emails
            result = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT LOWER(email), COUNT(*) as cnt FROM users GROUP BY LOWER(email) HAVING cnt > 1
                ) x
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Duplicate emails", "error", f"{result} found")
            else:
                self.add_result("integrity", "Duplicate emails", "ok", "None")

            # Duplicate steam IDs
            result = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT steam_id, COUNT(*) as cnt FROM users WHERE steam_id IS NOT NULL GROUP BY steam_id HAVING cnt > 1
                ) x
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Duplicate Steam IDs", "error", f"{result} found")
            else:
                self.add_result("integrity", "Duplicate Steam IDs", "ok", "None")

            # Duplicate topic slugs
            result = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT slug, COUNT(*) as cnt FROM forum_topics GROUP BY slug HAVING cnt > 1
                ) x
            """)).scalar()
            if result > 0:
                self.add_result("integrity", "Duplicate topic slugs", "warn", f"{result} found")
            else:
                self.add_result("integrity", "Duplicate topic slugs", "ok", "None")

        except Exception as e:
            self.add_result("integrity", "Data integrity check", "error", str(e))
        finally:
            db.close()

    # ==================== 3. SECURITY CHECK ====================
    def check_security(self):
        print_header("3. SECURITY CHECK")

        print_subheader("File Permissions")

        # .env file permissions
        env_path = "/var/www/agtrmerkezi/.env"
        if os.path.exists(env_path):
            mode = oct(os.stat(env_path).st_mode)[-3:]
            if mode in ['600', '400']:
                self.add_result("security", ".env permissions", "ok", mode)
            else:
                self.add_result("security", ".env permissions", "warn", f"{mode} (should be 600)")

        # Config files
        for config_file in ['alembic.ini', 'docker-compose.yml']:
            path = f"/var/www/agtrmerkezi/{config_file}"
            if os.path.exists(path):
                mode = oct(os.stat(path).st_mode)[-3:]
                if int(mode) <= 644:
                    self.add_result("security", f"{config_file} permissions", "ok", mode)
                else:
                    self.add_result("security", f"{config_file} permissions", "warn", mode)

        print_subheader("Configuration")

        # Debug mode
        try:
            from app.core.config import settings
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                self.add_result("security", "DEBUG mode", "warn", "Enabled in production!")
            else:
                self.add_result("security", "DEBUG mode", "ok", "Disabled")

            # Secret key strength
            if hasattr(settings, 'SECRET_KEY'):
                if len(settings.SECRET_KEY) < 32:
                    self.add_result("security", "SECRET_KEY length", "warn", f"{len(settings.SECRET_KEY)} chars (min 32)")
                else:
                    self.add_result("security", "SECRET_KEY length", "ok", f"{len(settings.SECRET_KEY)} chars")
        except:
            pass

        print_subheader("Code Security Scan")

        # SQL Injection patterns in Python files
        dangerous_patterns = [
            (r'f["\'].*SELECT.*\{', 'SQL Injection (f-string)'),
            (r'\.format\(.*SELECT', 'SQL Injection (.format)'),
            (r'%s.*SELECT.*%', 'SQL Injection (% format)'),
            (r'exec\s*\(', 'Code Injection (exec)'),
            (r'eval\s*\(', 'Code Injection (eval)'),
            (r'os\.system\s*\(', 'Command Injection (os.system)'),
            (r'subprocess\.call\s*\([^,]+,\s*shell\s*=\s*True', 'Command Injection (shell=True)'),
        ]

        py_files = glob.glob('/var/www/agtrmerkezi/app/**/*.py', recursive=True)
        security_issues = []

        for pattern, issue_name in dangerous_patterns:
            found = False
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if re.search(pattern, content, re.IGNORECASE):
                            # Exclude false positives (comments, etc.)
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if re.search(pattern, line, re.IGNORECASE) and not line.strip().startswith('#'):
                                    security_issues.append((issue_name, py_file, i+1))
                                    found = True
                                    break
                except:
                    pass
            if not found:
                self.add_result("security", f"Pattern: {issue_name}", "ok", "Not found")

        for issue, file, line in security_issues[:5]:  # Show max 5
            self.add_result("security", f"{issue}", "warn", f"{os.path.basename(file)}:{line}")

        print_subheader("XSS Protection")

        # Check v-html usage in Vue files
        vue_files = glob.glob('/var/www/agtrmerkezi/frontend/src/**/*.vue', recursive=True)
        unsafe_vhtml = 0
        for vue_file in vue_files:
            try:
                with open(vue_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # v-html without DOMPurify
                    vhtml_matches = re.findall(r'v-html="([^"]+)"', content)
                    for match in vhtml_matches:
                        if 'DOMPurify' not in match and 'sanitize' not in match.lower():
                            unsafe_vhtml += 1
            except:
                pass

        if unsafe_vhtml > 0:
            self.add_result("security", "Unsafe v-html usage", "warn", f"{unsafe_vhtml} instances")
        else:
            self.add_result("security", "XSS (v-html)", "ok", "All sanitized")

        print_subheader("Authentication")

        db = next(get_db())
        try:
            # Admin accounts
            admin_count = db.execute(text("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'superadmin')")).scalar()
            self.add_result("security", "Admin accounts", "info", f"{admin_count} found")

            # Users without password
            no_pass = db.execute(text("SELECT COUNT(*) FROM users WHERE password_hash IS NULL OR password_hash = ''")).scalar()
            if no_pass > 0:
                self.add_result("security", "Users without password", "error", f"{no_pass} found")
            else:
                self.add_result("security", "Users without password", "ok", "None")

            # Weak password hashes (too short)
            weak_hash = db.execute(text("SELECT COUNT(*) FROM users WHERE LENGTH(password_hash) < 50")).scalar()
            if weak_hash > 0:
                self.add_result("security", "Weak password hashes", "warn", f"{weak_hash} found")
            else:
                self.add_result("security", "Password hash strength", "ok", "All strong")

            # Expired sessions
            expired = db.execute(text("""
                SELECT COUNT(*) FROM user_sessions WHERE expires_at < NOW()
            """)).scalar() or 0
            if expired > 100:
                self.add_result("security", "Expired sessions", "warn", f"{expired} (should clean up)")
            else:
                self.add_result("security", "Expired sessions", "ok", f"{expired}")

        except Exception as e:
            self.add_result("security", "Auth check", "error", str(e))
        finally:
            db.close()

    # ==================== 4. API ENDPOINTS ====================
    def check_api_endpoints(self):
        print_header("4. API ENDPOINT CHECK")

        base_url = "http://localhost:8000"

        print_subheader("Public Endpoints")

        endpoints = [
            ("GET", "/api/health", 200, "Health check"),
            ("GET", "/api/forum/categories", 200, "Forum categories"),
            ("GET", "/api/servers", 200, "Server list"),
            ("GET", "/api/leaderboard", 200, "Leaderboard"),
            ("GET", "/api/tournaments", 200, "Tournaments"),
        ]

        for method, path, expected, name in endpoints:
            try:
                resp = requests.get(f"{base_url}{path}", timeout=5)
                if resp.status_code == expected:
                    self.add_result("api", name, "ok", f"{resp.status_code}")
                elif resp.status_code < 500:
                    self.add_result("api", name, "warn", f"{resp.status_code} (expected {expected})")
                else:
                    self.add_result("api", name, "error", f"{resp.status_code}")
            except requests.exceptions.ConnectionError:
                self.add_result("api", name, "error", "Connection refused")
            except Exception as e:
                self.add_result("api", name, "error", str(e)[:50])

        print_subheader("Auth-Protected Endpoints")

        protected = [
            ("GET", "/api/user/me", 401, "User profile (should require auth)"),
            ("POST", "/api/forum/topics", 401, "Create topic (should require auth)"),
            ("POST", "/api/jackpot/bet", 401, "Jackpot bet (should require auth)"),
        ]

        for method, path, expected, name in protected:
            try:
                if method == "GET":
                    resp = requests.get(f"{base_url}{path}", timeout=5)
                else:
                    resp = requests.post(f"{base_url}{path}", timeout=5)

                if resp.status_code in [401, 403, 422]:
                    self.add_result("api", name, "ok", "Protected")
                else:
                    self.add_result("api", name, "warn", f"{resp.status_code} (expected auth error)")
            except:
                self.add_result("api", name, "skip", "Could not test")

        print_subheader("Response Times")

        fast_endpoints = [("/api/health", 100), ("/api/forum/categories", 500)]
        for path, max_ms in fast_endpoints:
            try:
                start = datetime.now()
                resp = requests.get(f"{base_url}{path}", timeout=5)
                elapsed = (datetime.now() - start).total_seconds() * 1000

                if elapsed < max_ms:
                    self.add_result("api", f"{path} response time", "ok", f"{elapsed:.0f}ms")
                else:
                    self.add_result("api", f"{path} response time", "warn", f"{elapsed:.0f}ms (max {max_ms}ms)")
            except:
                self.add_result("api", f"{path} response time", "skip", "Could not test")

    # ==================== 5. SYSTEM RESOURCES ====================
    def check_system_resources(self):
        print_header("5. SYSTEM RESOURCES CHECK")

        print_subheader("Disk Space")

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        if disk_percent < 70:
            self.add_result("system", "Disk usage", "ok", f"{disk_percent}%")
        elif disk_percent < 85:
            self.add_result("system", "Disk usage", "warn", f"{disk_percent}%")
        else:
            self.add_result("system", "Disk usage", "error", f"{disk_percent}% (critical)")

        # Project directory size
        try:
            result = subprocess.run(['du', '-sh', '/var/www/agtrmerkezi'], capture_output=True, text=True)
            size = result.stdout.split()[0] if result.stdout else "unknown"
            self.add_result("system", "Project size", "info", size)
        except:
            pass

        # Log directory size
        try:
            result = subprocess.run(['du', '-sh', '/var/www/agtrmerkezi/logs'], capture_output=True, text=True)
            size = result.stdout.split()[0] if result.stdout else "unknown"
            if 'G' in size and float(size.replace('G', '')) > 1:
                self.add_result("system", "Log directory size", "warn", f"{size} (consider rotation)")
            else:
                self.add_result("system", "Log directory size", "ok", size)
        except:
            pass

        # Static files size
        try:
            result = subprocess.run(['du', '-sh', '/var/www/agtrmerkezi/static'], capture_output=True, text=True)
            size = result.stdout.split()[0] if result.stdout else "unknown"
            self.add_result("system", "Static files size", "info", size)
        except:
            pass

        print_subheader("Memory")

        mem = psutil.virtual_memory()
        if mem.percent < 70:
            self.add_result("system", "Memory usage", "ok", f"{mem.percent}%")
        elif mem.percent < 85:
            self.add_result("system", "Memory usage", "warn", f"{mem.percent}%")
        else:
            self.add_result("system", "Memory usage", "error", f"{mem.percent}% (critical)")

        # Available memory
        avail_gb = mem.available / (1024**3)
        self.add_result("system", "Available memory", "info", f"{avail_gb:.1f} GB")

        print_subheader("CPU")

        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 70:
            self.add_result("system", "CPU usage", "ok", f"{cpu_percent}%")
        elif cpu_percent < 90:
            self.add_result("system", "CPU usage", "warn", f"{cpu_percent}%")
        else:
            self.add_result("system", "CPU usage", "error", f"{cpu_percent}% (high)")

        # Load average
        load = os.getloadavg()
        self.add_result("system", "Load average", "info", f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")

        print_subheader("Processes")

        # Check if service is running
        try:
            result = subprocess.run(['systemctl', 'is-active', 'agtrmerkezi'], capture_output=True, text=True)
            if 'active' in result.stdout:
                self.add_result("system", "AGTR service", "ok", "Running")
            else:
                self.add_result("system", "AGTR service", "error", "Not running")
        except:
            pass

        # Check nginx
        try:
            result = subprocess.run(['systemctl', 'is-active', 'nginx'], capture_output=True, text=True)
            if 'active' in result.stdout:
                self.add_result("system", "Nginx", "ok", "Running")
            else:
                self.add_result("system", "Nginx", "warn", "Not running")
        except:
            pass

        # Check MySQL
        try:
            result = subprocess.run(['systemctl', 'is-active', 'mysql'], capture_output=True, text=True)
            status = result.stdout.strip()
            if status == 'active':
                self.add_result("system", "MySQL", "ok", "Running")
            else:
                # Try mariadb
                result = subprocess.run(['systemctl', 'is-active', 'mariadb'], capture_output=True, text=True)
                if 'active' in result.stdout:
                    self.add_result("system", "MariaDB", "ok", "Running")
                else:
                    self.add_result("system", "MySQL/MariaDB", "error", "Not running")
        except:
            pass

        # Check Redis
        try:
            result = subprocess.run(['systemctl', 'is-active', 'redis'], capture_output=True, text=True)
            if 'active' in result.stdout:
                self.add_result("system", "Redis", "ok", "Running")
            else:
                result = subprocess.run(['systemctl', 'is-active', 'redis-server'], capture_output=True, text=True)
                if 'active' in result.stdout:
                    self.add_result("system", "Redis", "ok", "Running")
                else:
                    self.add_result("system", "Redis", "warn", "Not running")
        except:
            pass

    # ==================== 6. DATABASE PERFORMANCE ====================
    def check_database_performance(self):
        print_header("6. DATABASE PERFORMANCE CHECK")

        db = next(get_db())

        try:
            print_subheader("Table Statistics")

            tables = [
                ('users', 10000),
                ('forum_topics', 100000),
                ('forum_replies', 500000),
                ('forum_likes', 1000000),
                ('payments', 100000),
                ('game_servers', 10000),
                ('user_sessions', 50000),
            ]

            for table, warn_threshold in tables:
                try:
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    if count > warn_threshold:
                        self.add_result("db", f"{table} rows", "warn", f"{count:,} (consider archiving)")
                    else:
                        self.add_result("db", f"{table} rows", "info", f"{count:,}")
                except:
                    pass

            print_subheader("Index Usage")

            # Check for missing indexes on foreign keys
            try:
                result = db.execute(text("""
                    SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE kcu
                    LEFT JOIN information_schema.STATISTICS s
                    ON kcu.TABLE_SCHEMA = s.TABLE_SCHEMA
                    AND kcu.TABLE_NAME = s.TABLE_NAME
                    AND kcu.COLUMN_NAME = s.COLUMN_NAME
                    WHERE kcu.TABLE_SCHEMA = 'agtrmerkezi'
                    AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
                    AND s.INDEX_NAME IS NULL
                """)).scalar()

                if result > 0:
                    self.add_result("db", "FK without index", "warn", f"{result} found")
                else:
                    self.add_result("db", "FK indexes", "ok", "All indexed")
            except:
                self.add_result("db", "FK indexes", "skip", "Could not check")

            print_subheader("Connection Pool")

            try:
                result = db.execute(text("SHOW STATUS LIKE 'Threads_connected'")).fetchone()
                connections = int(result[1]) if result else 0

                max_conn = db.execute(text("SHOW VARIABLES LIKE 'max_connections'")).fetchone()
                max_connections = int(max_conn[1]) if max_conn else 151

                conn_percent = (connections / max_connections) * 100
                if conn_percent < 50:
                    self.add_result("db", "DB connections", "ok", f"{connections}/{max_connections}")
                elif conn_percent < 80:
                    self.add_result("db", "DB connections", "warn", f"{connections}/{max_connections}")
                else:
                    self.add_result("db", "DB connections", "error", f"{connections}/{max_connections} (high)")
            except:
                pass

            print_subheader("Query Performance")

            # Slow query check
            try:
                result = db.execute(text("SHOW VARIABLES LIKE 'slow_query_log'")).fetchone()
                if result and result[1] == 'ON':
                    self.add_result("db", "Slow query log", "ok", "Enabled")
                else:
                    self.add_result("db", "Slow query log", "info", "Disabled")
            except:
                pass

        except Exception as e:
            self.add_result("db", "DB performance check", "error", str(e))
        finally:
            db.close()

    # ==================== 7. REDIS CHECK ====================
    def check_redis(self):
        print_header("7. REDIS CHECK")

        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)

            # Ping
            if r.ping():
                self.add_result("redis", "Connection", "ok", "Connected")

            # Memory usage
            info = r.info('memory')
            used_memory_mb = info.get('used_memory', 0) / (1024*1024)
            self.add_result("redis", "Memory usage", "info", f"{used_memory_mb:.1f} MB")

            # Keys count
            keys = r.dbsize()
            self.add_result("redis", "Total keys", "info", f"{keys:,}")

            # Connected clients
            info = r.info('clients')
            clients = info.get('connected_clients', 0)
            self.add_result("redis", "Connected clients", "info", str(clients))

        except ImportError:
            self.add_result("redis", "Redis check", "skip", "redis-py not installed")
        except Exception as e:
            self.add_result("redis", "Redis check", "error", str(e)[:50])

    # ==================== 8. SSL CERTIFICATE ====================
    def check_ssl(self):
        print_header("8. SSL CERTIFICATE CHECK")

        cert_path = "/etc/letsencrypt/live/agtrmerkezi.com/fullchain.pem"

        if os.path.exists(cert_path):
            try:
                result = subprocess.run(
                    ['openssl', 'x509', '-enddate', '-noout', '-in', cert_path],
                    capture_output=True, text=True
                )
                if result.stdout:
                    # Parse date
                    date_str = result.stdout.replace('notAfter=', '').strip()
                    # notAfter=Mar 15 12:00:00 2025 GMT
                    expire_date = datetime.strptime(date_str, '%b %d %H:%M:%S %Y %Z')
                    days_left = (expire_date - datetime.now()).days

                    if days_left > 30:
                        self.add_result("ssl", "Certificate expiry", "ok", f"{days_left} days left")
                    elif days_left > 7:
                        self.add_result("ssl", "Certificate expiry", "warn", f"{days_left} days left")
                    else:
                        self.add_result("ssl", "Certificate expiry", "error", f"{days_left} days left!")
            except Exception as e:
                self.add_result("ssl", "Certificate check", "error", str(e)[:50])
        else:
            self.add_result("ssl", "Certificate", "skip", "Not found at expected path")

    # ==================== 9. BACKUP CHECK ====================
    def check_backups(self):
        print_header("9. BACKUP CHECK")

        backup_dirs = [
            '/var/www/backups',
            '/var/www/agtrmerkezi/backups',
            '/var/www/agtrmerkezi_backup*',
            '/root/backups'
        ]

        found_backups = []
        for pattern in backup_dirs:
            found_backups.extend(glob.glob(pattern))

        if found_backups:
            self.add_result("backup", "Backup directories", "ok", f"{len(found_backups)} found")

            # Check latest backup age (check both directories and .sql files inside)
            latest_time = 0
            for backup_path in found_backups:
                try:
                    # Check the directory/file itself
                    mtime = os.path.getmtime(backup_path)
                    if mtime > latest_time:
                        latest_time = mtime
                    # Also check for .sql files inside directories
                    if os.path.isdir(backup_path):
                        for sql_file in glob.glob(os.path.join(backup_path, '*.sql')):
                            sql_mtime = os.path.getmtime(sql_file)
                            if sql_mtime > latest_time:
                                latest_time = sql_mtime
                except:
                    pass

            if latest_time > 0:
                age_hours = (datetime.now().timestamp() - latest_time) / 3600
                if age_hours < 24:
                    self.add_result("backup", "Latest backup age", "ok", f"{age_hours:.1f} hours")
                elif age_hours < 72:
                    self.add_result("backup", "Latest backup age", "warn", f"{age_hours:.1f} hours")
                else:
                    self.add_result("backup", "Latest backup age", "error", f"{age_hours/24:.1f} days (too old)")
        else:
            self.add_result("backup", "Backup directories", "warn", "None found")

    # ==================== 10. USER ACTIVITY ====================
    def check_user_activity(self):
        print_header("10. USER ACTIVITY CHECK")

        db = next(get_db())

        try:
            print_subheader("Recent Activity")

            # Active users (logged in last 24h)
            result = db.execute(text("""
                SELECT COUNT(*) FROM users WHERE last_login > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """)).scalar()
            self.add_result("activity", "Active users (24h)", "info", str(result))

            # New users (last 7 days)
            result = db.execute(text("""
                SELECT COUNT(*) FROM users WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)).scalar()
            self.add_result("activity", "New users (7d)", "info", str(result))

            # New topics (last 7 days)
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_topics WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)).scalar()
            self.add_result("activity", "New topics (7d)", "info", str(result))

            # New replies (last 7 days)
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_replies WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)).scalar()
            self.add_result("activity", "New replies (7d)", "info", str(result))

            print_subheader("Suspicious Activity")

            # Multiple failed logins
            result = db.execute(text("""
                SELECT COUNT(*) FROM users WHERE login_attempts > 5
            """)).scalar()
            if result > 0:
                self.add_result("activity", "Users with 5+ failed logins", "warn", str(result))
            else:
                self.add_result("activity", "Failed login attempts", "ok", "Normal")

            # Locked accounts
            result = db.execute(text("""
                SELECT COUNT(*) FROM users WHERE lockout_until > NOW()
            """)).scalar()
            if result > 0:
                self.add_result("activity", "Locked accounts", "warn", str(result))
            else:
                self.add_result("activity", "Locked accounts", "ok", "None")

            # Spam detection (too many posts in short time)
            result = db.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT user_id, COUNT(*) as cnt FROM forum_replies
                    WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                    GROUP BY user_id HAVING cnt > 20
                ) x
            """)).scalar()
            if result > 0:
                self.add_result("activity", "Potential spammers", "warn", f"{result} users")
            else:
                self.add_result("activity", "Spam detection", "ok", "No anomalies")

        except Exception as e:
            self.add_result("activity", "Activity check", "error", str(e))
        finally:
            db.close()

    # ==================== 11. FRONTEND BUILD ====================
    def check_frontend(self):
        print_header("11. FRONTEND CHECK")

        dist_path = "/var/www/agtrmerkezi/static/dist"

        if os.path.exists(dist_path):
            # Check build age
            try:
                mtime = os.path.getmtime(dist_path)
                age_hours = (datetime.now().timestamp() - mtime) / 3600
                self.add_result("frontend", "Last build", "info", f"{age_hours:.1f} hours ago")
            except:
                pass

            # Check index.html exists
            if os.path.exists(f"{dist_path}/index.html"):
                self.add_result("frontend", "index.html", "ok", "Exists")
            else:
                self.add_result("frontend", "index.html", "error", "Missing")

            # Check assets
            assets_path = f"{dist_path}/assets"
            if os.path.exists(assets_path):
                js_files = glob.glob(f"{assets_path}/*.js")
                css_files = glob.glob(f"{assets_path}/*.css")
                self.add_result("frontend", "JS bundles", "info", f"{len(js_files)} files")
                self.add_result("frontend", "CSS bundles", "info", f"{len(css_files)} files")
            else:
                self.add_result("frontend", "Assets folder", "error", "Missing")
        else:
            self.add_result("frontend", "Build output", "error", "dist/ not found")

        # Service Worker version
        sw_path = "/var/www/agtrmerkezi/frontend/public/sw.js"
        if os.path.exists(sw_path):
            try:
                with open(sw_path, 'r') as f:
                    content = f.read()
                    match = re.search(r'CACHE_VERSION\s*=\s*(\d+)', content)
                    if match:
                        self.add_result("frontend", "Service Worker version", "info", f"v{match.group(1)}")
            except:
                pass

    # ==================== 12. TIMESTAMP CONSISTENCY ====================
    def check_timestamps(self):
        print_header("12. TIMESTAMP CONSISTENCY CHECK")

        db = next(get_db())

        try:
            # Future timestamps
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_topics WHERE created_at > NOW()
            """)).scalar()
            if result > 0:
                self.add_result("timestamp", "Topics with future dates", "error", str(result))
            else:
                self.add_result("timestamp", "Topic timestamps", "ok", "All valid")

            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_replies WHERE created_at > NOW()
            """)).scalar()
            if result > 0:
                self.add_result("timestamp", "Replies with future dates", "error", str(result))
            else:
                self.add_result("timestamp", "Reply timestamps", "ok", "All valid")

            # Updated before created
            result = db.execute(text("""
                SELECT COUNT(*) FROM forum_topics WHERE updated_at < created_at
            """)).scalar()
            if result > 0:
                self.add_result("timestamp", "Topics updated before created", "warn", str(result))
            else:
                self.add_result("timestamp", "Update consistency", "ok", "All valid")

        except Exception as e:
            self.add_result("timestamp", "Timestamp check", "error", str(e))
        finally:
            db.close()

    # ==================== FIX FUNCTIONS ====================
    def fix_like_counts(self):
        print_header("FIXING LIKE COUNTS")
        db = next(get_db())

        try:
            db.execute(text("""
                UPDATE forum_topics t
                SET likes = (SELECT COUNT(*) FROM forum_likes WHERE content_type = 'topic' AND content_id = t.id)
            """))
            db.execute(text("""
                UPDATE forum_replies r
                SET likes = (SELECT COUNT(*) FROM forum_likes WHERE content_type = 'reply' AND content_id = r.id)
            """))
            db.commit()
            print_ok("Like counts synchronized")
        except Exception as e:
            db.rollback()
            print_error(f"Fix failed: {e}")
        finally:
            db.close()

    def fix_reply_counts(self):
        print_header("FIXING REPLY COUNTS")
        db = next(get_db())

        try:
            db.execute(text("""
                UPDATE forum_topics t
                SET reply_count = (SELECT COUNT(*) FROM forum_replies WHERE topic_id = t.id AND is_active = 1)
            """))
            db.commit()
            print_ok("Reply counts synchronized")
        except Exception as e:
            db.rollback()
            print_error(f"Fix failed: {e}")
        finally:
            db.close()

    def fix_negative_values(self):
        print_header("FIXING NEGATIVE VALUES")
        db = next(get_db())

        try:
            result = db.execute(text("UPDATE forum_topics SET likes = 0 WHERE likes < 0"))
            print_ok(f"Fixed {result.rowcount} topics with negative likes")

            result = db.execute(text("UPDATE forum_replies SET likes = 0 WHERE likes < 0"))
            print_ok(f"Fixed {result.rowcount} replies with negative likes")

            result = db.execute(text("UPDATE forum_topics SET view_count = 0 WHERE view_count < 0"))
            print_ok(f"Fixed {result.rowcount} topics with negative views")

            result = db.execute(text("UPDATE users SET balance_coin = 0 WHERE balance_coin < 0"))
            print_ok(f"Fixed {result.rowcount} users with negative balance")

            db.commit()
        except Exception as e:
            db.rollback()
            print_error(f"Fix failed: {e}")
        finally:
            db.close()

    def fix_orphan_records(self):
        print_header("FIXING ORPHAN RECORDS")
        db = next(get_db())

        try:
            # Delete orphaned likes
            result = db.execute(text("""
                DELETE fl FROM forum_likes fl
                LEFT JOIN forum_topics ft ON fl.content_type = 'topic' AND fl.content_id = ft.id
                LEFT JOIN forum_replies fr ON fl.content_type = 'reply' AND fl.content_id = fr.id
                WHERE ft.id IS NULL AND fr.id IS NULL
            """))
            print_ok(f"Deleted {result.rowcount} orphaned likes")

            db.commit()
        except Exception as e:
            db.rollback()
            print_error(f"Fix failed: {e}")
        finally:
            db.close()

    def clean_expired_sessions(self):
        print_header("CLEANING EXPIRED SESSIONS")
        db = next(get_db())

        try:
            result = db.execute(text("DELETE FROM user_sessions WHERE expires_at < NOW()"))
            print_ok(f"Deleted {result.rowcount} expired sessions")
            db.commit()
        except Exception as e:
            db.rollback()
            print_error(f"Fix failed: {e}")
        finally:
            db.close()

    # ==================== MAIN ====================
    def run_all_checks(self):
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}  AGTR MERKEZI - COMPREHENSIVE HEALTH CHECK v2.0{Colors.RESET}")
        print(f"{Colors.BOLD}  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")

        self.check_model_database_sync()
        self.check_data_integrity()
        self.check_security()
        self.check_api_endpoints()
        self.check_system_resources()
        self.check_database_performance()
        self.check_redis()
        self.check_ssl()
        self.check_backups()
        self.check_user_activity()
        self.check_frontend()
        self.check_timestamps()

        # Summary
        print_header("SUMMARY")
        print(f"\n    Total checks: {self.checks_total}")
        print(f"    {Colors.GREEN}Passed: {self.checks_passed}{Colors.RESET}")
        if self.warnings > 0:
            print(f"    {Colors.YELLOW}Warnings: {self.warnings}{Colors.RESET}")
        if self.errors > 0:
            print(f"    {Colors.RED}Errors: {self.errors}{Colors.RESET}")

        if self.errors == 0 and self.warnings == 0:
            print(f"\n    {Colors.GREEN}{Colors.BOLD}All checks passed!{Colors.RESET}")

        print()
        return 1 if self.errors > 0 else 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description='AGTR Merkezi Comprehensive Health Check v2.0')
    parser.add_argument('--fix-likes', action='store_true', help='Fix like counts')
    parser.add_argument('--fix-replies', action='store_true', help='Fix reply counts')
    parser.add_argument('--fix-negative', action='store_true', help='Fix negative values')
    parser.add_argument('--fix-orphans', action='store_true', help='Fix orphan records')
    parser.add_argument('--clean-sessions', action='store_true', help='Clean expired sessions')
    parser.add_argument('--fix-all', action='store_true', help='Fix all issues')
    parser.add_argument('--quick', action='store_true', help='Quick check (skip slow tests)')

    args = parser.parse_args()

    checker = HealthChecker()

    if args.fix_all:
        checker.fix_like_counts()
        checker.fix_reply_counts()
        checker.fix_negative_values()
        checker.fix_orphan_records()
        checker.clean_expired_sessions()
        print()
    elif args.fix_likes:
        checker.fix_like_counts()
    elif args.fix_replies:
        checker.fix_reply_counts()
    elif args.fix_negative:
        checker.fix_negative_values()
    elif args.fix_orphans:
        checker.fix_orphan_records()
    elif args.clean_sessions:
        checker.clean_expired_sessions()
    else:
        sys.exit(checker.run_all_checks())


if __name__ == "__main__":
    main()
