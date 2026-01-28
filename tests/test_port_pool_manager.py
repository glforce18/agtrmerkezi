"""
AGTR Merkezi - Port Pool Manager Tests
Unit tests for IP:PORT allocation with load balancing
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session

from app.services.port_pool_manager import PortPoolManager


class TestPortPoolManager:
    """Test suite for PortPoolManager"""

    def test_acquire_slot_empty_pool(self, db_session: Session):
        """Test acquiring slot when pool is completely empty"""
        pool_manager = PortPoolManager(db_session)

        # Mock database to return no servers
        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = []

            slot = pool_manager.acquire_slot()

            assert slot is not None
            ip, port = slot
            assert ip in pool_manager.AVAILABLE_IPS
            assert pool_manager.PORT_RANGE_START <= port <= pool_manager.PORT_RANGE_END

    def test_acquire_slot_load_balancing(self, db_session: Session):
        """Test that slots are distributed evenly across IPs"""
        pool_manager = PortPoolManager(db_session)

        # Create mock servers: IP1 has 10 servers, IP2 has 5, IP3 has 0
        with patch.object(pool_manager, "_get_ip_loads") as mock_get_loads:
            mock_get_loads.return_value = {
                "185.171.25.138": 10,
                "185.171.25.139": 5,
                "185.171.25.140": 0,  # This should be selected
            }

            with patch.object(pool_manager, "_find_available_port") as mock_find_port:
                mock_find_port.return_value = 27018

                slot = pool_manager.acquire_slot()

                assert slot is not None
                ip, port = slot
                # Should select IP with least servers (140)
                assert ip == "185.171.25.140"
                assert port == 27018

    def test_acquire_slot_all_full(self, db_session: Session):
        """Test behavior when all 150 slots are occupied"""
        pool_manager = PortPoolManager(db_session)

        # Mock all IPs as full
        with patch.object(pool_manager, "_find_available_port") as mock_find_port:
            mock_find_port.return_value = None  # No ports available

            slot = pool_manager.acquire_slot()

            assert slot is None

    def test_find_available_port_success(self, db_session: Session):
        """Test finding available port on specific IP"""
        pool_manager = PortPoolManager(db_session)

        # Mock used ports: 27018, 27019, 27020
        used_ports = [(27018,), (27019,), (27020,)]

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = used_ports

            port = pool_manager._find_available_port("185.171.25.138")

            # Should return first available port (27021)
            assert port == 27021

    def test_find_available_port_all_used(self, db_session: Session):
        """Test when all ports on IP are used"""
        pool_manager = PortPoolManager(db_session)

        # Mock all 50 ports as used
        used_ports = [(port,) for port in range(27018, 27068)]

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.all.return_value = used_ports

            port = pool_manager._find_available_port("185.171.25.138")

            assert port is None

    def test_get_ip_loads(self, db_session: Session):
        """Test IP load calculation"""
        pool_manager = PortPoolManager(db_session)

        # Mock server counts
        mock_result = [("185.171.25.138", 15), ("185.171.25.139", 20), ("185.171.25.140", 10)]

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = (
                mock_result
            )

            loads = pool_manager._get_ip_loads()

            assert loads["185.171.25.138"] == 15
            assert loads["185.171.25.139"] == 20
            assert loads["185.171.25.140"] == 10

    def test_get_ip_loads_empty(self, db_session: Session):
        """Test IP load when no servers exist"""
        pool_manager = PortPoolManager(db_session)

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.group_by.return_value.all.return_value = []

            loads = pool_manager._get_ip_loads()

            # All IPs should have 0 load
            assert all(count == 0 for count in loads.values())
            assert len(loads) == 3

    def test_get_capacity_info(self, db_session: Session):
        """Test capacity information calculation"""
        pool_manager = PortPoolManager(db_session)

        with patch.object(pool_manager, "_get_ip_loads") as mock_get_loads:
            mock_get_loads.return_value = {
                "185.171.25.138": 30,
                "185.171.25.139": 40,
                "185.171.25.140": 20,
            }

            capacity = pool_manager.get_capacity_info()

            assert capacity["total_slots"] == 150
            assert capacity["used_slots"] == 90
            assert capacity["available_slots"] == 60
            assert capacity["utilization_percent"] == 60.0
            assert len(capacity["ip_breakdown"]) == 3

    def test_mysql_lock_acquire_success(self, db_session: Session):
        """Test MySQL named lock acquisition"""
        pool_manager = PortPoolManager(db_session)

        # Mock successful lock acquisition
        mock_result = Mock()
        mock_result.scalar.return_value = 1  # Lock acquired

        with patch.object(db_session, "execute", return_value=mock_result):
            # Should not raise exception
            pool_manager._acquire_lock()

    def test_mysql_lock_acquire_failure(self, db_session: Session):
        """Test MySQL named lock acquisition failure"""
        pool_manager = PortPoolManager(db_session)

        # Mock failed lock acquisition
        mock_result = Mock()
        mock_result.scalar.return_value = 0  # Lock failed

        with patch.object(db_session, "execute", return_value=mock_result):
            with pytest.raises(Exception, match="Failed to acquire port pool lock"):
                pool_manager._acquire_lock()

    def test_mysql_lock_release(self, db_session: Session):
        """Test MySQL named lock release"""
        pool_manager = PortPoolManager(db_session)

        with patch.object(db_session, "execute") as mock_execute:
            pool_manager._release_lock()

            # Verify RELEASE_LOCK was called
            mock_execute.assert_called_once()

    def test_acquire_slot_atomicity(self, db_session: Session):
        """Test that acquire_slot properly acquires and releases lock"""
        pool_manager = PortPoolManager(db_session)

        with patch.object(pool_manager, "_acquire_lock") as mock_acquire, patch.object(
            pool_manager, "_release_lock"
        ) as mock_release, patch.object(pool_manager, "_get_ip_loads") as mock_loads, patch.object(
            pool_manager, "_find_available_port"
        ) as mock_find:

            mock_loads.return_value = {
                "185.171.25.138": 0,
                "185.171.25.139": 0,
                "185.171.25.140": 0,
            }
            mock_find.return_value = 27018

            slot = pool_manager.acquire_slot()

            # Verify lock was acquired and released
            mock_acquire.assert_called_once()
            mock_release.assert_called_once()
            assert slot is not None


@pytest.fixture
def db_session():
    """Mock database session for testing"""
    return Mock(spec=Session)


# Integration test markers (requires real database)
@pytest.mark.integration
class TestPortPoolManagerIntegration:
    """Integration tests with real database"""

    def test_concurrent_allocations(self, real_db_session):
        """Test concurrent slot allocations don't create duplicates"""
        # This would test with actual threading/multiprocessing
        # and verify no duplicate (IP, port) pairs are allocated
        pytest.skip("Requires real database and threading setup")

    def test_slot_recycling(self, real_db_session):
        """Test that DELETED/EXPIRED servers free up slots"""
        pytest.skip("Requires real database setup")
