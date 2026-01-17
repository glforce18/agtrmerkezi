"""
🏆 AGTR Tournament System API
Tournament Management, Brackets, Match Scheduling, ELO Rankings
"""
import json
import math
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.connection import get_db
from app.models.database import User, UserRole

router = APIRouter()

# ============================================================================
# DATABASE TABLES
# ============================================================================

def ensure_tournament_tables(db: Session):
    """Turnuva tablolarını oluştur"""
    try:
        # Turnuvalar
        db.execute(text("""CREATE TABLE IF NOT EXISTS tournaments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE,
            description TEXT,
            game_type VARCHAR(50),
            tournament_type ENUM('single_elimination', 'double_elimination', 'round_robin', 'swiss') DEFAULT 'single_elimination',
            team_size INT DEFAULT 5,
            max_teams INT DEFAULT 16,
            min_teams INT DEFAULT 4,
            prize_pool DECIMAL(10,2) DEFAULT 0,
            prize_distribution JSON,
            entry_fee DECIMAL(10,2) DEFAULT 0,
            rules TEXT,
            banner_url VARCHAR(500),
            status ENUM('draft', 'registration', 'active', 'completed', 'cancelled') DEFAULT 'draft',
            registration_start DATETIME,
            registration_end DATETIME,
            start_date DATETIME,
            end_date DATETIME,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_status (status),
            INDEX idx_game (game_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Turnuva takımları
        db.execute(text("""CREATE TABLE IF NOT EXISTS tournament_teams (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tournament_id INT NOT NULL,
            team_name VARCHAR(100) NOT NULL,
            team_tag VARCHAR(10),
            captain_id INT NOT NULL,
            logo_url VARCHAR(500),
            seed INT,
            status ENUM('pending', 'confirmed', 'checked_in', 'disqualified', 'eliminated') DEFAULT 'pending',
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            points INT DEFAULT 0,
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            checked_in_at DATETIME,
            INDEX idx_tournament (tournament_id),
            INDEX idx_captain (captain_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Takım üyeleri
        db.execute(text("""CREATE TABLE IF NOT EXISTS tournament_team_members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_id INT NOT NULL,
            user_id INT NOT NULL,
            steam_id VARCHAR(50),
            role ENUM('captain', 'player', 'substitute') DEFAULT 'player',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_member (team_id, user_id),
            INDEX idx_team (team_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Maçlar
        db.execute(text("""CREATE TABLE IF NOT EXISTS tournament_matches (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tournament_id INT NOT NULL,
            round_number INT NOT NULL,
            match_number INT NOT NULL,
            bracket_type ENUM('winners', 'losers', 'grand_final') DEFAULT 'winners',
            team1_id INT,
            team2_id INT,
            team1_score INT DEFAULT 0,
            team2_score INT DEFAULT 0,
            winner_id INT,
            loser_id INT,
            best_of INT DEFAULT 1,
            server_id INT,
            server_ip VARCHAR(50),
            server_password VARCHAR(50),
            status ENUM('pending', 'scheduled', 'live', 'completed', 'cancelled') DEFAULT 'pending',
            scheduled_at DATETIME,
            started_at DATETIME,
            completed_at DATETIME,
            notes TEXT,
            INDEX idx_tournament (tournament_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # Maç haritaları
        db.execute(text("""CREATE TABLE IF NOT EXISTS tournament_match_maps (
            id INT AUTO_INCREMENT PRIMARY KEY,
            match_id INT NOT NULL,
            map_number INT NOT NULL,
            map_name VARCHAR(50),
            team1_score INT DEFAULT 0,
            team2_score INT DEFAULT 0,
            winner_id INT,
            picked_by INT,
            status ENUM('pending', 'live', 'completed') DEFAULT 'pending',
            INDEX idx_match (match_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # ELO Rankings
        db.execute(text("""CREATE TABLE IF NOT EXISTS elo_rankings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            game_type VARCHAR(50) NOT NULL,
            elo_rating INT DEFAULT 1000,
            peak_elo INT DEFAULT 1000,
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            draws INT DEFAULT 0,
            win_streak INT DEFAULT 0,
            best_win_streak INT DEFAULT 0,
            last_match_at DATETIME,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_game (user_id, game_type),
            INDEX idx_elo (game_type, elo_rating DESC)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        # ELO geçmişi
        db.execute(text("""CREATE TABLE IF NOT EXISTS elo_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            game_type VARCHAR(50) NOT NULL,
            match_id INT,
            elo_before INT,
            elo_after INT,
            elo_change INT,
            recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user (user_id, game_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""))
        
        db.commit()
    except Exception:
        db.rollback()


# ============================================================================
# TOURNAMENT MANAGEMENT
# ============================================================================

@router.get("/tournaments")
async def list_tournaments(
    status: Optional[str] = None,
    game_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """📋 Turnuva listesi"""
    ensure_tournament_tables(db)
    
    q = "SELECT * FROM tournaments WHERE status != 'draft'"
    p = {}
    
    if status:
        q += " AND status = :status"
        p["status"] = status
    
    if game_type:
        q += " AND game_type = :game"
        p["game"] = game_type
    
    q += " ORDER BY start_date DESC LIMIT 50"
    
    rows = db.execute(text(q), p).fetchall()
    tournaments = [{
        "id": r[0], "name": r[1], "slug": r[2], "description": r[3],
        "game_type": r[4], "tournament_type": r[5], "team_size": r[6],
        "max_teams": r[7], "prize_pool": float(r[9]) if r[9] else 0,
        "status": r[14], "start_date": r[17].isoformat() if r[17] else None,
        "banner_url": r[13]
    } for r in rows]
    
    return {"success": True, "tournaments": tournaments}


@router.post("/tournaments")
async def create_tournament(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Turnuva oluştur"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    ensure_tournament_tables(db)
    
    name = data.get("name", "").strip()
    slug = data.get("slug", name.lower().replace(" ", "-"))
    
    r = db.execute(text("""
        INSERT INTO tournaments (name, slug, description, game_type, tournament_type,
            team_size, max_teams, min_teams, prize_pool, entry_fee, rules, banner_url,
            registration_start, registration_end, start_date, created_by)
        VALUES (:name, :slug, :desc, :game, :ttype, :size, :max, :min, :prize, :fee,
            :rules, :banner, :reg_start, :reg_end, :start, :uid)
    """), {
        "name": name, "slug": slug, "desc": data.get("description"),
        "game": data.get("game_type", "cs16"), "ttype": data.get("tournament_type", "single_elimination"),
        "size": data.get("team_size", 5), "max": data.get("max_teams", 16),
        "min": data.get("min_teams", 4), "prize": data.get("prize_pool", 0),
        "fee": data.get("entry_fee", 0), "rules": data.get("rules"),
        "banner": data.get("banner_url"),
        "reg_start": data.get("registration_start"),
        "reg_end": data.get("registration_end"),
        "start": data.get("start_date"),
        "uid": current_user.id
    })
    db.commit()
    
    return {"success": True, "tournament_id": r.lastrowid, "message": "Turnuva oluşturuldu"}


@router.get("/tournaments/{tournament_id}")
async def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    """🔍 Turnuva detayı"""
    ensure_tournament_tables(db)
    
    t = db.execute(text("SELECT * FROM tournaments WHERE id = :id"), {"id": tournament_id}).fetchone()
    if not t:
        raise HTTPException(404, "Turnuva bulunamadı")
    
    # Takımları al
    teams = db.execute(text("""
        SELECT tt.*, u.username as captain_name FROM tournament_teams tt
        LEFT JOIN users u ON tt.captain_id = u.id
        WHERE tt.tournament_id = :tid ORDER BY tt.seed, tt.registered_at
    """), {"tid": tournament_id}).fetchall()
    
    # Maçları al
    matches = db.execute(text("""
        SELECT m.*, t1.team_name as team1_name, t2.team_name as team2_name
        FROM tournament_matches m
        LEFT JOIN tournament_teams t1 ON m.team1_id = t1.id
        LEFT JOIN tournament_teams t2 ON m.team2_id = t2.id
        WHERE m.tournament_id = :tid
        ORDER BY m.round_number, m.match_number
    """), {"tid": tournament_id}).fetchall()
    
    return {
        "success": True,
        "tournament": {
            "id": t[0], "name": t[1], "slug": t[2], "description": t[3],
            "game_type": t[4], "tournament_type": t[5], "team_size": t[6],
            "max_teams": t[7], "min_teams": t[8], "prize_pool": float(t[9]) if t[9] else 0,
            "prize_distribution": json.loads(t[10]) if t[10] else None,
            "entry_fee": float(t[11]) if t[11] else 0, "rules": t[12],
            "banner_url": t[13], "status": t[14],
            "registration_start": t[15].isoformat() if t[15] else None,
            "registration_end": t[16].isoformat() if t[16] else None,
            "start_date": t[17].isoformat() if t[17] else None
        },
        "teams": [{
            "id": tm[0], "team_name": tm[2], "team_tag": tm[3],
            "captain_name": tm[14], "seed": tm[6], "status": tm[7],
            "wins": tm[8], "losses": tm[9]
        } for tm in teams],
        "matches": [{
            "id": m[0], "round": m[2], "match_number": m[3],
            "team1_id": m[5], "team1_name": m[18], "team1_score": m[7],
            "team2_id": m[6], "team2_name": m[19], "team2_score": m[8],
            "winner_id": m[9], "status": m[15],
            "scheduled_at": m[16].isoformat() if m[16] else None
        } for m in matches]
    }


@router.post("/tournaments/{tournament_id}/status")
async def update_tournament_status(
    tournament_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Turnuva durumunu güncelle"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    new_status = data.get("status")
    
    if new_status == "active":
        # Bracket oluştur
        await generate_bracket(db, tournament_id)
    
    db.execute(text("UPDATE tournaments SET status = :status WHERE id = :id"), 
              {"status": new_status, "id": tournament_id})
    db.commit()
    
    return {"success": True, "message": f"Turnuva durumu: {new_status}"}


# ============================================================================
# TEAM REGISTRATION
# ============================================================================

@router.post("/tournaments/{tournament_id}/register")
async def register_team(
    tournament_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📝 Turnuvaya takım kayıt"""
    ensure_tournament_tables(db)
    
    # Turnuva kontrolü
    tournament = db.execute(text("""
        SELECT status, max_teams, entry_fee, registration_start, registration_end
        FROM tournaments WHERE id = :id
    """), {"id": tournament_id}).fetchone()
    
    if not tournament:
        raise HTTPException(404, "Turnuva bulunamadı")
    
    if tournament[0] != "registration":
        return JSONResponse(status_code=400, content={"success": False, "detail": "Kayıtlar açık değil"})
    
    # Takım sayısı kontrolü
    team_count = db.execute(text("""
        SELECT COUNT(*) FROM tournament_teams WHERE tournament_id = :tid AND status != 'disqualified'
    """), {"tid": tournament_id}).fetchone()[0]
    
    if team_count >= tournament[1]:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Turnuva dolu"})
    
    team_name = data.get("team_name", "").strip()
    team_tag = data.get("team_tag", "").upper().strip()
    
    # Takım oluştur
    r = db.execute(text("""
        INSERT INTO tournament_teams (tournament_id, team_name, team_tag, captain_id)
        VALUES (:tid, :name, :tag, :captain)
    """), {"tid": tournament_id, "name": team_name, "tag": team_tag, "captain": current_user.id})
    team_id = r.lastrowid
    
    # Kaptanı üye olarak ekle
    db.execute(text("""
        INSERT INTO tournament_team_members (team_id, user_id, role)
        VALUES (:tid, :uid, 'captain')
    """), {"tid": team_id, "uid": current_user.id})
    
    db.commit()
    
    return {"success": True, "team_id": team_id, "message": "Takım kaydedildi"}


@router.post("/teams/{team_id}/members")
async def add_team_member(
    team_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """➕ Takıma üye ekle"""
    ensure_tournament_tables(db)
    
    # Kaptan kontrolü
    team = db.execute(text(
        "SELECT captain_id FROM tournament_teams WHERE id = :id"
    ), {"id": team_id}).fetchone()
    
    if not team or team[0] != current_user.id:
        raise HTTPException(403, "Sadece kaptan üye ekleyebilir")
    
    user_id = data.get("user_id")
    role = data.get("role", "player")
    
    try:
        db.execute(text("""
            INSERT INTO tournament_team_members (team_id, user_id, role)
            VALUES (:tid, :uid, :role)
        """), {"tid": team_id, "uid": user_id, "role": role})
        db.commit()
        return {"success": True, "message": "Üye eklendi"}
    except Exception:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Bu üye zaten takımda"})


# ============================================================================
# BRACKET GENERATION
# ============================================================================

async def generate_bracket(db: Session, tournament_id: int):
    """Bracket oluştur"""
    tournament = db.execute(text(
        "SELECT tournament_type, max_teams FROM tournaments WHERE id = :id"
    ), {"id": tournament_id}).fetchone()
    
    teams = db.execute(text("""
        SELECT id FROM tournament_teams 
        WHERE tournament_id = :tid AND status IN ('confirmed', 'checked_in')
        ORDER BY seed, registered_at
    """), {"tid": tournament_id}).fetchall()
    
    team_ids = [t[0] for t in teams]
    
    if tournament[0] == "single_elimination":
        await generate_single_elimination(db, tournament_id, team_ids)
    elif tournament[0] == "double_elimination":
        await generate_double_elimination(db, tournament_id, team_ids)
    elif tournament[0] == "round_robin":
        await generate_round_robin(db, tournament_id, team_ids)


async def generate_single_elimination(db: Session, tournament_id: int, team_ids: list):
    """Single elimination bracket"""
    num_teams = len(team_ids)
    num_rounds = math.ceil(math.log2(num_teams))
    
    # Seed sıralaması
    random.shuffle(team_ids)  # veya seed'e göre sırala
    
    # İlk tur maçları
    match_number = 0
    for i in range(0, num_teams, 2):
        match_number += 1
        team1 = team_ids[i] if i < num_teams else None
        team2 = team_ids[i + 1] if i + 1 < num_teams else None
        
        # Bye durumu
        if team2 is None:
            winner = team1
            status = "completed"
        else:
            winner = None
            status = "pending"
        
        db.execute(text("""
            INSERT INTO tournament_matches (tournament_id, round_number, match_number, 
                team1_id, team2_id, winner_id, status)
            VALUES (:tid, 1, :mn, :t1, :t2, :winner, :status)
        """), {
            "tid": tournament_id, "mn": match_number,
            "t1": team1, "t2": team2, "winner": winner, "status": status
        })
    
    # Sonraki turlar (boş maçlar)
    for round_num in range(2, num_rounds + 1):
        matches_in_round = 2 ** (num_rounds - round_num)
        for mn in range(1, matches_in_round + 1):
            db.execute(text("""
                INSERT INTO tournament_matches (tournament_id, round_number, match_number, status)
                VALUES (:tid, :rn, :mn, 'pending')
            """), {"tid": tournament_id, "rn": round_num, "mn": mn})
    
    db.commit()


async def generate_round_robin(db: Session, tournament_id: int, team_ids: list):
    """Round robin schedule"""
    num_teams = len(team_ids)
    if num_teams % 2 == 1:
        team_ids.append(None)  # Bye
        num_teams += 1
    
    rounds = num_teams - 1
    matches_per_round = num_teams // 2
    
    schedule = team_ids.copy()
    
    for round_num in range(1, rounds + 1):
        for i in range(matches_per_round):
            team1 = schedule[i]
            team2 = schedule[num_teams - 1 - i]
            
            if team1 and team2:
                db.execute(text("""
                    INSERT INTO tournament_matches (tournament_id, round_number, match_number, 
                        team1_id, team2_id, status)
                    VALUES (:tid, :rn, :mn, :t1, :t2, 'pending')
                """), {
                    "tid": tournament_id, "rn": round_num, "mn": i + 1,
                    "t1": team1, "t2": team2
                })
        
        # Rotate
        schedule = [schedule[0]] + [schedule[-1]] + schedule[1:-1]
    
    db.commit()


async def generate_double_elimination(db: Session, tournament_id: int, team_ids: list):
    """Double elimination - önce winners bracket"""
    await generate_single_elimination(db, tournament_id, team_ids)
    # Losers bracket maçları maç sonuçlarına göre oluşturulacak


# ============================================================================
# MATCH MANAGEMENT
# ============================================================================

@router.post("/matches/{match_id}/result")
async def submit_match_result(
    match_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """📊 Maç sonucu gir"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(403, "Yetkiniz yok")
    
    team1_score = data.get("team1_score", 0)
    team2_score = data.get("team2_score", 0)
    
    match = db.execute(text(
        "SELECT team1_id, team2_id, tournament_id, round_number FROM tournament_matches WHERE id = :id"
    ), {"id": match_id}).fetchone()
    
    if not match:
        raise HTTPException(404, "Maç bulunamadı")
    
    # Kazanan belirle
    winner_id = match[0] if team1_score > team2_score else match[1]
    loser_id = match[1] if team1_score > team2_score else match[0]
    
    # Maçı güncelle
    db.execute(text("""
        UPDATE tournament_matches SET 
            team1_score = :s1, team2_score = :s2, winner_id = :winner, loser_id = :loser,
            status = 'completed', completed_at = NOW()
        WHERE id = :id
    """), {"s1": team1_score, "s2": team2_score, "winner": winner_id, "loser": loser_id, "id": match_id})
    
    # Takım istatistiklerini güncelle
    db.execute(text("UPDATE tournament_teams SET wins = wins + 1 WHERE id = :id"), {"id": winner_id})
    db.execute(text("UPDATE tournament_teams SET losses = losses + 1 WHERE id = :id"), {"id": loser_id})
    
    # Sonraki maça kazananı yerleştir
    await advance_winner(db, match[2], match[3], winner_id)
    
    db.commit()
    
    return {"success": True, "winner_id": winner_id, "message": "Sonuç kaydedildi"}


async def advance_winner(db: Session, tournament_id: int, current_round: int, winner_id: int):
    """Kazananı sonraki tura yerleştir"""
    # Sonraki turda boş slot bul
    next_match = db.execute(text("""
        SELECT id, team1_id, team2_id FROM tournament_matches
        WHERE tournament_id = :tid AND round_number = :rn 
        AND (team1_id IS NULL OR team2_id IS NULL)
        LIMIT 1
    """), {"tid": tournament_id, "rn": current_round + 1}).fetchone()
    
    if next_match:
        if next_match[1] is None:
            db.execute(text("UPDATE tournament_matches SET team1_id = :winner WHERE id = :id"),
                      {"winner": winner_id, "id": next_match[0]})
        else:
            db.execute(text("UPDATE tournament_matches SET team2_id = :winner WHERE id = :id"),
                      {"winner": winner_id, "id": next_match[0]})


# ============================================================================
# ELO RANKINGS
# ============================================================================

@router.get("/rankings")
async def get_rankings(
    game_type: str = "cs16",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """🏆 ELO sıralaması"""
    ensure_tournament_tables(db)
    
    rows = db.execute(text("""
        SELECT e.*, u.username, u.avatar_url FROM elo_rankings e
        JOIN users u ON e.user_id = u.id
        WHERE e.game_type = :game
        ORDER BY e.elo_rating DESC
        LIMIT :lim
    """), {"game": game_type, "lim": limit}).fetchall()
    
    rankings = [{
        "rank": idx + 1,
        "user_id": r[1], "username": r[12], "avatar": r[13],
        "elo": r[3], "peak_elo": r[4],
        "wins": r[5], "losses": r[6],
        "win_rate": round(r[5] / max(r[5] + r[6], 1) * 100, 1),
        "win_streak": r[8]
    } for idx, r in enumerate(rows)]
    
    return {"success": True, "rankings": rankings, "game_type": game_type}


@router.get("/rankings/user/{user_id}")
async def get_user_ranking(user_id: int, game_type: str = "cs16", db: Session = Depends(get_db)):
    """🔍 Kullanıcı ELO bilgisi"""
    ensure_tournament_tables(db)
    
    ranking = db.execute(text("""
        SELECT * FROM elo_rankings WHERE user_id = :uid AND game_type = :game
    """), {"uid": user_id, "game": game_type}).fetchone()
    
    if not ranking:
        return {"success": True, "ranking": None}
    
    # Sıralama
    rank = db.execute(text("""
        SELECT COUNT(*) + 1 FROM elo_rankings 
        WHERE game_type = :game AND elo_rating > :elo
    """), {"game": game_type, "elo": ranking[3]}).fetchone()[0]
    
    # Son maçlar
    history = db.execute(text("""
        SELECT * FROM elo_history 
        WHERE user_id = :uid AND game_type = :game
        ORDER BY recorded_at DESC LIMIT 20
    """), {"uid": user_id, "game": game_type}).fetchall()
    
    return {
        "success": True,
        "ranking": {
            "rank": rank,
            "elo": ranking[3], "peak_elo": ranking[4],
            "wins": ranking[5], "losses": ranking[6],
            "win_streak": ranking[8], "best_streak": ranking[9]
        },
        "history": [{
            "elo_before": h[4], "elo_after": h[5], "change": h[6],
            "date": h[7].isoformat() if h[7] else None
        } for h in history]
    }


async def update_elo(db: Session, winner_id: int, loser_id: int, game_type: str, match_id: int = None):
    """ELO güncelle"""
    ensure_tournament_tables(db)
    
    K = 32  # K-factor
    
    # Mevcut ELO'ları al
    winner_elo = db.execute(text("""
        SELECT elo_rating FROM elo_rankings WHERE user_id = :uid AND game_type = :game
    """), {"uid": winner_id, "game": game_type}).fetchone()
    
    loser_elo = db.execute(text("""
        SELECT elo_rating FROM elo_rankings WHERE user_id = :uid AND game_type = :game
    """), {"uid": loser_id, "game": game_type}).fetchone()
    
    winner_rating = winner_elo[0] if winner_elo else 1000
    loser_rating = loser_elo[0] if loser_elo else 1000
    
    # Beklenen skor
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 - expected_winner
    
    # Yeni ELO
    new_winner_elo = round(winner_rating + K * (1 - expected_winner))
    new_loser_elo = round(loser_rating + K * (0 - expected_loser))
    
    # Minimum 100
    new_loser_elo = max(new_loser_elo, 100)
    
    # Güncelle
    for uid, new_elo, old_elo, is_winner in [
        (winner_id, new_winner_elo, winner_rating, True),
        (loser_id, new_loser_elo, loser_rating, False)
    ]:
        # Upsert
        db.execute(text("""
            INSERT INTO elo_rankings (user_id, game_type, elo_rating, peak_elo, wins, losses, win_streak, best_win_streak, last_match_at)
            VALUES (:uid, :game, :elo, :elo, :w, :l, :streak, :streak, NOW())
            ON DUPLICATE KEY UPDATE 
                elo_rating = :elo,
                peak_elo = GREATEST(peak_elo, :elo),
                wins = wins + :w,
                losses = losses + :l,
                win_streak = IF(:is_win, win_streak + 1, 0),
                best_win_streak = GREATEST(best_win_streak, IF(:is_win, win_streak + 1, best_win_streak)),
                last_match_at = NOW()
        """), {
            "uid": uid, "game": game_type, "elo": new_elo,
            "w": 1 if is_winner else 0, "l": 0 if is_winner else 1,
            "streak": 1 if is_winner else 0, "is_win": is_winner
        })
        
        # Geçmiş
        db.execute(text("""
            INSERT INTO elo_history (user_id, game_type, match_id, elo_before, elo_after, elo_change)
            VALUES (:uid, :game, :mid, :before, :after, :change)
        """), {
            "uid": uid, "game": game_type, "mid": match_id,
            "before": old_elo, "after": new_elo, "change": new_elo - old_elo
        })
    
    db.commit()
