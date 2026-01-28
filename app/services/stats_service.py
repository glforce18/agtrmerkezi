"""
AGTR Merkezi v6.0 - Stats Service
Gelismis istatistik servisi ve veri agregasyonu
"""

import csv
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from io import StringIO
from typing import Dict, List


from app.models.connection import SessionLocal
from app.models.database import (
    PlayerSession,
    ServerStatsDaily,
    ServerStatsHourly,
    ServerStatsWeekly,
)

logger = logging.getLogger(__name__)


class StatsService:
    """
    Sunucu istatistik servisi

    Saatlik, gunluk, haftalik istatistikler ve oyuncu analizleri
    """

    def get_hourly_stats(self, server_id: int, hours: int = 24) -> List[Dict]:
        """
        Saatlik istatistikleri getir

        Args:
            server_id: Sunucu ID
            hours: Kac saatlik veri

        Returns:
            Saatlik istatistik listesi
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            stats = (
                db.query(ServerStatsHourly)
                .filter(
                    ServerStatsHourly.server_id == server_id,
                    ServerStatsHourly.hour_timestamp >= cutoff,
                )
                .order_by(ServerStatsHourly.hour_timestamp.asc())
                .all()
            )

            return [
                {
                    "timestamp": s.hour_timestamp.isoformat(),
                    "avg_players": round(s.avg_players, 2),
                    "max_players": s.max_players,
                    "unique_players": s.unique_players,
                    "map": s.most_played_map,
                }
                for s in stats
            ]
        finally:
            db.close()

    def get_daily_stats(self, server_id: int, days: int = 30) -> List[Dict]:
        """
        Gunluk istatistikleri getir

        Args:
            server_id: Sunucu ID
            days: Kac gunluk veri

        Returns:
            Gunluk istatistik listesi
        """
        db = SessionLocal()
        try:
            cutoff = date.today() - timedelta(days=days)
            stats = (
                db.query(ServerStatsDaily)
                .filter(ServerStatsDaily.server_id == server_id, ServerStatsDaily.date >= cutoff)
                .order_by(ServerStatsDaily.date.asc())
                .all()
            )

            return [
                {
                    "date": s.date.isoformat() if hasattr(s.date, "isoformat") else str(s.date),
                    "total_players": s.total_players,
                    "unique_players": s.unique_players,
                    "avg_players": round(s.avg_players, 2),
                    "max_players": s.max_players,
                    "peak_hour": s.peak_hour,
                    "most_played_map": s.most_played_map,
                }
                for s in stats
            ]
        finally:
            db.close()

    def get_peak_hours_heatmap(self, server_id: int, days: int = 30) -> Dict:
        """
        24x7 yogunluk haritasi olustur

        Args:
            server_id: Sunucu ID
            days: Kac gunluk veri

        Returns:
            Heatmap verisi
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            stats = (
                db.query(ServerStatsHourly)
                .filter(
                    ServerStatsHourly.server_id == server_id,
                    ServerStatsHourly.hour_timestamp >= cutoff,
                )
                .all()
            )

            # 24x7 grid
            heatmap = [[0 for _ in range(7)] for _ in range(24)]

            for stat in stats:
                hour = stat.hour_timestamp.hour
                day_of_week = stat.hour_timestamp.weekday()
                heatmap[hour][day_of_week] += stat.avg_players

            # Hafta sayisina gore ortala
            weeks = days / 7
            for h in range(24):
                for d in range(7):
                    heatmap[h][d] = round(heatmap[h][d] / weeks, 1) if weeks > 0 else 0

            return {
                "hours": list(range(24)),
                "days": ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"],
                "data": heatmap,
            }
        finally:
            db.close()

    def calculate_retention_rate(self, server_id: int, days: int = 7) -> Dict:
        """
        Oyuncu sadakat orani hesapla

        Args:
            server_id: Sunucu ID
            days: Analiz suresi

        Returns:
            Sadakat istatistikleri
        """
        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Period icindeki oturumlari al
            sessions = (
                db.query(PlayerSession)
                .filter(PlayerSession.server_id == server_id, PlayerSession.join_time >= cutoff)
                .all()
            )

            # Her oyuncunun kac gun girdigini hesapla
            player_days = defaultdict(set)
            for session in sessions:
                if session.steam_id:
                    day = session.join_time.date()
                    player_days[session.steam_id].add(day)

            total_players = len(player_days)
            returning_players = sum(1 for days in player_days.values() if len(days) > 1)

            retention_rate = (returning_players / total_players * 100) if total_players > 0 else 0

            return {
                "total_players": total_players,
                "returning_players": returning_players,
                "retention_rate": round(retention_rate, 2),
            }
        finally:
            db.close()

    def get_map_distribution(self, server_id: int, days: int = 7) -> Dict:
        """
        Harita dagilimini getir

        Args:
            server_id: Sunucu ID
            days: Analiz suresi

        Returns:
            Harita dagilimi
        """
        db = SessionLocal()
        try:
            cutoff = date.today() - timedelta(days=days)
            stats = (
                db.query(ServerStatsDaily)
                .filter(ServerStatsDaily.server_id == server_id, ServerStatsDaily.date >= cutoff)
                .all()
            )

            map_totals = defaultdict(int)
            for stat in stats:
                if stat.map_playtime_json:
                    for map_name, minutes in stat.map_playtime_json.items():
                        map_totals[map_name] += minutes

            # En cok oynanan 10 harita
            sorted_maps = sorted(map_totals.items(), key=lambda x: x[1], reverse=True)[:10]

            return {"labels": [m[0] for m in sorted_maps], "data": [m[1] for m in sorted_maps]}
        finally:
            db.close()

    def export_stats_csv(self, server_id: int, date_from: date, date_to: date) -> str:
        """
        Istatistikleri CSV olarak export et

        Args:
            server_id: Sunucu ID
            date_from: Baslangic tarihi
            date_to: Bitis tarihi

        Returns:
            CSV string
        """
        db = SessionLocal()
        try:
            stats = (
                db.query(ServerStatsDaily)
                .filter(
                    ServerStatsDaily.server_id == server_id,
                    ServerStatsDaily.date >= date_from,
                    ServerStatsDaily.date <= date_to,
                )
                .order_by(ServerStatsDaily.date.asc())
                .all()
            )

            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "Tarih",
                    "Toplam Oyuncu",
                    "Benzersiz Oyuncu",
                    "Ortalama Oyuncu",
                    "Max Oyuncu",
                    "En Çok Oynanan Harita",
                ]
            )

            for stat in stats:
                writer.writerow(
                    [
                        (
                            stat.date.isoformat()
                            if hasattr(stat.date, "isoformat")
                            else str(stat.date)
                        ),
                        stat.total_players,
                        stat.unique_players,
                        round(stat.avg_players, 2),
                        stat.max_players,
                        stat.most_played_map or "",
                    ]
                )

            return output.getvalue()
        finally:
            db.close()

    def aggregate_daily_stats(self, server_id: int, target_date: date):
        """
        Saatlik istatistikleri gunluk olarak topla

        Args:
            server_id: Sunucu ID
            target_date: Hedef tarih

        Bu fonksiyon her gece calisir ve onceki gunun saatlik
        istatistiklerini gunluk istatistiklere toplar
        """
        db = SessionLocal()
        try:
            # Gunun saatlik istatistiklerini al
            day_start = datetime.combine(target_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)

            hourly_stats = (
                db.query(ServerStatsHourly)
                .filter(
                    ServerStatsHourly.server_id == server_id,
                    ServerStatsHourly.hour_timestamp >= day_start,
                    ServerStatsHourly.hour_timestamp < day_end,
                )
                .all()
            )

            if not hourly_stats:
                logger.info(f"No hourly stats for server {server_id} on {target_date}")
                return

            # Agregatlar
            total_players = sum(s.unique_players for s in hourly_stats)
            unique_players = total_players  # Yaklasik
            avg_players = sum(s.avg_players for s in hourly_stats) / len(hourly_stats)
            max_players = max(s.max_players for s in hourly_stats)

            # En yogun saat
            peak_hour_stat = max(hourly_stats, key=lambda s: s.avg_players)
            peak_hour = peak_hour_stat.hour_timestamp.hour

            # Harita dagilimi
            map_counts = defaultdict(int)
            for stat in hourly_stats:
                if stat.most_played_map:
                    map_counts[stat.most_played_map] += 1
            most_played_map = max(map_counts, key=map_counts.get) if map_counts else None

            # Gunluk stat oluştur/guncelle
            daily_stat = (
                db.query(ServerStatsDaily)
                .filter(
                    ServerStatsDaily.server_id == server_id, ServerStatsDaily.date == target_date
                )
                .first()
            )

            if daily_stat:
                daily_stat.total_players = total_players
                daily_stat.unique_players = unique_players
                daily_stat.avg_players = avg_players
                daily_stat.max_players = max_players
                daily_stat.peak_hour = peak_hour
                daily_stat.most_played_map = most_played_map
            else:
                daily_stat = ServerStatsDaily(
                    server_id=server_id,
                    date=target_date,
                    total_players=total_players,
                    unique_players=unique_players,
                    avg_players=avg_players,
                    max_players=max_players,
                    peak_hour=peak_hour,
                    most_played_map=most_played_map,
                )
                db.add(daily_stat)

            db.commit()
            logger.info(f"Daily stats aggregated for server {server_id} on {target_date}")

        except Exception as e:
            logger.error(f"Failed to aggregate daily stats for server {server_id}: {e}")
            db.rollback()
        finally:
            db.close()

    def aggregate_weekly_stats(self, server_id: int, week_start: date):
        """
        Gunluk istatistikleri haftalik olarak topla

        Args:
            server_id: Sunucu ID
            week_start: Hafta baslangici (Pazartesi)
        """
        db = SessionLocal()
        try:
            week_end = week_start + timedelta(days=7)

            daily_stats = (
                db.query(ServerStatsDaily)
                .filter(
                    ServerStatsDaily.server_id == server_id,
                    ServerStatsDaily.date >= week_start,
                    ServerStatsDaily.date < week_end,
                )
                .all()
            )

            if not daily_stats:
                return

            # Agregatlar
            total_players = sum(s.total_players for s in daily_stats)
            unique_players = sum(s.unique_players for s in daily_stats)
            avg_players = sum(s.avg_players for s in daily_stats) / len(daily_stats)
            max_players = max(s.max_players for s in daily_stats)

            # Haftalik stat oluştur/guncelle
            weekly_stat = (
                db.query(ServerStatsWeekly)
                .filter(
                    ServerStatsWeekly.server_id == server_id,
                    ServerStatsWeekly.week_start == week_start,
                )
                .first()
            )

            if weekly_stat:
                weekly_stat.total_players = total_players
                weekly_stat.unique_players = unique_players
                weekly_stat.avg_players = avg_players
                weekly_stat.max_players = max_players
            else:
                weekly_stat = ServerStatsWeekly(
                    server_id=server_id,
                    week_start=week_start,
                    total_players=total_players,
                    unique_players=unique_players,
                    avg_players=avg_players,
                    max_players=max_players,
                )
                db.add(weekly_stat)

            db.commit()
            logger.info(f"Weekly stats aggregated for server {server_id} week {week_start}")

        except Exception as e:
            logger.error(f"Failed to aggregate weekly stats for server {server_id}: {e}")
            db.rollback()
        finally:
            db.close()
