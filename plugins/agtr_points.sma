/**
 * AGTR Merkezi - Puan Sistemi Plugin
 * Half-Life / CS 1.6 AMX Mod X Plugin
 *
 * Bu plugin oyuncuların kill, headshot ve oynama sürelerini
 * AGTR API'sine gönderir ve Armor puanı kazandırır.
 *
 * Kurulum:
 * 1. Bu dosyayı scripting/ klasörüne koyun
 * 2. amxxpc agtr_points.sma ile derleyin
 * 3. agtr_points.amxx dosyasını plugins/ klasörüne koyun
 * 4. plugins.ini dosyasına "agtr_points.amxx" ekleyin
 * 5. server.cfg dosyasına API ayarlarını ekleyin
 */

#include <amxmodx>
#include <amxmisc>
#include <cstrike>
#include <fun>
#include <engine>
#include <fakemeta>

// Plugin bilgileri
#define PLUGIN_NAME    "AGTR Puan Sistemi"
#define PLUGIN_VERSION "1.0.0"
#define PLUGIN_AUTHOR  "AGTR Merkezi"

// CVarlar
new g_apiUrl[256]
new g_apiKey[128]
new g_serverName[64]

// Oyuncu verileri
new g_playerKills[33]
new g_playerDeaths[33]
new g_playerHeadshots[33]
new g_playerConnectTime[33]
new g_playerSteamId[33][35]
new bool:g_playerFirstBlood

public plugin_init()
{
    register_plugin(PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_AUTHOR)

    // CVarlar
    register_cvar("agtr_api_url", "https://agtrmerkezi.com/api/game")
    register_cvar("agtr_api_key", "YOUR_API_KEY_HERE")
    register_cvar("agtr_server_name", "AGTR CS 1.6")

    // Eventler
    register_event("DeathMsg", "event_death", "a")
    register_event("HLTV", "event_round_start", "a", "1=0", "2=0")
    register_event("TextMsg", "event_game_restart", "a", "2=#Game_Commencing")

    // Logeventler
    register_logevent("logevent_round_end", 2, "1=Round_End")

    // Task - her 5 dakikada bir kontrol
    set_task(300.0, "task_check_playtime", _, _, _, "b")
}

public plugin_cfg()
{
    // CVarları oku
    get_cvar_string("agtr_api_url", g_apiUrl, charsmax(g_apiUrl))
    get_cvar_string("agtr_api_key", g_apiKey, charsmax(g_apiKey))
    get_cvar_string("agtr_server_name", g_serverName, charsmax(g_serverName))
}

public client_connect(id)
{
    // Verileri sıfırla
    g_playerKills[id] = 0
    g_playerDeaths[id] = 0
    g_playerHeadshots[id] = 0
    g_playerConnectTime[id] = get_systime()

    // Steam ID al
    get_user_authid(id, g_playerSteamId[id], charsmax(g_playerSteamId[]))

    // API'ye bağlantı bildir
    new data[512]
    formatex(data, charsmax(data),
        "{\"steam_id\":\"%s\",\"player_name\":\"%n\",\"ip_address\":\"%s\"}",
        g_playerSteamId[id], id, "")

    send_api_request("/player-connect", data)
}

public client_disconnect(id)
{
    if(g_playerConnectTime[id] > 0)
    {
        new playtime = (get_systime() - g_playerConnectTime[id]) / 60

        // API'ye ayrılma bildir
        new data[256]
        formatex(data, charsmax(data),
            "{\"steam_id\":\"%s\",\"playtime_minutes\":%d}",
            g_playerSteamId[id], playtime)

        send_api_request("/player-disconnect", data)

        // Sıfırla
        g_playerConnectTime[id] = 0
    }
}

public event_death()
{
    new killer = read_data(1)
    new victim = read_data(2)
    new headshot = read_data(3)

    if(killer > 0 && killer != victim)
    {
        g_playerKills[killer]++

        if(headshot)
        {
            g_playerHeadshots[killer]++
        }

        // First blood kontrolü
        if(!g_playerFirstBlood)
        {
            g_playerFirstBlood = true
            // First blood API bildirimi yapılabilir
        }
    }

    if(victim > 0)
    {
        g_playerDeaths[victim]++
    }
}

public event_round_start()
{
    g_playerFirstBlood = false
}

public logevent_round_end()
{
    // Round sonu istatistikleri gönder
    send_all_player_stats()
}

public task_check_playtime()
{
    // Periyodik playtime kontrolü (opsiyonel)
}

send_all_player_stats()
{
    new players[32], num
    get_players(players, num)

    new mapname[32]
    get_mapname(mapname, charsmax(mapname))

    for(new i = 0; i < num; i++)
    {
        new id = players[i]

        if(g_playerKills[id] > 0 || g_playerDeaths[id] > 0)
        {
            new playtime = (get_systime() - g_playerConnectTime[id]) / 60

            new data[512]
            formatex(data, charsmax(data),
                "{\"steam_id\":\"%s\",\"kills\":%d,\"deaths\":%d,\"headshots\":%d,\"playtime_minutes\":%d,\"server_name\":\"%s\",\"map_name\":\"%s\"}",
                g_playerSteamId[id],
                g_playerKills[id],
                g_playerDeaths[id],
                g_playerHeadshots[id],
                playtime,
                g_serverName,
                mapname)

            send_api_request("/report-stats", data)

            // İstatistikleri sıfırla
            g_playerKills[id] = 0
            g_playerDeaths[id] = 0
            g_playerHeadshots[id] = 0
        }
    }
}

send_api_request(const endpoint[], const data[])
{
    // HTTP POST isteği gönder
    // Not: AMX Mod X'te HTTP için ek modül gerekebilir (curl, socket vs.)
    // Bu örnek kod temel yapıyı göstermektedir

    // Gerçek implementasyonda:
    // 1. socket modülü veya
    // 2. curl extension veya
    // 3. external script (PHP/Python) çağrısı kullanılabilir

    server_print("[AGTR] API Request: %s%s", g_apiUrl, endpoint)
    server_print("[AGTR] Data: %s", data)
}

// ============ KULLANICI KOMUTLARI ============

public client_command(id)
{
    new cmd[32]
    read_argv(0, cmd, charsmax(cmd))

    if(equal(cmd, "say") || equal(cmd, "say_team"))
    {
        new arg[64]
        read_args(arg, charsmax(arg))
        remove_quotes(arg)

        if(equal(arg, "/puan") || equal(arg, "!puan"))
        {
            show_player_stats(id)
            return PLUGIN_HANDLED
        }

        if(equal(arg, "/agtr") || equal(arg, "!agtr"))
        {
            show_agtr_info(id)
            return PLUGIN_HANDLED
        }
    }

    return PLUGIN_CONTINUE
}

show_player_stats(id)
{
    new playtime = (get_systime() - g_playerConnectTime[id]) / 60

    client_print(id, print_chat, "[AGTR] Kill: %d | Headshot: %d | Oynama: %d dk",
        g_playerKills[id], g_playerHeadshots[id], playtime)
    client_print(id, print_chat, "[AGTR] Steam ID: %s", g_playerSteamId[id])
}

show_agtr_info(id)
{
    client_print(id, print_chat, "[AGTR] AGTR Merkezi Puan Sistemi v%s", PLUGIN_VERSION)
    client_print(id, print_chat, "[AGTR] Kill: +0.5 Armor | Headshot: +1 Armor | Dakika: +0.1 Armor")
    client_print(id, print_chat, "[AGTR] Hesabini bagla: agtrmerkezi.com")
}
