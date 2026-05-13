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

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Klinik Genel Bakış")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi))
    c2.metric("AI Güven Endeksi", "%96")
    c3.metric("Öğrenilen Bilgi", len(st.session_state.kutuphane))

# --- 2. TAHLİL ANALİZ PANELİ (Glikoz Seçimi Kaldırıldı) ---
elif menu == "🔬 Tahlil Analiz Paneli":
    st.header("Akıllı Tahlil Analizi")
    st.write("Sistem tahlili tarayacak ve kütüphanendeki kurallara göre otomatik teşhis koyacaktır.")
    
    uploaded_file = st.file_uploader("Tahlil Dosyasını Buraya Bırakın", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        pet_name = st.text_input("Hasta / Pet Adı")
        pet_type = st.selectbox("Tür", ["Kedi", "Köpek"])
        
        if st.button("AI Taramayı Başlat"):
            # PDF OKUMA VE VERİ AYIKLAMA (SİSİMLÜSAYON)
            detected_data = {}
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "".join([page.extract_text() for page in pdf.pages])
                # Otomatik Değer Bulma (Örn: GLU)
                if "GLU" in text or "Glikoz" in text:
                    detected_data["GLU"] = 250 # Örnek saptanan değer
            else:
                st.image(uploaded_file, width=400)
                detected_data["GLU"] = 210 # Görselden saptanan örnek değer
            
            # KÜTÜPHANE İLE EŞLEŞTİRME VE ANALİZ
            st.subheader("Olası Klinik Bulgular")
            found_issue = False
            
            # Kütüphanedeki kuralları tarar
            for kural in st.session_state.kutuphane:
                if "GLU" in detected_data:
                    # Diyabet Paketi v1 Kuralı Kontrolü (Simülasyon)
                    if "Diyabet" in kural["Başlık"] and detected_data["GLU"] > 180:
                        st.warning(f"⚠️ {kural['Başlık']} Tespiti!")
                        st.write(f"**AI Analizi:** Saptanan değer {detected_data['GLU']} mg/dL. {kural['İçerik'][:200]}...")
                        found_issue = True
            
            if not found_issue:
                st.success("Analiz Tamamlandı: Kütüphanedeki kurallar dahilinde bir anomaliye rastlanmadı.")
            
            # Arşive Ekle
            st.session_state.vaka_arsivi.append({
                "Pet": pet_name, "Tür": pet_type, "Tanı": "Analiz Edildi", "Durum": "Kayıtlı"
            })

# --- 3. VAKA KÜTÜPHANESİ ---
elif menu == "📚 Vaka Kütüphanesi":
    st.header("Klinik Vaka Arşivi")
    st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi), use_container_width=True)

# --- 4. AI EĞİTİM & ADMIN ---
elif menu == "⚙️ AI Eğitim & Admin":
    st.header("Yönetim ve AI Eğitim Merkezi")
    uploaded_article = st.file_uploader("Eğitim Makalesi (PDF)", type="pdf")
    if uploaded_article and st.button("PDF Makaleyi Sisteme Öğret"):
        with pdfplumber.open(uploaded_article) as pdf:
            article_text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.kutuphane.append({"Başlık": uploaded_article.name, "İçerik": article_text})
        st.success(f"'{uploaded_article.name}' başarıyla kütüphaneye eklendi!")

    st.subheader("AI Belleğindeki Bilgiler")
    for item in st.session_state.kutuphane:
        with st.expander(item['Başlık']):
            st.write(item['İçerik'])
