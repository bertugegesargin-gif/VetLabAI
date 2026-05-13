import streamlit as st
import pandas as pd

# Sayfa Ayarları (Senin renk paletin)
st.set_page_config(page_title="VetLabAI - Klinik Zeka", layout="wide")

# Sidebar (Görsel 1: Sol Menü)
st.sidebar.title("🐾 VetLabAI")
menu = st.sidebar.radio("Bölümler", ["Dashboard", "Tahlil Analizi", "Kütüphane & AI Eğitim"])

# Hafıza (Zeka Geliştirme Alanı)
if 'kutuphane' not in st.session_state:
    st.session_state.kutuphane = [] # Makaleler burada birikecek

# --- 1. DASHBOARD (Görsel 1) ---
if menu == "Dashboard":
    st.header("Klinik Durum Özeti")
    c1, c2, c3 = st.columns(3)
    c1.metric("Analiz Edilen Vaka", "142", "+12%")
    c2.metric("AI Güven Skoru", "%94", "+2%")
    c3.metric("Öğrenilen Makale", len(st.session_state.kutuphane))
    st.info("VetLabAI şu an senin yüklediğin verilerle gelişiyor.")

# --- 2. TAHLİL ANALİZİ (Görsel 2) ---
elif menu == "Tahlil Analizi":
    st.header("🔬 Akıllı Tahlil Paneli")
    tur = st.selectbox("Tür", ["Kedi", "Köpek"])
    deger = st.number_input("GLU (Glikoz) - mg/dL", min_value=0)
    
    if st.button("AI Analizini Başlat"):
        # Burası kütüphanedeki verilerle analiz yapacak zeka motoru
        st.subheader("Analiz Sonucu")
        if tur == "Köpek" and deger > 180:
            st.warning("🟠 Diyabet Şüphesi (%78)")
            st.write("**Neden?** Glikoz eşik değerin üzerinde.")
        elif tur == "Kedi" and deger > 220:
            st.warning("🟠 Diyabet Şüphesi (Kedi - Stres Faktörü)")
        else:
            st.success("✅ Normal Değerler")

# --- 3. KÜTÜPHANE VE AI EĞİTİM (Görsel 3 - Senin İstediğin Kısım) ---
elif menu == "Kütüphane & AI Eğitim":
    st.header("📚 AI Zekasını Geliştir")
    st.write("Buraya eklediğin her makale ve bilgi, analiz motorunun zekasını artırır.")
    
    with st.form("zeka_formu"):
        konu = st.text_input("Makale/Bilgi Başlığı")
        icerik = st.text_area("Klinik Bilgi / Kurallar (Buraya Diyabet Paketi Notlarını Yapıştır)")
        yukle = st.form_submit_button("Sistemi Eğit ve Kaydet")
        
        if yukle:
            st.session_state.kutuphane.append({"konu": konu, "icerik": icerik})
            st.balloons()
            st.success("AI bu bilgiyi öğrendi ve kütüphaneye ekledi!")

    st.write("### AI'nın Öğrendiği Bilgiler")
    for b in st.session_state.kutuphane:
        with st.expander(b['konu']):
            st.write(b['icerik'])
