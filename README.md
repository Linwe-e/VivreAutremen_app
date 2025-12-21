# 🛠️ Matériauthèque - Vivre Autrement

> **Une application légère pour gérer le partage de matériel au sein de notre habitat groupé.**

Ce projet vise à simplifier la vie collective en permettant à chacun de visualiser, emprunter et gérer le matériel commun (outillage, cuisine, jardinage) via une interface simple, sans passer par des solutions propriétaires complexes.

## 🎯 Objectifs

- **Centraliser** l'inventaire des objets partagés.
- **Visualiser** la disponibilité en temps réel.
- **Simplifier** l'emprunt pour les membres du groupe (interface "No-Code friendly").
- **Souveraineté des données** : Le backend reste un simple Google Sheet, exportable à tout moment.
- **Sécurité des données** : priorité sur la sécurité et l'éthique

## 🏗️ Architecture Technique

Un projet **Python** pur utilisant la puissance de Streamlit pour le frontend et Google Sheets comme base de données flexible.

- **Langage :** Python 3.x
- **Frontend :** [Streamlit](https://streamlit.io/)
- **Backend / Database :** Google Sheets (Connecté via API)
- **Librairies clés :** `streamlit`, `gspread`, `google-auth`, `pandas`

### Pourquoi `gspread` plutôt que `streamlit-gsheets` ?

Bien que `streamlit-gsheets` soit la connexion officielle de Streamlit, nous avons choisi d'utiliser **`gspread`** (la librairie Python officielle de Google) pour les raisons suivantes :

- ✅ **Fiabilité accrue** : `gspread` gère mieux l'authentification avec les Google Sheets privés
- ✅ **Contrôle total** : Accès direct à l'API Google Sheets sans couche d'abstraction supplémentaire
- ✅ **Meilleure documentation** : Librairie mature et largement utilisée dans la communauté Python
- ✅ **Moins de bugs** : `streamlit-gsheets` peut échouer avec des erreurs 401 sur certaines configurations

## 🚀 Installation & Démarrage local

Si vous souhaitez faire tourner le projet sur votre machine :

### 1. Cloner le projet

```bash
git clone https://github.com/Linwe-e/VivreAutrement_app.git
cd VivreAutrement_app
```

### 2. Environnement virtuel (Recommandé)

```bash
python -m venv venv
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

> Note : Assurez-vous que le fichier requirements.txt contient bien streamlit, gspread, google-auth et pandas

### 4. Configuration des secrets (⚠️ Important)

L'application nécessite des clés d'accès à l'API Google.

#### a. Créer un Service Account sur Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet (ou sélectionnez-en un existant)
3. Activez l'**API Google Sheets** et l'**API Google Drive**
4. Créez un **Service Account** (IAM & Admin > Service Accounts)
5. Téléchargez le fichier JSON des credentials

#### b. Partager votre Google Sheet

1. Ouvrez votre Google Sheet
2. Cliquez sur **Partager**
3. Ajoutez l'email du service account (celui dans `client_email` du JSON) avec les droits de **Lecteur** (ou Éditeur si besoin)

#### c. Configurer secrets.toml

Créez un dossier `.streamlit` à la racine du projet, puis un fichier `secrets.toml` :

```toml
# .streamlit/secrets.toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/VOTRE_ID_ICI/edit"

service_account = """{"type": "service_account", "project_id": "...", "private_key_id": "...", "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n", "client_email": "...", "client_id": "...", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "...", "universe_domain": "googleapis.com"}"""
```

⚠️ **Important** : Le JSON du service account doit être sur **une seule ligne** avec tous les `\n` échappés en `\\n`. Copiez-le depuis le fichier JSON téléchargé de Google Cloud.

### 5. Lancer l'application

```bash
streamlit run app.py
```

## 📂 Structure du projet

```
VivreAutrement-App
 ┣ 📂 .streamlit
 ┃ ┗ 📜 secrets.toml      # (Non versionné - Contient les clés API)
 ┣ 📜 app.py              # Le coeur de l'application
 ┣ 📜 requirements.txt    # Liste des librairies Python
 ┗ 📜 README.md           # Documentation
```

## 🔮 Roadmap (Améliorations futures)

- Filtres : Recherche par catégorie (Jardin, Bricolage, Cuisine).
- Intéractions : Bouton "Emprunter" qui met à jour le Google Sheet directement.
- UI/UX : Affichage en mode "Galerie" avec photos des objets.
- Admin : Page sécurisée pour ajouter de nouveaux objets.

## 🤝 Contribution

Projet interne pour le collectif "Vivre Autrement". Les Pull Requests sont les bienvenues pour améliorer la vie du groupe !

Développé avec ❤️ (et du Python) pour le collectif.