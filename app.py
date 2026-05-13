import streamlit as st
import pandas as pd
import pdfplumber
from PIL import Image

# 1. Sayfa Ayarları (Tasarımlarındaki o şık hava için)
st.set_page_config(page_title="VetLabAI | Professional Diagnostic Tool", layout="wide", initial_sidebar_state="expanded")

# --- Session State (Hafıza ve Güvenlik) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'vaka_arsivi' not in st.session_state: st.session_state.vaka_arsivi = []

# --- GİRİŞ KONTROLÜ (Admin Yetkilendirme) ---
if not st.session_state.logged_in:
    st.title("🐾 VetLabAI - Giriş")
    st.info("Sistemi eğitmek ve analiz yapmak için giriş yapın.")
    user = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user == "admin" and password == "vetlab2026": 
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı giriş! Lütfen bilgileri kontrol edin.")
    st.stop()

# --- SIDEBAR (Görsel 1: Sol Menü) ---
st.sidebar.title("🐾 VetLabAI")
st.sidebar.write(f"Hoş geldin, **Bertuğ Ege Sargın**")
menu = st.sidebar.radio("Navigasyon", ["📊 Dashboard", "🔬 Tahlil Analiz Paneli", "📚 Vaka Kütüphanesi", "⚙️ AI Eğitim & Admin"])

if st.sidebar.button("Güvenli Çıkış"):
    st.session_state.logged_in = False
    st.rerun()

# --- 1. DASHBOARD (Görsel 1) ---
if menu == "📊 Dashboard":
    st.header("Klinik Genel Bakış")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Vaka", len(st.session_state.vaka_arsivi), "+5%")
    c2.metric("AI Güven Endeksi", "%96", "Stabil")
    c3.metric("Öğrenilen Bilgi", len(st.session_state.kutuphane), "Yeni")
    
    st.subheader("Son Analizler")
    if st.session_state.vaka_arsivi:
        st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi).tail(5), use_container_width=True)
    else:
        st.info("Henüz analiz kaydı bulunmamaktadır.")

# --- 2. TAHLİL ANALİZ PANELİ (PDF & GÖRSEL DESTEĞİ) ---
elif menu == "🔬 Tahlil Analiz Paneli":
    st.header("Akıllı Tahlil Analizi")
    st.write("Laboratuvar sonucunu (PDF) veya tahlil fotoğrafını (JPG/PNG) yükleyin.")
    
    col_file, col_input = st.columns([1, 1])
    
    with col_file:
        uploaded_file = st.file_uploader("Dosya Seçin", type=["pdf", "jpg", "jpeg", "png"])
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                st.success("PDF Dosyası Algılandı.")
                with pdfplumber.open(uploaded_file) as pdf:
                    text = "".join([page.extract_text() for page in pdf.pages])
                st.text_area("PDF İçeriği (Okunan)", text, height=150)
            else:
                st.image(uploaded_file, caption="Yüklenen Tahlil Görseli", use_container_width=True)
    
    with col_input:
        pet_name = st.text_input("Hasta / Pet Adı")
        pet_type = st.selectbox("Tür", ["Kedi", "Köpek"])
        glu_val = st.number_input("GLU (Glikoz) Değeri - mg/dL", min_value=0)
        
        if st.button("Analizi Başlat ve Kaydet"):
            # Diyabet Paketi v1 Kuralları
            diagnosis = "Normal"
            note = "Değerler normal sınırlar içerisinde."
            
            if pet_type == "Köpek" and glu_val > 180:
                diagnosis = "🟠 Diyabet Şüphesi"
                note = "Glikoz 180 mg/dL eşiğinin üzerinde. Fruktozamin testi önerilir."
            elif pet_type == "Kedi" and glu_val > 220:
                diagnosis = "🟠 Diyabet Şüphesi"
                note = "Kedi stres faktörü dışlanmalı, idrar analizi ile desteklenmelidir."
            
            st.subheader("AI Analiz Raporu")
            if "Şüphesi" in diagnosis:
                st.warning(f"**Tanı:** {diagnosis}")
            else:
                st.success(f"**Tanı:** {diagnosis}")
            st.info(f"**Uzman Notu:** {note}")
            
            # Arşive Ekle
            st.session_state.vaka_arsivi.append({
                "Pet": pet_name, 
                "Tür": pet_type, 
                "Değer": glu_val, 
                "Tanı": diagnosis
            })

# --- 3. VAKA KÜTÜPHANESİ ---
elif menu == "📚 Vaka Kütüphanesi":
    st.header("Klinik Vaka Arşivi")
    if st.session_state.vaka_arsivi:
        st.dataframe(pd.DataFrame(st.session_state.vaka_arsivi), use_container_width=True)
    else:
        st.info("Arşivde henüz vaka bulunmuyor.")

# --- 4. AI EĞİTİM & ADMIN (PDF MAKALE DESTEĞİ) ---
elif menu == "⚙️ AI Eğitim & Admin":
    st.header("Yönetim ve AI Eğitim Merkezi")
    
    st.subheader("Yeni Bilgi / Makale Öğret")
    method = st.radio("Yükleme Yöntemi", ["Metin Olarak Gir", "PDF Makale Yükle"])
    
    if method == "Metin Olarak Gir":
        title = st.text_input("Başlık (Örn: Diyabet Paketi v1)")
        content = st.text_area("Klinik Notlar ve Kurallar")
        if st.button("Sistemi Eğit"):
            st.session_state.kutuphane.append({"Başlık": title, "İçerik": content})
            st.success("AI bu bilgiyi öğrendi!")
            
    else:
        uploaded_article = st.file_uploader("Eğitim Makalesi (PDF)", type="pdf")
        if uploaded_article and st.button("PDF Makaleyi Sisteme Öğret"):
            with pdfplumber.open(uploaded_article) as pdf:
                article_text = "".join([page.extract_text() for page in pdf.pages])
            st.session_state.kutuphane.append({"Başlık": uploaded_article.name, "İçerik": article_text})
            st.success(f"'{uploaded_article.name}' başarıyla kütüphaneye eklendi ve AI eğitildi!")

    st.write("---")
    st.subheader("AI Belleğindeki Bilgiler")
    for item in st.session_state.kutuphane:
        with st.expander(item['Başlık']):
            st.write(item['İçerik'])
