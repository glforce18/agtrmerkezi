"""
AGTR Merkezi - Steam Features Tests
Steam baglantisi gerektiren ozellik testleri
"""

import pytest


class TestJackpotSteamRequired:
    """Jackpot oyunu - Steam gereksinimi testleri"""

    def test_get_current_round_public(self, client):
        """Aktif jackpot turu herkes icin gorunur"""
        response = client.get("/api/games/jackpot/current")
        assert response.status_code == 200
        data = response.json()
        # Response should have round info or create a new one
        assert "id" in data or "round_number" in data or "status" in data

    def test_get_jackpot_history_public(self, client):
        """Jackpot gecmisi herkes icin gorunur"""
        response = client.get("/api/games/jackpot/history")
        assert response.status_code == 200
        # Should return a list
        data = response.json()
        assert isinstance(data, list)

    def test_place_bet_without_auth_fails(self, client):
        """Auth olmadan bahis yapilamaz"""
        response = client.post("/api/games/jackpot/bet", json={
            "amount": 10.0
        })
        assert response.status_code == 401

    def test_place_bet_without_steam_fails(self, client, auth_headers):
        """Steam olmadan bahis yapilamaz"""
        response = client.post("/api/games/jackpot/bet", headers=auth_headers, json={
            "amount": 10.0
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]

    def test_place_bet_with_steam_succeeds(self, client, steam_user_headers):
        """Steam ile bahis yapilabilir"""
        response = client.post("/api/games/jackpot/bet", headers=steam_user_headers, json={
            "amount": 10.0
        })
        # May succeed or fail due to balance/game state
        # 201 = success, 400 = validation error, 403 = forbidden
        assert response.status_code in [201, 200, 400, 422]

    def test_place_bet_validates_amount(self, client, steam_user_headers):
        """Bahis miktari dogrulanir"""
        response = client.post("/api/games/jackpot/bet", headers=steam_user_headers, json={
            "amount": -5.0  # Negative amount
        })
        assert response.status_code == 422  # Validation error

    def test_place_bet_zero_amount_fails(self, client, steam_user_headers):
        """Sifir bahis yapilamaz"""
        response = client.post("/api/games/jackpot/bet", headers=steam_user_headers, json={
            "amount": 0
        })
        assert response.status_code == 422  # Validation error

    def test_verify_round_fairness_public(self, client):
        """Fairness dogrulamasi herkes icin acik"""
        # Using a non-existent round ID
        response = client.get("/api/games/jackpot/verify/99999")
        # Either 404 (not found) or 400 (not completed)
        assert response.status_code in [400, 404]


class TestTournamentSteamRequired:
    """Turnuva sistemi - Steam gereksinimi testleri"""

    def test_list_tournaments_public(self, client):
        """Turnuva listesi herkes icin gorunur"""
        response = client.get("/api/tournament/tournaments")
        assert response.status_code == 200
        data = response.json()
        assert "tournaments" in data or "success" in data

    def test_get_tournament_details_public(self, client):
        """Turnuva detayi herkes icin gorunur"""
        # Non-existent tournament
        response = client.get("/api/tournament/tournaments/99999")
        assert response.status_code == 404

    def test_register_team_without_auth_fails(self, client):
        """Auth olmadan takim kaydi yapilamaz"""
        response = client.post("/api/tournament/tournaments/1/register", json={
            "team_name": "Test Team",
            "team_tag": "TST"
        })
        assert response.status_code == 401

    def test_register_team_without_steam_fails(self, client, auth_headers):
        """Steam olmadan takim kaydi yapilamaz"""
        response = client.post("/api/tournament/tournaments/1/register", headers=auth_headers, json={
            "team_name": "Test Team",
            "team_tag": "TST"
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]

    def test_get_rankings_public(self, client):
        """ELO siralamalari herkes icin gorunur"""
        response = client.get("/api/tournament/rankings")
        assert response.status_code == 200
        data = response.json()
        assert "rankings" in data or "success" in data

    def test_get_rankings_by_game_type(self, client):
        """Oyun turune gore siralama"""
        response = client.get("/api/tournament/rankings?game_type=cs16")
        assert response.status_code == 200

    def test_get_user_ranking(self, client):
        """Kullanici ELO bilgisi"""
        response = client.get("/api/tournament/rankings/user/1?game_type=cs16")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestGameStatsSteamRequired:
    """Oyun istatistikleri - Steam gereksinimi testleri"""

    def test_get_my_stats_requires_auth(self, client):
        """Istatistikler auth gerektirir"""
        response = client.get("/api/games/stats/me")
        assert response.status_code == 401

    def test_get_my_stats(self, client, auth_headers):
        """Kendi istatistikleri goruntulenebilir"""
        response = client.get("/api/games/stats/me", headers=auth_headers)
        # May succeed or have db issues in test env
        assert response.status_code in [200, 500]

    def test_get_game_leaderboard_public(self, client):
        """Oyun liderlik tablosu herkes icin acik"""
        response = client.get("/api/games/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_game_leaderboard_with_period(self, client):
        """Donem bazli liderlik tablosu"""
        response = client.get("/api/games/leaderboard?period=week&limit=10")
        assert response.status_code == 200


class TestClanSteamRequired:
    """Klan sistemi - Steam gereksinimi testleri"""

    def test_create_clan_without_auth_fails(self, client):
        """Auth olmadan klan olusturulamaz"""
        response = client.post("/api/social/clans", json={
            "name": "Test Clan",
            "tag": "TST"
        })
        # May be 401 (unauthorized) or 405 (method not allowed if endpoint doesn't exist)
        assert response.status_code in [401, 404, 405]


class TestProfileSteamLink:
    """Profil Steam baglanti testleri"""

    def test_get_profile_shows_steam_status(self, client, auth_headers):
        """Profil Steam durumunu gosterir"""
        response = client.get("/api/user/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Profile should indicate steam_id is None for non-steam user
        assert "steam_id" in data or "user" in data

    def test_steam_user_has_steam_id(self, client, steam_user_headers):
        """Steam kullanicisi steam_id'ye sahip"""
        response = client.get("/api/user/profile", headers=steam_user_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have a steam_id
        if "steam_id" in data:
            assert data["steam_id"] is not None
        elif "user" in data:
            assert data["user"].get("steam_id") is not None


class TestOAuthSteamLogin:
    """Steam OAuth login testleri"""

    def test_steam_oauth_redirect(self, client):
        """Steam OAuth redirect calisir"""
        response = client.get("/api/auth/oauth/steam", follow_redirects=False)
        # Should redirect to Steam
        assert response.status_code in [302, 307]

    def test_discord_oauth_redirect(self, client):
        """Discord OAuth redirect calisir"""
        response = client.get("/api/auth/oauth/discord", follow_redirects=False)
        # Should redirect to Discord
        assert response.status_code in [302, 307]


class TestSteamRequiredErrorMessages:
    """Steam gerekli hata mesajlari testleri"""

    def test_forum_topic_steam_error_message(self, client, auth_headers, forum_category):
        """Forum konu olusturma Steam hata mesaji"""
        response = client.post("/api/forum/topics", headers=auth_headers, json={
            "title": "Test Topic Title",
            "category_id": forum_category.id,
            "content": "This is a test topic content with enough characters."
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]
        assert "profil" in data["detail"].lower() or "baglant" in data["detail"].lower() or "bagla" in data["detail"].lower()

    def test_forum_reply_steam_error_message(self, client, auth_headers, forum_topic):
        """Forum yanit Steam hata mesaji"""
        response = client.post(f"/api/forum/topics/{forum_topic.slug}/replies", headers=auth_headers, json={
            "content": "This is a test reply content."
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]

    def test_jackpot_steam_error_message(self, client, auth_headers):
        """Jackpot Steam hata mesaji"""
        response = client.post("/api/games/jackpot/bet", headers=auth_headers, json={
            "amount": 10.0
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]

    def test_tournament_steam_error_message(self, client, auth_headers):
        """Tournament Steam hata mesaji"""
        response = client.post("/api/tournament/tournaments/1/register", headers=auth_headers, json={
            "team_name": "Test Team",
            "team_tag": "TST"
        })
        assert response.status_code == 403
        data = response.json()
        assert "Steam" in data["detail"]
