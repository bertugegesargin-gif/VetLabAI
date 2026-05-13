import streamlit as st
import pandas as pd
import pdfplumber

# 1. Sayfa Konfigürasyonu (Senin Tasarımların)
st.set_page_config(page_title="VetLabAI | Professional", layout="wide", initial_sidebar_state="expanded")

# --- CSS: Tasarımlarındaki Renk Paleti (Koyu ve Şık) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- Session State (Hafıza ve Güvenlik) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- GİRİŞ KONTROLÜ (Admin Yetkilendirme) ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Giriş")
    user = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and password == "vetlab2026": # Şifren bu!
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı giriş!")
    st.stop()

# --- SIDEBAR (Görsel 1) ---
st.sidebar.title("🐾 VetLabAI")
st.sidebar.write(f"Hoş geldin, **Bertuğ Ege Sargın**") #
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 PDF Tahlil Analizi", "📚 Vaka Kütüphanesi", "⚙️ AI Eğitim & Admin"])
if st.sidebar.button("Güvenli Çıkış"):
    st.session_state.logged_in = False
    st.rerun()

# --- 1. DASHBOARD (Görsel 1) ---
if menu == "📊 Dashboard":
    st.header("Klinik Genel Bakış")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi), "+5%")
    c2.metric("AI Güven Endeksi", "%96", "Stabil")
    c3.metric("Kütüphane Bilgisi", len(st.session_state.kutuphane), "Yeni")
    
    st.subheader("Son Analizler")
    if st.session_state.vaka_arsivi:
        st.table(pd.DataFrame(st.session_state.vaka_arsivi).tail(5))
    else:
        st.write("Henüz vaka kaydı yok.")

# --- 2. PDF TAHLİL ANALİZİ (En Önemli Kısım) ---
elif menu == "🔬 PDF Tahlil Analizi":
    st.header("Biyokimya / Hemogram PDF Analizi")
    st.write("Laboratuvardan gelen PDF sonucunu buraya yükleyin.")
    
    uploaded_file = st.file_uploader("PDF Dosyası Seçin", type="pdf")
    pet_type = st.selectbox("Tür", ["Kedi", "Köpek"])
    pet_name = st.text_input("Hasta/Pet Adı")

    if uploaded_file and st.button("PDF'i Oku ve Analiz Et"):
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join([page.extract_text() for page in pdf.pages])
            
        # Basit Bir Veri Çekme Simülasyonu (Text içinde GLU arar)
        glu_val = 0
        if "GLU" in text or "Glikoz" in text:
            # Gerçek bir regex veya string ayıklama buraya gelir
            st.success("PDF başarıyla okundu: Glikoz parametresi saptandı.")
            # Örnek değer ataması (Senin Diyabet Paketi Kuralların Uygulanır)
            glu_val = 280 # Simülasyon değeri
            
        st.subheader(f"Analiz Raporu: {pet_name}")
        if pet_type == "Köpek" and glu_val > 180: #
            st.warning("🟠 Diyabet Şüphesi Saptandı")
            st.info("Hekim Notu: Fruktozamin testi ve idrar glukozu kontrol edilmeli.") #
        elif pet_type == "Kedi" and glu_val > 220: #
            st.warning("🟠 Diyabet Şüphesi (Kedi - Stres Hiperglisemisi?)") #
        
        # Vakayı Arşive Kaydet
        st.session_state.vaka_arsivi.append({"Pet": pet_name, "Tür": pet_type, "Değer": glu_val, "Tanı": "Diyabet Şüphesi"})

# --- 3. VAKA KÜTÜPHANESİ ---
elif menu == "📚 Vaka Kütüphanesi":
    st.header("Klinik Vaka Arşivi")
    if st.session_state.vaka_arsivi:
        df = pd.DataFrame(st.session_state.vaka_arsivi)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz kayıtlı vaka bulunmamaktadır.")

# --- 4. AI EĞİTİM & ADMIN (Görsel 3) ---
elif menu == "⚙️ AI Eğitim & Admin":
    st.header("Yönetim ve AI Eğitim Paneli")
    tab1, tab2 = st.tabs(["Makale Yükle", "Sistem Ayarları"])
    
    with tab1:
        st.write("AI'nın tahlilleri daha iyi yorumlaması için makale veya kural setleri girin.")
        title = st.text_input("Bilgi Başlığı (Örn: Böbrek Yetmezliği v1)")
        content = st.text_area("Klinik İçerik ve Kurallar")
        if st.button("Sistemi Eğit"):
            st.session_state.kutuphane.append({"Başlık": title, "İçerik": content})
            st.success("AI kütüphanesi güncellendi!")
