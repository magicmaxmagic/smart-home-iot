import streamlit as st
import pandas as pd
import requests
import json
import altair as alt

def fetch_data_from_api(api_url):
    """Récupère les données depuis l'API Gateway et les transforme en JSON utilisable."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Vérifie si l'API renvoie une erreur

        # 🔹 Désérialiser le JSON correctement
        data = response.json()

        # ✅ Vérifier si `body` est une string encodée et la convertir en JSON
        if isinstance(data, dict) and "body" in data:
            data = json.loads(data["body"])  # Convertir `body` en vrai JSON

        # Debug: afficher la réponse après transformation
        st.write("✅ Données transformées :", data)

        return data

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Réponse JSON invalide depuis l'API.")
        return None

def display_timeseries_from_api(api_url):
    """Affiche un graphique de séries temporelles des données de l'API."""
    data = fetch_data_from_api(api_url)

    if data:
        try:
            # Debugging: afficher les données brutes reçues
            st.write("🔍 Données après conversion :", data)

            # Vérifier que `data` est une liste
            if isinstance(data, str):
                data = json.loads(data)  # Conversion si encore sous forme de string

            if not isinstance(data, list):
                st.error("⚠ Erreur : Les données ne sont pas sous forme de liste JSON.")
                return

            # Vérifier si `timestamp` est bien présent dans chaque élément
            for item in data:
                if "timestamp" not in item:
                    st.error(f"⚠ Erreur : 'timestamp' absent dans {item}")
                    return

            # Préparation des données pour affichage
            flattened_data = []
            for item in data:
                payload = item.get("payload", {})
                acceleration = payload.get("acceleration", {})
                timestamp = item.get("timestamp")
                sensor_id = item.get("sensor_id", "Unknown")

                if timestamp is not None:
                    flattened_data.append({
                        "timestamp": timestamp,
                        "sensor_id": sensor_id,
                        "x": acceleration.get("x"),
                        "y": acceleration.get("y"),
                        "z": acceleration.get("z"),
                    })

            # Convertir en DataFrame
            df = pd.DataFrame(flattened_data)
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
            df = df.set_index("timestamp")

            # Melt les colonnes pour affichage
            df_melted = df.reset_index().melt("timestamp", var_name="variable", value_name="value")

            # Affichage avec Altair
            chart = alt.Chart(df_melted).mark_line().encode(
                x="timestamp:T",
                y="value:Q",
                color="variable:N",
                tooltip=["timestamp", "variable", "value"]
            ).properties(
                width=800,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
            
def main():
    st.title("📊 Dashboard Temps Réel - MPU6050")
    
    api_url = "https://xz0syz1fc6.execute-api.ca-central-1.amazonaws.com/prod/data"

    # Bouton pour rafraîchir les données
    if st.button("🔄 Rafraîchir les données"):
        display_timeseries_from_api(api_url)

    # Chargement initial des données
    display_timeseries_from_api(api_url)

if __name__ == "__main__":
    main()