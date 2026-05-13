import streamlit as st
import pandas as pd

# Sayfa Ayarları ve Tasarım Renkleri (Senin Tasarımlarına Uygun)
st.set_page_config(page_title="VetLabAI - Klinik Destek", layout="wide")

# Sidebar - Menü (Görsel 1'deki Sol Panel)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/194/194279.png", width=100)
st.sidebar.title("VetLabAI")
menu = st.sidebar.radio("Menü", ["Dashboard", "Yeni Analiz", "Vaka Arşivi", "Admin Paneli"])

# Veritabanı Simülasyonu (Hafıza)
if 'kurallar' not in st.session_state:
    st.session_state.kurallar = []
if 'vakalar' not in st.session_state:
    st.session_state.vakalar = []

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    st.title("Hoş geldiniz, Hekim 👋")
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Analiz", len(st.session_state.vakalar), "+%18")
    col2.metric("Aktif Abone", "1.248", "+23")
    col3.metric("Sistem Gücü", "Premium", "Aktif")
    st.image("https://i.imgur.com/r6O0GjN.png") # Placeholder görsel

# --- 2. YENİ ANALİZ (Görsel 2) ---
elif menu == "Yeni Analiz":
    st.header("🔬 Tahlil Analiz Et")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        tur = st.selectbox("Tür Seçimi", ["Kedi", "Köpek"])
        glu = st.number_input("GLU (Glikoz) Değeri - mg/dL", min_value=0)
        btn_analiz = st.button("Analiz Et")

    if btn_analiz:
        st.subheader("AI Destekli Olası Tanılar")
        bulundu = False
        for kural in st.session_state.kurallar:
            if kural['tur'] == tur and glu > kural['esik']:
                st.warning(f"📍 {kural['ad']} (%92 Olasılık)")
                st.info(f"**Neden?** {glu} mg/dL değeri belirlenen {kural['esik']} eşiğinin üzerindedir.")
                st.write(f"**Hekim Notu:** {kural['not']}")
                bulundu = True
        
        if not bulundu:
            st.success("Analiz Sonucu: Normal. Belirlenen kurallar dahilinde bir risk saptanmadı.")
        
        # Onay Butonu Ekliyoruz!
        st.write("---")
        st.write("### Bu tanı doğru mu?")
        c1, c2 = st.columns(2)
        if c1.button("✅ Evet, Doğru"):
            st.success("Geri bildiriminiz kaydedildi. AI kendini optimize ediyor!")
            st.session_state.vakalar.append({"tur": tur, "deger": glu, "sonuc": "Doğru"})
        if c2.button("❌ Hayır, Yanlış"):
            st.error("Bildirim Admin'e iletildi. Kuralı gözden geçireceğiz.")

# --- 4. ADMIN PANELI (Görsel 3) ---
elif menu == "Admin Paneli":
    st.header("⚙️ Admin Yönetim Paneli")
    st.subheader("Yeni Kural / Bilgi Ekle")
    
    with st.form("yeni_kural"):
        k_ad = st.text_input("Kural Adı", "Diyabet Şüphesi")
        k_tur = st.selectbox("Tür", ["Kedi", "Köpek"])
        k_esik = st.number_input("Eşik Değeri (GLU > ...)", value=180)
        k_not = st.text_area("Hekime Gösterilecek Not", "Fruktozamin testi önerilir. Kedilerde stres faktörünü dışlayın.")
        kaydet = st.form_submit_button("Sisteme Kaydet ve Yayınla")
        
        if kaydet:
            st.session_state.kurallar.append({"ad": k_ad, "tur": k_tur, "esik": k_esik, "not": k_not})
            st.success(f"{k_ad} kuralı tüm sistemde aktif edildi!")

    st.write("### Mevcut Kurallar")
    st.table(pd.DataFrame(st.session_state.kurallar))
