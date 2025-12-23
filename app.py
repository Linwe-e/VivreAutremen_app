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

def get_gspread_client():
    """Crée un client Google Sheets authentifié (sans cache pour éviter les sessions expirées)."""
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
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df


def get_worksheet():
    """Retourne un worksheet frais pour les opérations d'écriture."""
    client = get_gspread_client()
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(spreadsheet_url)
    return sheet.get_worksheet(0)


# -----------------------------------------------------
# 2. MAIN : Affichage + interface
# -----------------------------------------------------

try:
    df = load_data()

    required_cols = ["Objet", "Statut", "Emprunteur"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Colonnes obligatoires manquantes : {required_cols}")
        st.stop()

    st.success(f"📦 {len(df)} objets dans la matériauthèque")

    st.subheader("📋 Liste complète")
    st.dataframe(df, width='stretch')

    # -----------------------------------------------------
    # Ajouter un nouvel objet
    # -----------------------------------------------------
    st.divider()
    
    if st.button("➕ Ajouter un nouvel objet"):
        st.session_state["show_add_form"] = True
    
    if st.session_state.get("show_add_form", False):
        with st.form("add_objet_form", clear_on_submit=True):
            st.subheader("Nouvel objet")
            new_objet = st.text_input("Nom de l'objet :")
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("✅ Ajouter", width='stretch')
            with col2:
                cancelled = st.form_submit_button("❌ Annuler", width='stretch')
            
            if cancelled:
                st.session_state["show_add_form"] = False
                st.rerun()
                
            if submitted:
                if new_objet.strip() == "":
                    st.warning("Veuillez indiquer un nom d'objet.")
                else:
                    try:
                        worksheet = get_worksheet()
                        worksheet.append_row([new_objet, "Libre", ""])
                        
                        # Vider le cache
                        load_data.clear()
                        
                        st.session_state["show_add_form"] = False
                        st.success(f"🎉 L'objet '{new_objet}' a été ajouté !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'ajout : {e}")

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
                try:
                    # Créer une connexion fraîche pour l'écriture
                    worksheet = get_worksheet()
                    worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Statut") + 1, "Prêt en cours")
                    worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Emprunteur") + 1, new_user)
                    
                    # Vider le cache
                    load_data.clear()
                    
                    st.success(f"🎉 {selected_obj} a été emprunté par {new_user} !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'emprunt : {e}")

    # --- Rendre ---
    if statut == "Prêt en cours":
        if st.button("📤 Rendre l'objet"):
            try:
                # Créer une connexion fraîche pour l'écriture
                worksheet = get_worksheet()
                worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Statut") + 1, "Libre")
                worksheet.update_cell(obj_row_index + 2, df.columns.get_loc("Emprunteur") + 1, "")
            
                # Vider le cache
                load_data.clear()
                
                st.success(f"👍 {selected_obj} a été rendu !")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors du rendu : {e}")

except Exception as e:
    st.error("❌ Impossible de charger les données")
    st.info("Vérifiez que le service account a accès au Google Sheet.")
    with st.expander("🔍 Détails de l'erreur"):
        st.code(str(e))
