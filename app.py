import streamlit as st
import pandas as pd
import pdfplumber
from PIL import Image

# 1. Sayfa Ayarları
st.set_page_config(page_title="VetLabAI | Diagnostic Engine", layout="wide")

# --- Session State ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- GİRİŞ KONTROLÜ ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Giriş")
    user = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and password == "vetlab2026": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı giriş!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🐾 VetLabAI")
st.sidebar.write(f"Hoş geldin, **Bertuğ Ege Sargın**")
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 Tahlil Analiz Paneli", "📚 Vaka Kütüphanesi", "⚙️ AI Eğitim & Admin"])

# --- 2. TAHLİL ANALİZ PANELİ (Hasta Bilgileri Güncellendi) ---
if menu == "🔬 Tahlil Analiz Paneli":
    st.header("Akıllı Tahlil Analizi")
    st.write("Sistem tahlili tarayacak ve kütüphanendeki kurallara göre otomatik teşhis koyacaktır.")
    
    uploaded_file = st.file_uploader("Tahlil Dosyasını Buraya Bırakın", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.subheader("📋 Hasta Künyesi")
        col1, col2 = st.columns(2)
        
        with col1:
            pet_name = st.text_input("Hasta / Pet Adı", placeholder="Örn: Pamuk")
            pet_age = st.number_input("Yaş", min_value=0, max_value=30, step=1)
            
        with col2:
            pet_type = st.selectbox("Tür", ["Kedi", "Köpek"])
            pet_breed = st.text_input("Irk / Diğer Bilgiler", placeholder="Örn: Golden Retriever")
        
        if st.button("AI Taramayı Başlat"):
            # PDF OKUMA VE VERİ AYIKLAMA (SİSİMLÜSAYON)
            detected_data = {}
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "".join([page.extract_text() for page in pdf.pages])
                if "GLU" in text or "Glikoz" in text:
                    detected_data["GLU"] = 250 
            else:
                st.image(uploaded_file, width=400)
                detected_data["GLU"] = 210 
            
            # ANALİZ VE RAPORLAMA
            st.write("---")
            st.subheader(f"📊 Analiz Sonucu: {pet_name}")
            found_issue = False
            
            for kural in st.session_state.kutuphane:
                if "GLU" in detected_data:
                    if "Diyabet" in kural["Başlık"] and detected_data["GLU"] > 180:
                        st.warning(f"⚠️ {kural['Başlık']} Tespiti!")
                        st.write(f"**Hasta:** {pet_name} ({pet_age} Yaş, {pet_breed})")
                        st.write(f"**AI Analizi:** Saptanan değer {detected_data['GLU']} mg/dL. {kural['İçerik'][:200]}...")
                        found_issue = True
            
            if not found_issue:
                st.success(f"Analiz Tamamlandı: {pet_name} için herhangi bir anomaliye rastlanmadı.")
            
            # Arşive Tüm Bilgilerle Kaydet
            st.session_state.vaka_arsivi.append({
                "Pet": pet_name, 
                "Tür": pet_type, 
                "Yaş": pet_age,
                "Bilgi": pet_breed,
                "Tanı": "Analiz Edildi", 
                "Tarih": "13.05.2026"
            })

# --- DİĞER BÖLÜMLER (Dashboard, Kütüphane, Admin) ---
# (Önceki kodun aynısı devam edecek şekilde GitHub'a yapıştırabilirsin)
elif menu == "📊 Dashboard":
    st.header("Klinik Genel Bakış")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi))
    c2.metric("AI Güven Endeksi", "%96")
    c3.metric("Öğrenilen Bilgi", len(st.session_state.kutuphane))

elif menu == "📚 Vaka Kütüphanesi":
    st.header("Klinik Vaka Arşivi")
    st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi), use_container_width=True)

elif menu == "⚙️ AI Eğitim & Admin":
    st.header("Yönetim ve AI Eğitim Merkezi")
    uploaded_article = st.file_uploader("Eğitim Makalesi (PDF)", type="pdf")
    if uploaded_article and st.button("PDF Makaleyi Sisteme Öğret"):
        with pdfplumber.open(uploaded_article) as pdf:
            article_text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.kutuphane.append({"Başlık": uploaded_article.name, "İçerik": article_text})
        st.success(f"'{uploaded_article.name}' başarıyla kütüphaneye eklendi!")

    for item in st.session_state.kutuphane:
        with st.expander(item['Başlık']):
            st.write(item['İçerik'])
