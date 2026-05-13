import streamlit as st
import pandas as pd
import pdfplumber
import base64
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="VetLabAI | Diagnostic System", layout="wide")

# --- SESSION STATE (Veri Koruma) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- PDF GÖRÜNTÜLEME FONKSİYONU ---
def pdf_goruntule(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # PDF'i bir iframe içinde web sayfasında gösterir
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- GELİŞMİŞ TEŞHİS MOTORU ---
def vaka_analiz_motoru(tahlil_metni, kütüphane):
    teshisler = []
    for makale in kütüphane:
        skor = 0
        eslesen_parametreler = []
        icerik = makale["İçerik"].lower()
        
        parametre_sozlugu = {
            "HGB": ["hemoglobin", "hgb", "anemi", "düşük"],
            "FE": ["demir", "serum demir", "fe", "hipoferremi"],
            "FERRITIN": ["ferritin", "depo demir", "azalma"],
            "GLU": ["glikoz", "glukoz", "şeker", "diyabet"],
            "RBC": ["alyuvar", "rbc", "eritrosit"]
        }
        
        for p_key, anahtar_kelimeler in parametre_sozlugu.items():
            if any(ak in icerik for ak in anahtar_kelimeler) and p_key.lower() in tahlil_metni:
                skor += 1
                eslesen_parametreler.append(p_key)
        
        if skor >= 2:
            teshisler.append({
                "Hastalık": makale["Başlık"],
                "Güven": f"%{min(skor * 25, 98)}",
                "Analiz": "Kütüphanedeki bilimsel veriler, tahlildeki anomali tablosuyla yüksek oranda örtüşmektedir."
            })
    return teshisler

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Giriş")
    user = st.text_input("Kullanıcı Adı")
    pw = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and pw == "vetlab2026":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🐾 VetLabAI")
st.sidebar.write(f"Hoş geldin, **Bertuğ Ege Sargın**")
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 Teşhis Paneli", "📚 Vaka Arşivi", "⚙️ AI Eğitim & Kütüphane"])

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Klinik Durum Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi))
    c2.metric("Kütüphane (Makale)", len(st.session_state.kutuphane))
    c3.metric("Teşhis Motoru", "Aktif")

# --- 2. TEŞHİS PANELİ ---
elif menu == "🔬 Teşhis Paneli":
    st.header("🔬 Akıllı Teşhis Paneli")
    up = st.file_uploader("Tahlil Dosyası Yükle", type=["pdf", "jpg", "png"])
    if up:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("🐾 Hasta Adı")
            age = st.number_input("🎂 Yaş", 0, 30)
        with col2:
            breed = st.text_input("🐕 Irk")
            gender = st.selectbox("⚧ Cinsiyet", ["Erkek", "Dişi"])
            
        if st.button("AI Analizini Başlat"):
            tahlil_text = ""
            if up.type == "application/pdf":
                with pdfplumber.open(up) as pdf:
                    tahlil_text = "".join([p.extract_text() for p in pdf.pages]).lower()
            
            sonuclar = vaka_analiz_motoru(tahlil_text, st.session_state.kutuphane)
            if sonuclar:
                for s in sonuclar:
                    st.success(f"### 🎯 Teşhis: {s['Hastalık']}")
                    st.write(f"**Güven Oranı:** {s['Güven']}")
                    st.info(f"**🔍 Analiz Notu:** {s['Analiz']}")
                    st.session_state.vaka_arsivi.append({
                        "Tarih": datetime.now().strftime("%d/%m/%Y"),
                        "Hasta": name, "Teşhis": s['Hastalık'], "Güven": s['Güven']
                    })
            else:
                st.warning("Eşleşen bir hastalık bulunamadı.")

# --- 3. VAKA ARŞİVİ ---
elif menu == "📚 Vaka Arşivi":
    st.header("📖 Klinik Kayıt Arşivi")
    if st.session_state.vaka_arsivi:
        st.table(pd.DataFrame(st.session_state.vaka_arsivi))
    else:
        st.info("Henüz kaydedilmiş bir vaka bulunmuyor.")

# --- 4. AI EĞİTİM & KÜTÜPHANE ---
elif menu == "⚙️ AI Eğitim & Kütüphane":
    st.header("📚 AI Bilgi Bankası ve Kaynak Yönetimi")
    
    new_pdf = st.file_uploader("Sisteme Yeni Makale Öğret (PDF)", type="pdf")
    if new_pdf and st.button("Veriyi Hafızaya Al"):
        with pdfplumber.open(new_pdf) as pdf:
            text = "".join([p.extract_text() for p in pdf.pages])
        # PDF dosyasının kendisini de saklıyoruz
        st.session_state.kutuphane.append({
            "Başlık": new_pdf.name, 
            "İçerik": text, 
            "Raw": new_pdf.getvalue()
        })
        st.success("Yeni bilgi başarıyla öğrenildi!")

    st.divider()
    st.subheader("📖 Öğrenilen Kaynaklar")
    
    if st.session_state.kutuphane:
        for idx, makale in enumerate(st.session_state.kutuphane):
            col_name, col_view, col_del = st.columns([3, 1, 1])
            with col_name:
                # İsim Düzenleme Alanı
                st.session_state.kutuphane[idx]['Başlık'] = st.text_input(f"Kaynak {idx+1}", value=makale['Başlık'], key=f"title_{idx}")
            with col_view:
                st.write(" ") # Hizalama
                if st.button("📄 PDF Aç", key=f"open_{idx}"):
                    st.info(f"{makale['Başlık']} Görüntüleniyor...")
                    pdf_goruntule(makale['Raw'])
            with col_del:
                st.write(" ") # Hizalama
                if st.button("🗑 Sil", key=f"del_{idx}"):
                    st.session_state.kutuphane.pop(idx)
                    st.rerun()
    else:
        st.info("Kütüphanede kayıtlı makale bulunamadı.")
