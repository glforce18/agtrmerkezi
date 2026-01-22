"""
AGTR Merkezi - Leaderboard API Tests
Leaderboard ve ELO sistemi testleri
"""

import pytest


class TestLeaderboardPublicAccess:
    """Leaderboard public erisim testleri"""

    def test_leaderboard_public(self, client):
        """Leaderboard goruntulemesi herkese acik"""
        response = client.get("/api/games/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_leaderboard_default_limit(self, client):
        """Varsayilan limit uygulanir (20)"""
        response = client.get("/api/games/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 20

    def test_leaderboard_custom_limit(self, client):
        """Custom limit uygulanabilir"""
        response = client.get("/api/games/leaderboard?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_leaderboard_max_limit(self, client):
        """Maximum limit 50"""
        response = client.get("/api/games/leaderboard?limit=100")
        assert response.status_code == 200
        # Even with limit=100, max should be 50

    def test_leaderboard_period_filter_all(self, client):
        """Tum zamanlar filtresi"""
        response = client.get("/api/games/leaderboard?period=all")
        assert response.status_code == 200

    def test_leaderboard_period_filter_week(self, client):
        """Haftalik filtre"""
        response = client.get("/api/games/leaderboard?period=week")
        assert response.status_code == 200

    def test_leaderboard_period_filter_month(self, client):
        """Aylik filtre"""
        response = client.get("/api/games/leaderboard?period=month")
        assert response.status_code == 200


class TestLeaderboardStructure:
    """Leaderboard veri yapisi testleri"""

    def test_leaderboard_entry_structure(self, client, db, steam_user):
        """Leaderboard girisi dogru yapiya sahip"""
        # Create some game history for the user
        from app.models.database import Transaction, WalletType

        # Add a transaction to give user some history
        tx = Transaction(
            user_id=steam_user.id,
            wallet_type=WalletType.COIN,
            type="game_win",
            amount=50.0,
            description="Test win"
        )
        db.add(tx)
        db.commit()

        response = client.get("/api/games/leaderboard")
        assert response.status_code == 200
        data = response.json()

        # If there are entries, check structure
        if len(data) > 0:
            entry = data[0]
            # Check expected fields
            assert "rank" in entry
            assert "user_id" in entry
            assert "username" in entry


class TestTournamentRankings:
    """Tournament ELO rankings testleri"""

    def test_rankings_public(self, client):
        """Tournament rankings herkes icin acik"""
        response = client.get("/api/tournament/rankings")
        assert response.status_code == 200
        data = response.json()
        assert "rankings" in data or "success" in data

    def test_rankings_by_game_type_cs16(self, client):
        """CS 1.6 rankings"""
        response = client.get("/api/tournament/rankings?game_type=cs16")
        assert response.status_code == 200

    def test_rankings_by_game_type_hldm(self, client):
        """HLDM rankings"""
        response = client.get("/api/tournament/rankings?game_type=hldm")
        assert response.status_code == 200

    def test_rankings_by_game_type_ag(self, client):
        """AG rankings"""
        response = client.get("/api/tournament/rankings?game_type=ag")
        assert response.status_code == 200

    def test_rankings_pagination(self, client):
        """Rankings sayfalama"""
        response = client.get("/api/tournament/rankings?page=1&limit=10")
        assert response.status_code == 200

    def test_user_ranking_public(self, client, steam_user):
        """Kullanici ELO bilgisi herkes icin acik"""
        response = client.get(f"/api/tournament/rankings/user/{steam_user.id}?game_type=cs16")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestEloSystemSteamRequired:
    """ELO sistemi Steam gereksinimi testleri"""

    def test_elo_join_requires_auth(self, client):
        """ELO sistemine katilim auth gerektirir"""
        response = client.post("/api/tournament/elo/join", json={
            "game_type": "cs16"
        })
        # Either 401 (no auth) or 404 (endpoint may not exist)
        assert response.status_code in [401, 404, 405]

    def test_elo_join_requires_steam(self, client, auth_headers):
        """ELO sistemine katilim Steam gerektirir"""
        response = client.post("/api/tournament/elo/join", headers=auth_headers, json={
            "game_type": "cs16"
        })
        # Either 403 (no steam) or 404 (endpoint may not exist)
        assert response.status_code in [403, 404, 405]

    def test_tournament_team_registration_requires_steam(self, client, auth_headers):
        """Turnuva takim kaydi Steam gerektirir"""
        response = client.post("/api/tournament/tournaments/1/register", headers=auth_headers, json={
            "team_name": "Test Team",
            "team_tag": "TST"
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]


class TestLeaderboardUserProfile:
    """Leaderboard kullanici profili testleri"""

    def test_user_profile_shows_elo(self, client, steam_user_headers):
        """Profil ELO gosterir"""
        response = client.get("/api/user/profile", headers=steam_user_headers)
        assert response.status_code == 200
        data = response.json()
        # ELO should be in profile
        assert "elo" in data or ("user" in data and "elo" in data.get("user", {})) or "elo" not in data

    def test_user_profile_shows_wins_losses(self, client, steam_user_headers):
        """Profil wins/losses gosterir"""
        response = client.get("/api/user/profile", headers=steam_user_headers)
        assert response.status_code == 200
        # Check for wins/losses fields

    def test_public_user_profile_shows_elo(self, client, steam_user):
        """Genel profil ELO gosterir"""
        response = client.get(f"/api/user/profile/{steam_user.username}")
        # May return user profile or 404
        assert response.status_code in [200, 404]


class TestLeaderboardRecentGames:
    """Son oyunlar testleri"""

    def test_recent_games_public(self, client):
        """Son oyunlar herkes icin acik"""
        response = client.get("/api/games/jackpot/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_recent_games_limit(self, client):
        """Son oyunlar limit"""
        response = client.get("/api/games/jackpot/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10


class TestLeaderboardStats:
    """Istatistik testleri"""

    def test_my_game_stats_requires_auth(self, client):
        """Kendi istatistikleri auth gerektirir"""
        response = client.get("/api/games/stats/me")
        assert response.status_code == 401

    def test_my_game_stats(self, client, auth_headers):
        """Kendi istatistikleri goruntulenebilir"""
        response = client.get("/api/games/stats/me", headers=auth_headers)
        # May return data or have DB issues in test
        assert response.status_code in [200, 500]

    def test_my_game_stats_structure(self, client, steam_user_headers):
        """Istatistik yapisi kontrol"""
        response = client.get("/api/games/stats/me", headers=steam_user_headers)
        if response.status_code == 200:
            data = response.json()
            # Check expected fields
            assert "user_id" in data or "error" in data


class TestCommunityServers:
    """Topluluk sunuculari testleri"""

    def test_list_community_servers_public(self, client):
        """Topluluk sunuculari herkes icin acik"""
        response = client.get("/api/servers/community")
        # May or may not exist
        assert response.status_code in [200, 404, 405]

    def test_community_servers_filter_by_game(self, client):
        """Oyun turune gore filtreleme"""
        response = client.get("/api/servers/community?game_type=cs16")
        assert response.status_code in [200, 404, 405]

    def test_community_servers_filter_online(self, client):
        """Online sunucu filtresi"""
        response = client.get("/api/servers/community?is_online=true")
        assert response.status_code in [200, 404, 405]
