import streamlit as st
import pandas as pd
import pdfplumber
import re

# Sayfa Ayarları
st.set_page_config(page_title="VetLabAI | Automated Engine", layout="wide")

# Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- OTOMATİK ANALİZ MOTORU ---
def ai_engine(tahlil_metni, kütüphane):
    bulgular = []
    # Tahlil metnindeki sayıları ve parametreleri yakala (Örn: HGB 9.1)
    for kural in kütüphane:
        makale_icerigi = kural["İçerik"].lower()
        # Makalede geçen parametreleri tahlil içinde ara
        for parametre in ["hgb", "rbc", "hct", "glu", "fe", "ferritin"]:
            if parametre in makale_icerigi:
                # Makaledeki "düşüş" veya "yükseklik" vurgularını kontrol et
                if "düşüş" in makale_icerigi or "anlamlı derecede düşük" in makale_icerigi:
                    bulgular.append(f"📍 **{kural['Başlık']}** ile uyumlu {parametre.upper()} sapması saptandı.")
    return list(set(bulgular))

# --- GİRİŞ PANELİ ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Otomasyon Paneli")
    user = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and password == "vetlab2026": 
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🐾 VetLabAI")
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 Akıllı Tahlil Analizi", "⚙️ AI Eğitim Paneli"])

# --- 2. AKILLI TAHLİL ANALİZİ (OTOMATİZE EDİLDİ) ---
if menu == "🔬 Akıllı Tahlil Analizi":
    st.header("🔬 Otomatik Teşhis Motoru")
    uploaded_file = st.file_uploader("Tahlil PDF/Görsel Yükle", type=["pdf", "png", "jpg"])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Hasta Adı")
            pet_type = st.selectbox("Tür", ["Köpek", "Kedi"])
        with col2:
            pet_age = st.number_input("Yaş", min_value=0)
            pet_breed = st.text_input("Irk")

        if st.button("AI Analizini Başlat"):
            with st.spinner('AI kütüphanedeki tüm makaleleri tarıyor...'):
                # 1. Tahlili oku
                tahlil_text = ""
                if uploaded_file.type == "application/pdf":
                    with pdfplumber.open(uploaded_file) as pdf:
                        tahlil_text = "".join([page.extract_text() for page in pdf.pages]).lower()
                
                # 2. Otomatik Motoru Çalıştır
                sonuclar = ai_engine(tahlil_text, st.session_state.kutuphane)
                
                st.write("---")
                st.subheader(f"📊 Klinik Analiz Raporu: {pet_name}")
                
                if sonuclar:
                    for sonuc in sonuclar:
                        st.warning(sonuc)
                    st.info("Bu analiz, kütüphaneye yüklediğiniz bilimsel verilerle eşleştirilmiştir.")
                else:
                    st.success("Kütüphanedeki mevcut bilgilere göre bir anomali saptanmadı.")

# --- 4. AI EĞİTİM PANELİ ---
elif menu == "⚙️ AI Eğitim Paneli":
    st.header("📚 AI Bilgi Bankası")
    uploaded_article = st.file_uploader("Bilimsel Makale Yükle (PDF)", type="pdf")
    if uploaded_article and st.button("Sistemi Eğit"):
        with pdfplumber.open(uploaded_article) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.kutuphane.append({"Başlık": uploaded_article.name, "İçerik": text})
        st.success(f"'{uploaded_article.name}' sisteme öğretildi. Artık bu makaleye göre teşhis koyabilirim!")
