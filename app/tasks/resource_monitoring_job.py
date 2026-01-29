"""
AGTR Merkezi - Resource Monitoring Background Job
Runs every 5 minutes to monitor CPU/RAM usage and handle crashes
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import psutil
from sqlalchemy.orm import Session

from app.models.database import (
    GameServer,
    ServerMetrics,
    ServerStatus,
    get_session_local,
)

logger = logging.getLogger(__name__)


class ResourceMonitoringMetrics:
    """Metrics for resource monitoring job execution"""

    def __init__(self):
        self.total_servers_checked = 0
        self.high_cpu_alerts = 0
        self.high_ram_alerts = 0
        self.crashes_detected = 0
        self.auto_restarts = 0
        self.errors = []
        self.resource_details = []

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            "total_servers_checked": self.total_servers_checked,
            "high_cpu_alerts": self.high_cpu_alerts,
            "high_ram_alerts": self.high_ram_alerts,
            "crashes_detected": self.crashes_detected,
            "auto_restarts": self.auto_restarts,
            "errors": self.errors,
            "resource_details": self.resource_details,
        }


def get_process_resources(pid: int) -> Optional[Dict[str, float]]:
    """
    Get CPU and RAM usage for a process

    Args:
        pid: Process ID

    Returns:
        Dict with cpu_percent and ram_mb, or None if process not found
    """
    try:
        process = psutil.Process(pid)

        # Get CPU percent (interval for accurate measurement)
        cpu_percent = process.cpu_percent(interval=1.0)

        # Get memory info
        mem_info = process.memory_info()
        ram_mb = mem_info.rss / (1024 * 1024)  # Convert bytes to MB

        return {
            "cpu_percent": cpu_percent,
            "ram_mb": ram_mb,
        }

    except psutil.NoSuchProcess:
        logger.debug(f"Process {pid} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting resources for PID {pid}: {e}")
        return None


def restart_server(server: GameServer, db: Session) -> bool:
    """
    Restart a game server

    Args:
        server: GameServer object
        db: Database session

    Returns:
        True if restart successful, False otherwise
    """
    try:
        # Import server control service
        from app.services.server_control import ServerControlService

        control_service = ServerControlService(db)

        # Stop server first
        control_service.stop_server(server.id, server.owner_id)

        # Wait a moment
        import time

        time.sleep(2)

        # Start server
        control_service.start_server(server.id, server.owner_id)

        logger.info(f"Server {server.id} restarted successfully")
        return True

    except Exception as e:
        logger.error(f"Error restarting server {server.id}: {e}", exc_info=True)
        return False


def monitor_server_resources():
    """
    Monitor server resources and handle high usage / crashes

    This job:
    1. Gets CPU/RAM usage for all running servers
    2. Stores metrics in ServerMetrics table
    3. Alerts on high usage (>90% for 15+ minutes)
    4. Detects crashes and auto-restarts if enabled
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("Starting resource monitoring job")
    logger.info(f"Execution time: {start_time}")
    logger.info("=" * 80)

    metrics = ResourceMonitoringMetrics()
    db = None

    try:
        # Get database session
        SessionLocal = get_session_local()
        db = SessionLocal()

        # Get all running servers
        servers = db.query(GameServer).filter(GameServer.status == ServerStatus.RUNNING).all()

        metrics.total_servers_checked = len(servers)

        logger.info(f"Monitoring resources for {metrics.total_servers_checked} running servers")

        # Monitor each server
        for server in servers:
            try:
                # Skip if no PID
                if not server.process_pid:
                    logger.debug(f"Server {server.id} has no PID, skipping")
                    continue

                # Get process resources
                resources = get_process_resources(server.process_pid)

                if resources:
                    cpu_percent = resources["cpu_percent"]
                    ram_mb = resources["ram_mb"]

                    # Log resources
                    logger.debug(
                        f"Server {server.id} resources: CPU={cpu_percent:.1f}%, RAM={ram_mb:.1f}MB"
                    )

                    # Store metrics in database
                    try:
                        server_metric = ServerMetrics(
                            server_id=server.id,
                            cpu_usage=cpu_percent,
                            ram_usage=ram_mb,
                            player_count=server.current_players or 0,
                            timestamp=datetime.now(),
                        )
                        db.add(server_metric)
                        db.commit()
                    except Exception as e:
                        logger.error(f"Error storing metrics for server {server.id}: {e}")
                        db.rollback()

                    # Check for high CPU usage
                    if cpu_percent > 90:
                        metrics.high_cpu_alerts += 1

                        # Check if high for 15+ minutes
                        fifteen_min_ago = datetime.now() - timedelta(minutes=15)
                        high_cpu_count = (
                            db.query(ServerMetrics)
                            .filter(
                                ServerMetrics.server_id == server.id,
                                ServerMetrics.timestamp >= fifteen_min_ago,
                                ServerMetrics.cpu_usage > 90,
                            )
                            .count()
                        )

                        if high_cpu_count >= 3:  # At least 3 samples in 15 min (5min interval)
                            logger.warning(
                                f"⚠ Server {server.id} has high CPU usage (>{cpu_percent:.1f}%) "
                                f"for 15+ minutes"
                            )

                            metrics.resource_details.append(
                                {
                                    "server_id": server.id,
                                    "server_name": server.name,
                                    "alert_type": "high_cpu",
                                    "cpu_percent": cpu_percent,
                                    "duration": "15+ minutes",
                                }
                            )

                            # TODO: Send alert to server owner
                            # notification_service.send_high_cpu_alert(server)

                    # Check for high RAM usage
                    if ram_mb > 500:  # Over 500MB
                        metrics.high_ram_alerts += 1

                        logger.warning(f"⚠ Server {server.id} has high RAM usage ({ram_mb:.1f}MB)")

                        metrics.resource_details.append(
                            {
                                "server_id": server.id,
                                "server_name": server.name,
                                "alert_type": "high_ram",
                                "ram_mb": ram_mb,
                            }
                        )

                        # TODO: Send alert to server owner
                        # notification_service.send_high_ram_alert(server)

                else:
                    # Process not found - possible crash
                    logger.warning(
                        f"⚠ Server {server.id} process not found (PID: {server.process_pid}). "
                        f"Possible crash detected."
                    )

                    metrics.crashes_detected += 1

                    # Increment crash count
                    server.crash_count = (server.crash_count or 0) + 1
                    server.last_crash = datetime.now()

                    # Update status to STOPPED
                    server.status = ServerStatus.STOPPED
                    server.process_pid = None

                    db.commit()

                    logger.info(
                        f"Server {server.id} marked as STOPPED. "
                        f"Total crashes: {server.crash_count}"
                    )

                    # Auto-restart if enabled
                    if server.auto_restart:
                        # Check if in backoff period
                        if (
                            server.restart_backoff_until
                            and server.restart_backoff_until > datetime.now()
                        ):
                            logger.info(
                                f"Server {server.id} in restart backoff until "
                                f"{server.restart_backoff_until}, skipping auto-restart"
                            )
                        else:
                            logger.info(f"Attempting auto-restart for server {server.id}")

                            if restart_server(server, db):
                                metrics.auto_restarts += 1
                                logger.info(f"✓ Server {server.id} auto-restarted successfully")

                                # Set exponential backoff (if crashes continue)
                                if server.crash_count >= 3:
                                    # 2^crash_count minutes backoff
                                    backoff_minutes = 2 ** min(server.crash_count, 6)  # Max 64 min
                                    server.restart_backoff_until = datetime.now() + timedelta(
                                        minutes=backoff_minutes
                                    )
                                    logger.info(
                                        f"Server {server.id} backoff set to {backoff_minutes} minutes"
                                    )
                                    db.commit()
                            else:
                                logger.error(f"✗ Failed to auto-restart server {server.id}")

                    # Send crash notification after 3+ crashes
                    if server.crash_count >= 3:
                        logger.error(
                            f"⚠ Server {server.id} has crashed {server.crash_count} times. "
                            f"Owner should be notified."
                        )
                        # TODO: Send crash alert to server owner
                        # notification_service.send_crash_alert(server)

            except Exception as e:
                logger.error(f"Error monitoring server {server.id}: {e}", exc_info=True)
                metrics.errors.append({"server_id": server.id, "error": str(e)})

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Log summary
        logger.info("=" * 80)
        logger.info("Resource monitoring job completed")
        logger.info(f"Execution time: {execution_time:.2f} seconds")
        logger.info("Summary:")
        logger.info(f"  Total checked: {metrics.total_servers_checked}")
        logger.info(f"  ⚠ High CPU alerts: {metrics.high_cpu_alerts}")
        logger.info(f"  ⚠ High RAM alerts: {metrics.high_ram_alerts}")
        logger.info(f"  💥 Crashes detected: {metrics.crashes_detected}")
        logger.info(f"  🔄 Auto-restarts: {metrics.auto_restarts}")
        logger.info(f"  ⚡ Errors: {len(metrics.errors)}")
        logger.info("=" * 80)

        return metrics.to_dict()

    except Exception as e:
        logger.error(f"Fatal error in resource monitoring job: {e}", exc_info=True)
        raise

    finally:
        if db:
            db.close()


def monitor_server_resources_with_error_handling():
    """
    Wrapper function with error handling for APScheduler

    This ensures the job doesn't crash the scheduler if an error occurs
    """
    try:
        return monitor_server_resources()
    except Exception as e:
        logger.error(f"Resource monitoring job failed with error: {e}", exc_info=True)
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


# For manual testing
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Running resource monitoring job manually...")
    result = monitor_server_resources()

    print("\n" + "=" * 80)
    print("RESOURCE MONITORING JOB RESULT")
    print("=" * 80)
    for key, value in result.items():
        print(f"{key}: {value}")
    print("=" * 80)
