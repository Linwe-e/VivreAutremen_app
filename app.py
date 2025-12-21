import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Matériauthèque - Vivre Autrement", page_icon="🛠️", layout="wide")
st.title("🛠️ Matériauthèque - Vivre Autrement")

# -----------------------------------------------------
# 1. Connexion Google Sheets
# -----------------------------------------------------

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


@st.cache_data(ttl=60)
def load_data():
    """Charge les données depuis Google Sheets."""
    client = get_gspread_client()
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(spreadsheet_url)

    # Charge automatiquement la 1ère feuille
    worksheet = sheet.get_worksheet(0)

    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    return df, worksheet


# -----------------------------------------------------
# 2. MAIN : Affichage + interface
# -----------------------------------------------------

try:
    df, worksheet = load_data()

    required_cols = ["Objet", "Statut", "Emprunteur"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Colonnes obligatoires manquantes : {required_cols}")
        st.stop()

    st.success(f"📦 {len(df)} objets dans la matériauthèque")

    st.subheader("📋 Liste complète")
    st.dataframe(df, use_container_width=True)

    # -----------------------------------------------------
    # Zone emprunt / rendu
    # -----------------------------------------------------

    st.divider()
    st.subheader("🔄 Emprunter / Rendre un objet")

    obj_list = df["Objet"].tolist()
    selected_obj = st.selectbox("Choisissez un objet :", obj_list)

    obj_row_index = df.index[df["Objet"] == selected_obj][0]
    statut = df.loc[obj_row_index, "Statut"]
    emprunteur = df.loc[obj_row_index, "Emprunteur"]

    st.write(f"➡️ **Statut actuel :** {statut}")
    if emprunteur:
        st.write(f"👤 **Emprunteur actuel :** {emprunteur}")

    # --- Emprunter ---
    if statut == "Libre":
        new_user = st.text_input("Votre nom pour l'emprunt :")
        if st.button("📥 Emprunter"):
            if new_user.strip() == "":
                st.warning("Veuillez indiquer votre nom.")
            else:
                worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Statut") + 1, "Emprunté")
                worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Emprunteur") + 1, new_user)
                st.success(f"🎉 {selected_obj} a été emprunté par {new_user} !")

    # --- Rendre ---
    if statut == "Prêt en cours":
        if st.button("📤 Rendre l'objet"):
            worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Statut") + 1, "Disponible")
            worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Emprunteur") + 1, "")
            st.success(f"👍 {selected_obj} a été rendu !")

except Exception as e:
    st.error("❌ Impossible de charger les données")
    st.info("Vérifiez que le service account a accès au Google Sheet.")
    with st.expander("🔍 Détails de l'erreur"):
        st.code(str(e))
