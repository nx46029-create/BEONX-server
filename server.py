import array, json, math, os, random, ssl, sys, threading, traceback, urllib.parse, urllib.request, pygame

SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_PoeNO0-oIckh8xxWLk4dkA__KQrchrf"

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = ekran.get_size()
tam_ekran = True
pygame.display.set_caption("BEONX")

ARKA, IZGARA, PANEL, BEYAZ, GRI = (14, 16, 26), (26, 30, 48), (20, 24, 38), (240, 245, 255), (50, 55, 75)
MAVI, YESIL, SARI, KIRMIZI, MOR, TURUNCU, CAMGOBEGI = (0, 210, 255), (50, 255, 130), (255, 215, 0), (255, 65, 85), (190, 80, 255), (255, 140, 0), (0, 255, 220)
GUMUS, BRONZ = (192, 192, 210), (205, 127, 50)
font, kucuk_font, buyuk_font = pygame.font.SysFont("Segoe UI", 21, bold=True), pygame.font.SysFont("Segoe UI", 15, bold=True), pygame.font.SysFont("Segoe UI", 64, bold=True)
saat, oyun_durumu, KAYIT_DOSYA = pygame.time.Clock(), "LOGIN", "kayit.json"

online_liderlik = []
sunucu_durum_mesaji = ""

def supabase_baglan(yol, method="GET", veri=None):
    baglam = ssl._create_unverified_context()
    basliklar = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    govde = json.dumps(veri).encode("utf-8") if veri is not None else None
    istek = urllib.request.Request(f"{SUPABASE_URL}/rest/v1/{yol}", data=govde, headers=basliklar, method=method)
    with urllib.request.urlopen(istek, timeout=15, context=baglam) as yanit:
        icerik = yanit.read().decode("utf-8")
        return json.loads(icerik) if icerik else []

def sunucuya_skor_gonder(k_ad, rekor_skor):
    def islem():
        try:
            guvenli_ad = urllib.parse.quote(k_ad)
            mevcut = supabase_baglan(f"skorlar?ad=eq.{guvenli_ad}&select=rekor", "GET")
            if mevcut:
                if rekor_skor > mevcut.get("rekor", 0):
                    supabase_baglan(f"skorlar?ad=eq.{guvenli_ad}", "PATCH", {"rekor": rekor_skor})
            else:
                supabase_baglan("skorlar", "POST", {"ad": k_ad, "rekor": rekor_skor})
        except Exception:
            pass
    threading.Thread(target=islem, daemon=True).start()

def sunucudan_liderlik_cek():
    global online_liderlik, sunucu_durum_mesaji
    sunucu_durum_mesaji = "Veritabanına bağlanılıyor..."
    def islem():
        global online_liderlik, sunucu_durum_mesaji
        try:
            online_liderlik = supabase_baglan("skorlar?select=ad,rekor&order=rekor.desc&limit=10", "GET")
            sunucu_durum_mesaji = "" if online_liderlik else "Bağlantı BAŞARILI! (Henüz skor yok)"
        except Exception as e:
            sunucu_durum_mesaji = f"Hata: {str(e)[:50]}"
    threading.Thread(target=islem, daemon=True).start()
