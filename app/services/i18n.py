"""
AGTR Merkezi - i18n Service
Coklu dil destegi
"""

from typing import Dict

# Dil dosyalari
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "tr": {
        "home": "Ana Sayfa",
        "forum": "Forum",
        "servers": "Sunucular",
        "leaderboard": "Sıralama",
        "members": "Üyeler",
        "login": "Giriş Yap",
        "register": "Kayıt Ol",
        "logout": "Çıkış Yap",
        "profile": "Profilim",
        "panel": "Kontrol Paneli",
        "my_servers": "Sunucularım",
        "balance": "Bakiye",
        "settings": "Ayarlar",
        "admin": "Admin",
        "search": "Ara",
        "notifications": "Bildirimler",
        "no_notifications": "Yeni bildirim yok",
        "mark_all_read": "Tümünü Okundu İşaretle",
        "welcome": "Hoş Geldiniz",
        "slogan": "Türkiye'nin en iyi Half-Life ve CS 1.6 platformu",
        "create_server": "Sunucu Oluştur",
        "buy_package": "Paket Satın Al",
        "view_all": "Tümünü Gör",
        "online": "Çevrimiçi",
        "offline": "Çevrimdışı",
        "players": "Oyuncu",
        "slots": "Slot",
        "monthly": "Aylık",
        "popular": "Popüler",
        "new": "Yeni",
        "save": "Kaydet",
        "cancel": "İptal",
        "delete": "Sil",
        "edit": "Düzenle",
        "add": "Ekle",
        "loading": "Yükleniyor...",
        "error": "Hata",
        "success": "Başarılı",
        "confirm": "Onayla",
        "back": "Geri",
        "next": "İleri",
        "previous": "Önceki",
        "total": "Toplam",
        "today": "Bugün",
        "yesterday": "Dün",
        "this_week": "Bu Hafta",
        "this_month": "Bu Ay",
    },
    "en": {
        "home": "Home",
        "forum": "Forum",
        "servers": "Servers",
        "leaderboard": "Leaderboard",
        "members": "Members",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "profile": "My Profile",
        "panel": "Control Panel",
        "my_servers": "My Servers",
        "balance": "Balance",
        "settings": "Settings",
        "admin": "Admin",
        "search": "Search",
        "notifications": "Notifications",
        "no_notifications": "No new notifications",
        "mark_all_read": "Mark All Read",
        "welcome": "Welcome",
        "slogan": "Turkey's best Half-Life and CS 1.6 platform",
        "create_server": "Create Server",
        "buy_package": "Buy Package",
        "view_all": "View All",
        "online": "Online",
        "offline": "Offline",
        "players": "Players",
        "slots": "Slots",
        "monthly": "Monthly",
        "popular": "Popular",
        "new": "New",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "confirm": "Confirm",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "total": "Total",
        "today": "Today",
        "yesterday": "Yesterday",
        "this_week": "This Week",
        "this_month": "This Month",
    }
}

DEFAULT_LANG = "tr"


def get_translation(key: str, lang: str = None) -> str:
    """Ceviri getir"""
    if lang is None:
        lang = DEFAULT_LANG
    
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANG
    
    return TRANSLATIONS[lang].get(key, key)


def t(key: str, lang: str = None) -> str:
    """Kisa ceviri fonksiyonu"""
    return get_translation(key, lang)


def get_available_languages() -> list:
    """Mevcut dilleri getir"""
    return [
        {"code": "tr", "name": "Türkçe", "flag": "🇹🇷"},
        {"code": "en", "name": "English", "flag": "🇬🇧"}
    ]


class I18n:
    """i18n class for templates"""
    
    def __init__(self, lang: str = None):
        self.lang = lang or DEFAULT_LANG
    
    def __call__(self, key: str) -> str:
        return get_translation(key, self.lang)
    
    def set_lang(self, lang: str):
        self.lang = lang


# Global instance
i18n = I18n()

def get_locale() -> str:
    return i18n.lang

def set_locale(lang: str):
    i18n.set_lang(lang)
