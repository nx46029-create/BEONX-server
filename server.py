from flask import Flask, request, jsonify
import json, os, urllib.request, urllib.parse

app = Flask(__name__)

# Render Environment Variables kısmından otomatik çeker (veya doğrudan tırnak içine yazabilirsin)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "BURAYA_SUPABASE_PROJECT_URL_YAZ")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "BURAYA_SUPABASE_ANON_KEY_YAZ")

def supabase_istek(endpoint, method="GET", data=None):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as res:
        icerik = res.read().decode("utf-8")
        return json.loads(icerik) if icerik else []

@app.route("/", methods=["GET"])
def ana_sayfa():
    return jsonify({"durum": "BEONX Online Sunucu Aktif!"})

@app.route("/skor_gonder", methods=["POST"])
def skor_gonder():
    data = request.get_json(silent=True)
    if not data or "ad" not in data or "rekor" not in data:
        return jsonify({"durum": "hata", "mesaj": "Eksik veri"}), 400
    
    ad = str(data["ad"]).strip()[:16]
    try:
        yeni_rekor = int(data["rekor"])
    except ValueError:
        return jsonify({"durum": "hata", "mesaj": "Gecersiz skor"}), 400

    if yeni_rekor < 0 or yeni_rekor > 100000:
        return jsonify({"durum": "hata", "mesaj": "Gecersiz aralik"}), 400

    try:
        guvenli_ad = urllib.parse.quote(ad)
        mevcut = supabase_istek(f"skorlar?ad=eq.{guvenli_ad}&select=rekor", method="GET")
        
        if mevcut:
            eski_rekor = mevcut[0].get("rekor", 0)
            if yeni_rekor > eski_rekor:
                supabase_istek(f"skorlar?ad=eq.{guvenli_ad}", method="PATCH", data={"rekor": yeni_rekor})
                return jsonify({"durum": "ok", "rekor": yeni_rekor})
            return jsonify({"durum": "ok", "rekor": eski_rekor})
        else:
            supabase_istek("skorlar", method="POST", data={"ad": ad, "rekor": yeni_rekor})
            return jsonify({"durum": "ok", "rekor": yeni_rekor})
    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": str(e)}), 500

@app.route("/liderlik", methods=["GET"])
def liderlik():
    try:
        sirali = supabase_istek("skorlar?select=ad,rekor&order=rekor.desc&limit=10", method="GET")
        return jsonify(sirali)
    except Exception:
        return jsonify([]), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
