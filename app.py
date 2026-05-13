import streamlit as st
import pandas as pd
import pdfplumber
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="VetLabAI | Diagnostic System", layout="wide")

# --- SESSION STATE (Veri Koruma) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

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
            ozet_neden = "Bilimsel veriler; yetersiz beslenme veya kronik süreçlere işaret etmektedir."
            if "demir" in icerik or "anemi" in icerik:
                ozet_neden = "Makale verilerine göre: Genç hayvanlarda yetersiz demir alımı veya paraziter yük temel nedendir."
            
            teshisler.append({
                "Hastalık": makale["Başlık"],
                "Güven": f"%{min(skor * 25, 98)}",
                "Kanıtlar": ", ".join(eslesen_parametreler),
                "Analiz": ozet_neden
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
st.sidebar.write(f"Kullanıcı: **Bertuğ Ege Sargın**")
menu = st.sidebar.radio("Menü", ["📊 Dashboard", "🔬 Teşhis Paneli", "📚 Vaka Arşivi", "⚙️ AI Eğitim & Kütüphane"])

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Klinik Durum Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Vaka Arşivi", len(st.session_state.vaka_arsivi))
    c2.metric("Öğrenilen Makale", len(st.session_state.kutuphane))
    c3.metric("AI Kapasitesi", "Dinamik")

# --- 2. TEŞHİS PANELİ ---
elif menu == "🔬 Teşhis Paneli":
    st.header("🔬 Akıllı Teşhis Paneli")
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
                    tahlil_text = "".join([p.extract_text() for p in pdf.pages]).lower()
            
            sonuclar = vaka_analiz_motoru(tahlil_text, st.session_state.kutuphane)
            
            if sonuclar:
                for s in sonuclar:
                    st.success(f"### 🎯 Teşhis: {s['Hastalık']}")
                    st.write(f"**Güven Oranı:** {s['Güven']}")
                    st.info(f"**🔍 Bilimsel Analiz:** {s['Analiz']}")
                    
                    st.session_state.vaka_arsivi.append({
                        "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Hasta": name, 
                        "Tür/Irk": breed,
                        "Teşhis": s['Hastalık'],
                        "Güven": s['Güven']
                    })
            else:
                st.warning("Eşleşen bir hastalık bulunamadı.")

# --- 3. VAKA ARŞİVİ ---
elif menu == "📚 Vaka Arşivi":
    st.header("📖 Klinik Kayıt Arşivi")
    if st.session_state.vaka_arsivi:
        df = pd.DataFrame(st.session_state.vaka_arsivi)
        st.dataframe(df, use_container_width=True)
        if st.button("Arşivi Temizle"):
            st.session_state.vaka_arsivi = []
            st.rerun()
    else:
        st.info("Henüz kaydedilmiş bir vaka bulunmuyor.")

# --- 4. AI EĞİTİM & KÜTÜPHANE ---
elif menu == "⚙️ AI Eğitim & Kütüphane":
    st.header("📚 AI Bilgi Bankası Yönetimi")
    
    new_pdf = st.file_uploader("Yeni Makale Yükle (PDF)", type="pdf")
    if new_pdf and st.button("Bilgiyi Kaydet"):
        with pdfplumber.open(new_pdf) as pdf:
            text = "".join([p.extract_text() for p in pdf.pages])
        st.session_state.kutuphane.append({"Başlık": new_pdf.name, "İçerik": text})
        st.success("Öğrenildi!")

    st.divider()
    st.subheader("📖 Öğrenilen Kaynaklar ve İsim Düzenleme")
    
    if st.session_state.kutuphane:
        for idx, makale in enumerate(st.session_state.kutuphane):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                yeni_isim = st.text_input(f"Kaynak {idx+1} İsmi", value=makale['Başlık'], key=f"edit_{idx}")
                if yeni_isim != makale['Başlık']:
                    st.session_state.kutuphane[idx]['Başlık'] = yeni_isim
            with col_b:
                st.write(" ") # Hizalama için
                if st.button("Kaydı Sil", key=f"del_{idx}"):
                    st.session_state.kutuphane.pop(idx)
                    st.rerun()
    else:
        st.info("Kütüphane boş.")
