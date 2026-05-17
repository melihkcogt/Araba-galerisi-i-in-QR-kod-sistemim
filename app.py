from flask import Flask, render_template, send_file
import json
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

# Araç verilerini JSON dosyasından oku
def arac_verisi_yukle():
    try:
        with open('data/araclar.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def arac_verisi_kaydet(araclar):
    with open('data/araclar.json', 'w', encoding='utf-8') as f:
        json.dump(araclar, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/arac/<arac_id>')
def arac_detay(arac_id):
    araclar = arac_verisi_yukle()
    arac = araclar.get(arac_id, {})
    return render_template('arac.html', arac=arac, arac_id=arac_id)

@app.route('/admin')
def admin_panel():
    araclar = arac_verisi_yukle()
    html = '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #333; text-align: center; }
            .form-card, .arac-card { 
                background: white; padding: 20px; margin: 15px 0; 
                border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            input, textarea { 
                width: 100%; padding: 10px; margin: 5px 0; 
                border: 1px solid #ddd; border-radius: 5px; 
            }
            .btn { 
                display: inline-block; padding: 12px 24px; 
                background: #007bff; color: white; text-decoration: none; 
                border-radius: 5px; margin: 5px; border: none; cursor: pointer;
            }
            .btn-green { background: #28a745; }
            .btn-red { background: #dc3545; }
            .qr-container { text-align: center; margin-top: 15px; }
            .qr-container img { max-width: 250px; border: 2px solid #ddd; border-radius: 10px; }
            .success { color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Araba Galerisi Sistemi</h1>
            <p>QR Kod ile Araç Yönetimi</p>
            
            <div class="form-card">
                <h2>➕ Araç Ekle</h2>
                <form action="/admin/arac-ekle" method="POST">
                    <input type="text" name="marka" placeholder="Marka (örn: BMW)" required>
                    <input type="text" name="model" placeholder="Model (örn: 3.20i)" required>
                    <input type="text" name="yil" placeholder="Yıl (örn: 2020)" required>
                    <input type="text" name="fiyat" placeholder="Fiyat (örn: 850.000 TL)" required>
                    <input type="text" name="km" placeholder="Kilometre (örn: 45.000 km)" required>
                    <input type="text" name="yakit" placeholder="Yakıt (örn: Benzin)" required>
                    <input type="text" name="vites" placeholder="Vites (örn: Otomatik)" required>
                    <input type="text" name="renk" placeholder="Renk (örn: Beyaz)" required>
                    <input type="text" name="telefon" placeholder="Telefon (örn: 0555 123 45 67)" required>
                    <input type="text" name="foto" placeholder="Fotoğraf URL (opsiyonel)">
                    <textarea name="aciklama" placeholder="Araç açıklaması..." rows="3"></textarea>
                    <button type="submit" class="btn btn-green">🚗 Araç Ekle & QR Kod Üret</button>
                </form>
            </div>
            
            <h2>📋 Eklenen Araçlar</h2>
    '''
    
    for arac_id, arac in araclar.items():
        qr_yolu = f'static/qr_kodlar/{arac_id}.png'
        qr_var = os.path.exists(qr_yolu)
        
        html += f'''
            <div class="arac-card">
                <h3>{arac.get('baslik', arac_id)}</h3>
                <p>💰 Fiyat: ₺{arac.get('fiyat', '?')}</p>
                <p>📱 Telefon: {arac.get('telefon', '?')}</p>
                <a href="/admin/qr-goster/{arac_id}" class="btn">📱 QR Kod Gör</a>
                <a href="/arac/{arac_id}" target="_blank" class="btn btn-green">🔗 Sayfayı Gör</a>
                <a href="/admin/arac-sil/{arac_id}" class="btn btn-red" onclick="return confirm('Silmek istediğine emin misin?')">🗑️ Sil</a>
        '''
        
        if qr_var:
            html += f'''
                <div class="qr-container">
                    <p class="success">✅ QR Kodunuz Hazır!</p>
                    <p>Bu QR kodu aracın camına yapıştırın.</p>
                    <img src="/static/qr_kodlar/{arac_id}.png" alt="QR Kod">
                    <br><br>
                    <a href="/static/qr_kodlar/{arac_id}.png" download class="btn">⬇️ İndir</a>
                </div>
            '''
        
        html += '</div>'
    
    html += '''
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/admin/arac-ekle', methods=['POST'])
def arac_ekle():
    marka = request.form.get('marka')
    model = request.form.get('model')
    yil = request.form.get('yil')
    fiyat = request.form.get('fiyat')
    km = request.form.get('km')
    yakit = request.form.get('yakit')
    vites = request.form.get('vites')
    renk = request.form.get('renk')
    telefon = request.form.get('telefon')
    foto = request.form.get('foto', '/static/arac-foto.jpg')
    aciklama = request.form.get('aciklama', '')
    
    arac_id = f"{marka.lower()}{model.lower()}-{yil}"
    
    araclar = arac_verisi_yukle()
    araclar[arac_id] = {
        "baslik": f"{yil} {marka} {model}",
        "marka": marka,
        "model": model,
        "yil": yil,
        "fiyat": fiyat,
        "km": km,
        "yakit": yakit,
        "vites": vites,
        "renk": renk,
        "telefon": telefon,
        "foto": foto,
        "aciklama": aciklama
    }
    arac_verisi_kaydet(araclar)
    
    # QR kod üret
    return qr_uret(arac_id)

@app.route('/admin/qr-goster/<arac_id>')
def qr_goster(arac_id):
    return qr_uret(arac_id)

def qr_uret(arac_id):
    araclar = arac_verisi_yukle()
    arac = araclar.get(arac_id)
    
    if not arac:
        return "Araç bulunamadı!", 404
    
    # QR kod URL'si
    url = f"https://glowing-happiness-w7v9v5wx5wvgp76.github.dev/arac/{arac_id}"
    
    # QR kod oluştur
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Kaydet
    qr_klasor = 'static/qr_kodlar'
    os.makedirs(qr_klasor, exist_ok=True)
    dosya_yolu = f'{qr_klasor}/{arac_id}.png'
    img.save(dosya_yolu)
    
    return f'''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QR Kod - {arac.get('baslik')}</title>
        <style>
            body {{ font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; }}
            img {{ max-width: 300px; border: 3px solid #007bff; border-radius: 10px; }}
            .btn {{ display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
            .url {{ background: #f8f9fa; padding: 10px; border-radius: 5px; word-break: break-all; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✅ QR Kod Üretildi!</h2>
            <h3>{arac.get('baslik')}</h3>
            <p class="url">URL: {url}</p>
            <img src="/static/qr_kodlar/{arac_id}.png" alt="QR Kod">
            <br><br>
            <a href="/static/qr_kodlar/{arac_id}.png" download class="btn">⬇️ İndir</a>
            <a href="/admin" class="btn" style="background:#28a745;">← Admin Panel</a>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/arac-sil/<arac_id>')
def arac_sil(arac_id):
    araclar = arac_verisi_yukle()
    if arac_id in araclar:
        del araclar[arac_id]
        arac_verisi_kaydet(araclar)
        
        # QR kodu da sil
        qr_yolu = f'static/qr_kodlar/{arac_id}.png'
        if os.path.exists(qr_yolu):
            os.remove(qr_yolu)
    
    return '''
    <script>alert('Araç silindi!'); window.location.href='/admin';</script>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)