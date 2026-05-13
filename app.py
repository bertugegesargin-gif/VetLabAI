import streamlit as st
import pandas as pd
import pdfplumber
import base64
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="VetLabAI | Diagnostic System", layout="wide")

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- PDF GÖRÜNTÜLEME ---
def pdf_goruntule(pdf_bytes):
    try:
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception:
        st.error("Bu dosya önizleme için uygun değil. Lütfen dosyayı tekrar yükleyin.")

# --- GELİŞMİŞ TEŞHİS MOTORU (Daha Esnek Arama) ---
def vaka_analiz_motoru(tahlil_metni, kütüphane):
    teshisler = []
    tahlil_metni = tahlil_metni.lower()
    for makale in kütüphane:
        skor = 0
        eslesenler = []
        icerik = makale["İçerik"].lower()
        
        # Kritik parametreler ve makale içi anahtar kelimeler
        parametreler = {
            "HGB": ["hemoglobin", "hgb", "anemi", "düşük"],
            "FE": ["demir", "serum demir", "fe", "hipoferremi", "eksikliği"],
            "FERRITIN": ["ferritin", "depo demir", "azalma"],
            "RBC": ["alyuvar", "rbc", "eritrosit", "kırmızı kan"]
        }
        
        for p_key, keywords in parametreler.items():
            if any(k in icerik for k in keywords) and (p_key.lower() in tahlil_metni or any(k in tahlil_metni for k in keywords)):
                skor += 1
                eslesenler.append(p_key)
        
        if skor >= 1: # Eşleşme hassasiyetini artırdık
            teshisler.append({
                "Hastalık": makale["Başlık"],
                "Güven": f"%{min(skor * 30 + 10, 99)}",
                "Kanıtlar": ", ".join(eslesenler)
            })
    return teshisler

# --- GİRİŞ ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Giriş")
    user = st.text_input("Kullanıcı Adı")
    pw = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if user == "admin" and pw == "vetlab2026":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- SIDEBAR ---
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 Teşhis Paneli", "📚 Vaka Arşivi", "⚙️ AI Eğitim & Kütüphane"])

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Klinik Durum")
    st.metric("Toplam Vaka", len(st.session_state.vaka_arsivi))
    st.metric("Öğrenilen Makale", len(st.session_state.kutuphane))

# --- 2. TEŞHİS PANELİ ---
elif menu == "🔬 Teşhis Paneli":
    st.header("🔬 Akıllı Teşhis")
    up = st.file_uploader("Tahlil Dosyası", type=["pdf", "jpg", "png"])
    if up:
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Hasta Adı")
            age = st.number_input("Yaş", 0, 30)
        with col2:
            breed = st.text_input("Irk")
            gender = st.selectbox("Cinsiyet", ["Erkek", "Dişi"])
            
        if st.button("AI Analizini Başlat"):
            tahlil_text = ""
            if up.type == "application/pdf":
                with pdfplumber.open(up) as pdf:
                    tahlil_text = "".join([p.extract_text() or "" for p in pdf.pages])
            else:
                tahlil_text = up.name # Görsel ismi üzerinden basit eşleşme
            
            sonuclar = vaka_analiz_motoru(tahlil_text, st.session_state.kutuphane)
            if sonuclar:
                for s in sonuclar:
                    st.success(f"### 🎯 Teşhis: {s['Hastalık']}")
                    st.write(f"**Güven Oranı:** {s['Güven']} | **Kanıtlar:** {s['Kanıtlar']}")
                    st.session_state.vaka_arsivi.append({
                        "Tarih": datetime.now().strftime("%d/%m/%Y"),
                        "Hasta": name, "Teşhis": s['Hastalık']
                    })
            else: st.warning("Eşleşme bulunamadı. Lütfen kütüphanedeki makale başlığını ve içeriğini kontrol edin.")

# --- 3. VAKA ARŞİVİ ---
elif menu == "📚 Vaka Arşivi":
    st.header("📖 Kayıt Arşivi")
    if st.session_state.vaka_arsivi:
        st.table(pd.DataFrame(st.session_state.vaka_arsivi))
    else: st.info("Kayıt yok.")

# --- 4. AI EĞİTİM & KÜTÜPHANE ---
elif menu == "⚙️ AI Eğitim & Kütüphane":
    st.header("📚 Kaynak Yönetimi")
    new_pdf = st.file_uploader("Yeni Makale Yükle", type="pdf")
    if new_pdf and st.button("Bilgiyi Kaydet"):
        with pdfplumber.open(new_pdf) as pdf:
            text = "".join([p.extract_text() or "" for p in pdf.pages])
        st.session_state.kutuphane.append({
            "Başlık": new_pdf.name, 
            "İçerik": text, 
            "Raw": new_pdf.getvalue()
        })
        st.success("Öğrenildi!")

    if st.button("🚨 Kütüphaneyi Sıfırla (Hataları Temizler)"):
        st.session_state.kutuphane = []
        st.rerun()

    st.divider()
    for idx, makale in enumerate(st.session_state.kutuphane):
        col_a, col_b, col_c = st.columns([3, 1, 1])
        with col_a:
            st.session_state.kutuphane[idx]['Başlık'] = st.text_input(f"İsim {idx+1}", value=makale['Başlık'], key=f"t_{idx}")
        with col_b:
            # Hata denetimi: Eğer Raw verisi varsa butonu göster
            if "Raw" in makale and st.button("📄 PDF Aç", key=f"o_{idx}"):
                pdf_goruntule(makale['Raw'])
        with col_c:
            if st.button("🗑 Sil", key=f"d_{idx}"):
                st.session_state.kutuphane.pop(idx)
                st.rerun()
