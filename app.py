import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

st.title("🛠️ Matériauthèque - Vivre Autrement")

@st.cache_resource
def get_gspread_client():
    """Crée et met en cache le client Google Sheets authentifié."""
    service_account_info = st.secrets["connections"]["gsheets"]["service_account"]
    
    if isinstance(service_account_info, str):
        service_account_info = json.loads(service_account_info)
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes
    )
    
    return gspread.authorize(credentials)

@st.cache_data(ttl=600)  # Cache pendant 10 minutes
def load_data():
    """Charge les données depuis Google Sheets."""
    client = get_gspread_client()
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = client.open_by_url(spreadsheet_url)
    worksheet = sh.worksheet("Feuille1")
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

try:
    df = load_data()
    
    st.success(f"✅ {len(df)} objets dans la matériauthèque")
    
    # Affichage des données
    st.dataframe(df, use_container_width=True)
    
    # Exemple d'affichage personnalisé (adaptez selon vos colonnes)
    st.subheader("📋 Liste des objets")
    for idx, row in df.iterrows():
        # Adaptez les noms de colonnes selon votre feuille
        cols = df.columns.tolist()
        if len(cols) > 0:
            st.write(f"• {row[cols[0]]}")

except Exception as e:
    st.error("❌ Impossible de charger les données")
    st.info("Vérifiez que la feuille 'Feuille1' existe et que le service account a accès au Google Sheet.")
    
    with st.expander("🔍 Détails de l'erreur"):
        st.code(str(e))