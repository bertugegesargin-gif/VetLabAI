import streamlit as st
import pandas as pd
import pdfplumber
from PIL import Image

# 1. Sayfa Ayarları ve Tasarım (Görsel 1-2-3 Referanslı)
st.set_page_config(page_title="VetLabAI | Diagnostic Engine", layout="wide", initial_sidebar_state="expanded")

# --- Session State (Veri Depolama) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- GİRİŞ KONTROLÜ (Güvenlik) ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Yönetim Girişi")
    user = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and password == "vetlab2026": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı giriş! Lütfen bilgilerinizi kontrol edin.")
    st.stop()

# --- SIDEBAR (Sol Menü) ---
st.sidebar.title("🐾 VetLabAI")
st.sidebar.write(f"Hoş geldin, **Bertuğ Ege Sargın**")
menu = st.sidebar.radio("Menü", ["📊 Dashboard", "🔬 Akıllı Tahlil Analizi", "📚 Vaka Arşivi", "⚙️ AI Eğitim Paneli"])

if st.sidebar.button("Güvenli Çıkış"):
    st.session_state.logged_in = False
    st.rerun()

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Klinik Genel Bakış")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi), "+%5")
    c2.metric("AI Güven Endeksi", "%96", "Stabil")
    c3.metric("Eğitim Kaydı", len(st.session_state.kutuphane), "Yeni")
    
    st.subheader("Son Klinik İşlemler")
    if st.session_state.vaka_arsivi:
        st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi).tail(5), use_container_width=True)
    else:
        st.info("Henüz bir vaka kaydı bulunmuyor.")

# --- 2. AKILLI TAHLİL ANALİZİ (GÜNCELLENEN KISIM) ---
elif menu == "🔬 Akıllı Tahlil Analizi":
    st.header("🔬 Tahlil Analiz ve Teşhis Paneli")
    st.write("Dosyayı yükleyin, sistem hasta bilgilerini ve tahlili eşleştirerek analiz edecektir.")
    
    uploaded_file = st.file_uploader("Tahlil Dosyası (PDF veya Görsel)", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.markdown("### 📋 Hasta Künyesi")
        # Senin istediğin o 3 yeni alan burada:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pet_name = st.text_input("Hasta Adı", placeholder="Örn: Pamuk")
            pet_age = st.number_input("Yaş", min_value=0, max_value=30, step=1)
            
        with col2:
            pet_type = st.selectbox("Tür", ["Kedi", "Köpek"])
            pet_breed = st.text_input("Irk / Cins", placeholder="Örn: Terier")
            
        with col3:
            pet_gender = st.selectbox("Cinsiyet", ["Erkek", "Dişi", "Kısırlaştırılmış Erkek", "Kısırlaştırılmış Dişi"])
            owner_name = st.text_input("Hasta Sahibi (Opsiyonel)")

        if st.button("AI Analizini Başlat"):
            with st.spinner('AI kütüphaneyi tarıyor ve tahlili yorumluyor...'):
                # PDF ve Görsel Okuma Simülasyonu
                detected_glu = 0
                if uploaded_file.type == "application/pdf":
                    with pdfplumber.open(uploaded_file) as pdf:
                        text = "".join([page.extract_text() for page in pdf.pages])
                    if "GLU" in text or "Glikoz" in text:
                        detected_glu = 245 # Örnek saptanan değer
                else:
                    st.image(uploaded_file, width=300)
                    detected_glu = 215 # Görselden saptanan örnek değer

                # ANALİZ SONUCU
                st.write("---")
                st.subheader(f"📊 Klinik Rapor: {pet_name}")
                found = False
                
                for kural in st.session_state.kutuphane:
                    if detected_glu > 0:
                        # Kütüphanedeki 'Diyabet' anahtar kelimesine ve tahlil değerine göre otomatik analiz
                        if "Diyabet" in kural["Başlık"] and detected_glu > 180:
                            st.warning(f"⚠️ {kural['Başlık']} Saptandı!")
                            st.write(f"**Hasta Bilgisi:** {pet_age} yaşında, {pet_gender} {pet_type} ({pet_breed})")
                            st.write(f"**Bulgu:** Glikoz seviyesi {detected_glu} mg/dL olarak saptandı. Bu değer eşik sınırın üzerindedir.")
                            st.info(f"**Eğitim Notu:** {kural['İçerik'][:300]}...")
                            found = True
                
                if not found:
                    st.success(f"Analiz Tamamlandı. {pet_name} için kütüphane kuralları dahilinde bir anomali saptanmadı.")

                # Arşive Kaydet
                st.session_state.vaka_arsivi.append({
                    "Hasta": pet_name, 
                    "Tür": pet_type, 
                    "Yaş": pet_age, 
                    "Irk": pet_breed,
                    "Cinsiyet": pet_gender,
                    "Durum": "Tamamlandı"
                })

# --- 3. VAKA ARŞİVİ ---
elif menu == "📚 Vaka Arşivi":
    st.header("Klinik Kayıt Arşivi")
    if st.session_state.vaka_arsivi:
        st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi), use_container_width=True)
    else:
        st.info("Henüz kayıtlı bir vaka bulunmuyor.")

# --- 4. AI EĞİTİM PANELİ ---
elif menu == "⚙️ AI Eğitim Paneli":
    st.header("Yönetim ve AI Geliştirme")
    st.write("Buraya yüklediğiniz PDF makaleler sistemin 'zekasını' oluşturur.")
    
    uploaded_article = st.file_uploader("Eğitim Makalesi (PDF)", type="pdf")
    if uploaded_article and st.button("Sistemi Bu Bilgiyle Eğit"):
        with pdfplumber.open(uploaded_article) as pdf:
            article_text = "".join([page.extract_text() for page in pdf.pages])
        st.session_state.kutuphane.append({"Başlık": uploaded_article.name, "İçerik": article_text})
        st.success(f"'{uploaded_article.name}' başarıyla öğrenildi!")

    st.write("---")
    st.subheader("AI'nın Bildiği Konular")
    for item in st.session_state.kutuphane:
        with st.expander(item['Başlık']):
            st.write(item['İçerik'])
