"""
AGTR Merkezi - Server Status Synchronization Job
Runs every hour to verify and sync server status between database and real server state
"""

import logging
import subprocess
from datetime import datetime
from typing import Dict, Optional

from app.models.database import GameServer, ServerStatus, get_session_local

logger = logging.getLogger(__name__)


class StatusSyncMetrics:
    """Metrics for status sync job execution"""

    def __init__(self):
        self.total_servers_checked = 0
        self.servers_in_sync = 0
        self.discrepancies_found = 0
        self.auto_corrections = 0
        self.errors = []
        self.discrepancy_details = []

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            "total_servers_checked": self.total_servers_checked,
            "servers_in_sync": self.servers_in_sync,
            "discrepancies_found": self.discrepancies_found,
            "auto_corrections": self.auto_corrections,
            "errors": self.errors,
            "discrepancy_details": self.discrepancy_details,
            "accuracy_rate": (
                f"{(self.servers_in_sync / self.total_servers_checked * 100):.2f}%"
                if self.total_servers_checked > 0
                else "N/A"
            ),
        }


def check_screen_session(screen_name: str) -> bool:
    """
    Check if a screen session exists and is running

    Args:
        screen_name: Screen session name

    Returns:
        True if screen session exists, False otherwise
    """
    try:
        result = subprocess.run(["screen", "-list"], capture_output=True, text=True, timeout=5)

        # Check if screen name appears in output
        return screen_name in result.stdout

    except subprocess.TimeoutExpired:
        logger.warning(f"Screen check timed out for {screen_name}")
        return False
    except Exception as e:
        logger.error(f"Error checking screen session {screen_name}: {e}")
        return False


def check_process_running(pid: Optional[int]) -> bool:
    """
    Check if a process with given PID is running

    Args:
        pid: Process ID

    Returns:
        True if process is running, False otherwise
    """
    if not pid:
        return False

    try:
        # Check if process exists
        result = subprocess.run(["ps", "-p", str(pid)], capture_output=True, timeout=5)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        logger.warning(f"Process check timed out for PID {pid}")
        return False
    except Exception as e:
        logger.error(f"Error checking process {pid}: {e}")
        return False


def query_server_a2s(ip: str, port: int) -> bool:
    """
    Query server via A2S protocol to check if it's responding

    Args:
        ip: Server IP address
        port: Server port

    Returns:
        True if server responds, False otherwise
    """
    try:
        # Try to import python-a2s library
        import a2s

        # Query server info with timeout
        address = (ip, port)
        info = a2s.info(address, timeout=3.0)

        return info is not None

    except ImportError:
        logger.debug("python-a2s not available, using basic check")
        # Fallback: try basic socket connection
        import socket

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3.0)
            sock.connect((ip, port))
            sock.close()
            return True
        except:
            return False

    except Exception as e:
        logger.debug(f"A2S query failed for {ip}:{port}: {e}")
        return False


def get_real_server_status(server: GameServer) -> ServerStatus:
    """
    Determine the real status of a game server

    Checks:
    1. Screen session existence
    2. Process PID (if available)
    3. A2S query response

    Args:
        server: GameServer object

    Returns:
        Actual ServerStatus based on checks
    """
    # Don't check deleted/cancelled servers
    if server.status in [ServerStatus.DELETED, ServerStatus.CANCELLED]:
        return server.status

    # Check screen session
    screen_running = False
    if server.screen_name:
        screen_running = check_screen_session(server.screen_name)

    # Check process
    process_running = False
    if server.process_pid:
        process_running = check_process_running(server.process_pid)

    # Check A2S query
    a2s_responding = False
    if server.ip_address and server.port:
        a2s_responding = query_server_a2s(server.ip_address, server.port)

    # Determine status based on checks
    if screen_running or process_running or a2s_responding:
        return ServerStatus.RUNNING
    else:
        # Server is not running
        # If DB says RUNNING but checks fail, it's STOPPED
        if server.status == ServerStatus.RUNNING:
            return ServerStatus.STOPPED
        else:
            # Keep current status if it's already STOPPED, PENDING, etc.
            return server.status


def sync_server_status():
    """
    Synchronize server status between database and real server state

    This job:
    1. Gets all servers with status RUNNING or STOPPED
    2. Checks real status via screen session + A2S query
    3. Auto-corrects DB status if mismatch detected
    4. Alerts admin if >10 discrepancies found
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("Starting server status synchronization job")
    logger.info(f"Execution time: {start_time}")
    logger.info("=" * 80)

    metrics = StatusSyncMetrics()
    db = None

    try:
        # Get database session
        SessionLocal = get_session_local()
        db = SessionLocal()

        # Get servers to check (only RUNNING and STOPPED)
        servers = (
            db.query(GameServer)
            .filter(GameServer.status.in_([ServerStatus.RUNNING, ServerStatus.STOPPED]))
            .all()
        )

        metrics.total_servers_checked = len(servers)

        logger.info(f"Checking status for {metrics.total_servers_checked} servers")

        # Check each server
        for server in servers:
            try:
                db_status = server.status
                real_status = get_real_server_status(server)

                # Check if status matches
                if db_status == real_status:
                    metrics.servers_in_sync += 1
                    logger.debug(f"Server {server.id} status in sync: {db_status.value}")
                else:
                    # Discrepancy found
                    metrics.discrepancies_found += 1

                    logger.warning(
                        f"⚠ Status mismatch for server {server.id} "
                        f"(name: {server.name}, owner: {server.owner_id}): "
                        f"DB={db_status.value}, Real={real_status.value}"
                    )

                    metrics.discrepancy_details.append(
                        {
                            "server_id": server.id,
                            "server_name": server.name,
                            "db_status": db_status.value,
                            "real_status": real_status.value,
                            "screen_name": server.screen_name,
                            "process_pid": server.process_pid,
                        }
                    )

                    # Auto-correct status
                    server.status = real_status
                    server.last_heartbeat = datetime.now()
                    db.commit()

                    metrics.auto_corrections += 1

                    logger.info(
                        f"✓ Auto-corrected server {server.id} status: "
                        f"{db_status.value} → {real_status.value}"
                    )

                # Update last heartbeat
                server.last_heartbeat = datetime.now()
                db.commit()

            except Exception as e:
                logger.error(f"Error checking server {server.id}: {e}", exc_info=True)
                metrics.errors.append({"server_id": server.id, "error": str(e)})
                db.rollback()

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Log summary
        logger.info("=" * 80)
        logger.info("Status synchronization job completed")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        logger.info("Summary:")
        logger.info(f"  Total checked: {metrics.total_servers_checked}")
        logger.info(f"  ✓ In sync: {metrics.servers_in_sync}")
        logger.info(f"  ⚠ Discrepancies: {metrics.discrepancies_found}")
        logger.info(f"  🔧 Auto-corrected: {metrics.auto_corrections}")
        logger.info(f"  ⚡ Errors: {len(metrics.errors)}")

        if metrics.total_servers_checked > 0:
            accuracy_rate = (metrics.servers_in_sync / metrics.total_servers_checked) * 100
            logger.info(f"  Accuracy rate: {accuracy_rate:.2f}%")

        logger.info("=" * 80)

        # Alert if too many discrepancies
        if metrics.discrepancies_found > 10:
            logger.error(
                f"⚠ WARNING: High number of status discrepancies detected: "
                f"{metrics.discrepancies_found}"
            )
            # TODO: Send admin alert email

        return metrics.to_dict()

    except Exception as e:
        logger.error(f"Fatal error in status sync job: {e}", exc_info=True)
        raise

    finally:
        if db:
            db.close()


def sync_server_status_with_error_handling():
    """
    Wrapper function with error handling for APScheduler

    This ensures the job doesn't crash the scheduler if an error occurs
    """
    try:
        return sync_server_status()
    except Exception as e:
        logger.error(f"Status sync job failed with error: {e}", exc_info=True)
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# For manual testing
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Running status sync job manually...")
    result = sync_server_status()

    print("\n" + "=" * 80)
    print("STATUS SYNC JOB RESULT")
    print("=" * 80)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 80)
