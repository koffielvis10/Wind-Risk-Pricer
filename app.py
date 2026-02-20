import streamlit as st
import pandas as pd

from utils.visualizations import plot_wind_speed_distribution, plot_wind_speed_over_time, get_wind_speed_stats, count_wind_speed_thresholds, wind_speed_seasonality 
from utils.visualizations import plot_weibull_fit, plot_weibull_qq
from src.data_fetcher import get_wind_data
from src.model_wind import fit_weibull_distribution, calculate_exceedance_probability
from src.pricer import calculate_premium


# Configuration de la page Streamlit
st.set_page_config(page_title="Wind Risk Pricer",page_icon="🌪️",layout= "wide")

# Titre de l'application
st.title("Wind Risk Pricer 🌪️")
st.info("Cette application permet d'analyser les données de vent, de calibrer un modèle de Weibull, de calculer la probabilité de dépassement d'un seuil de vent et de calculer la prime d'assurance correspondante.")
st.markdown("""=================================================================================================================""")

# Section de récupération des données
st.sidebar.header("Configuration")

# Section 1 : Localisation
st.sidebar.subheader("📍 Localisation")

# Choix du mode de sélection
location_mode = st.sidebar.radio(
    "Mode de sélection",
    options=["🔍 Recherche par nom", "📍 Coordonnées GPS"],
    help="Choisir comment définir la localisation"
)

if location_mode == "🔍 Recherche par nom":
    # Mode recherche par nom
    location_name = st.sidebar.text_input(
        "Nom du lieu",
        value="Bordeaux, France",
        placeholder="Ex: Paris, Lyon, Bordeaux...",
        help="Entrez le nom d'une ville, région ou pays"
    )
    
    # Bouton de géocodage
    if st.sidebar.button("🔍 Localiser", key="geocode_btn"):
        try:
            from geopy.geocoders import Nominatim
            
            # Géocodage
            geolocator = Nominatim(user_agent="wind_risk_pricer")
            location = geolocator.geocode(location_name)
            
            if location:
                # Stocker dans session_state pour persistance
                st.session_state.latitude = location.latitude
                st.session_state.longitude = location.longitude
                st.session_state.location_found = True
                st.sidebar.success(f"✅ Trouvé : {location.address}")
            else:
                st.sidebar.error("❌ Lieu introuvable. Essayez un autre nom.")
                st.session_state.location_found = False
        except Exception as e:
            st.sidebar.error(f"❌ Erreur : {str(e)}")
            st.session_state.location_found = False
    
    # Afficher les coordonnées trouvées (non modifiables)
    if 'latitude' in st.session_state and st.session_state.get('location_found', False):
        st.sidebar.info(f"📍 Lat: {st.session_state.latitude:.4f} | Lon: {st.session_state.longitude:.4f}")
        latitude = st.session_state.latitude
        longitude = st.session_state.longitude
    else:
        # Valeurs par défaut si pas encore géocodé
        latitude = 44.2971
        longitude = 0.1178

else:
    # Mode coordonnées GPS
    latitude = st.sidebar.number_input(
        "Latitude",
        value=st.session_state.get('latitude', 44.2971),
        min_value=-90.0,
        max_value=90.0,
        format="%.4f",
        help="Latitude de la localisation"
    )

    longitude = st.sidebar.number_input(
        "Longitude", 
        value=st.session_state.get('longitude', 0.1178),
        min_value=-180.0,
        max_value=180.0,
        format="%.4f",
        help="Longitude de la localisation"
    )
    
    
    # Mettre à jour session_state
    st.session_state.latitude = latitude
    st.session_state.longitude = longitude

# Après la sélection de localisation
if st.sidebar.checkbox("📍 Afficher sur la carte"):
    import folium
    from streamlit_folium import folium_static
    
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Localisation sélectionnée").add_to(m)
    folium_static(m, width=600, height=400)

start_date = st.sidebar.date_input("Date de début", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("Date de fin", value=pd.to_datetime("2025-12-31"))

st.sidebar.subheader("Paramètres de calcul de la prime")

threshold = st.sidebar.number_input(
        "Seuil de vent (km/h)", 
        value=35.0,
         format="%.1f",
        help="Entrez le seuil de vent en km/h pour lequel vous souhaitez calculer la prime d'assurance"
         )
exposure = st.sidebar.number_input(
        "Exposition (en €)", 
        value=1000000.0,
         format="%.2f",
        help="Entrez l'exposition financière en euros pour laquelle vous souhaitez calculer la prime d'assurance"
         )

loading_factor = st.sidebar.slider(
        "Facteur de chargement pour la prime finale", 
        min_value=1.0, 
        max_value=2.0, 
        value=1.2, 
        step=0.01,
        help="Marge de sécurité pour la prime finale (ex: 1.2 pour une prime finale égale à 120% de la prime calculée)"
    )

calculate_button = st.sidebar.button(
    "Calculer la prime",
    type="primary",
    help="Lancer l'analyse et la tarification"
)

# ===============================================================
# Page principale
# ===============================================================

if calculate_button:
    with st.spinner("Chargement des données et calibration du modèle"):

        # Récupération des données de vent
        df = get_wind_data(latitude, longitude, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        st.success("✅ Données de vent récupérées avec succès !")

        # Calibration du modèle 
        shape, loc, scale = fit_weibull_distribution(df)
        st.success(f"✅ Modèle de Weibull calibré : shape={shape:.2f}, scale={scale:.2f}")

        # Calcul de la prime d'assurance
        premium_df = calculate_premium(shape, scale, threshold, exposure, confidence_level=1/loading_factor)
        premium = premium_df["Prime totale"].iloc[0]
        st.success(f"✅ Prime d'assurance calculée : {premium:.2f} €")

        st.write(" Détails du calcul de la prime d'assurance")
        st.write(premium_df)

        # Stockage dans les session_state pour éviter de recalculer à chaque interaction
        st.session_state.df = df
        st.session_state.shape = shape
        st.session_state.loc = loc
        st.session_state.scale = scale
        st.session_state.premium = premium
        st.session_state.threshold = threshold
        st.session_state.exposure = exposure
        st.session_state.loading_factor = loading_factor
        st.session_state.calculation_done = True


# Affichachage des résultats
if st.session_state.get('calculation_done', False):

    # Je crée deux onglets pour séparer les analyses et validation de modèle du calcul de la prime
    tab1, tab2 = st.tabs(["📊 Analyse des données ", "✅ Validation du modèle"])

    # ==============================================================
    # Onglet 1 : Analyse des données & validation du modèle
    # ==============================================================
    with tab1:
        st.header("📊 Analyse des données ")

        # Statistiques descriptives des vitesses de vent
        st.markdown(" Statistiques descriptives des vitesses de vent")
        wind_summary = get_wind_speed_stats(st.session_state.df)
        st.write(wind_summary)

        # Visualisation de la distribution des vitesses de vent
        fig_weibull_fit = plot_wind_speed_distribution(st.session_state.df)
        st.plotly_chart(fig_weibull_fit, use_container_width=True)

        # Trend des vitesses de vent dans le temps
        fig_trend = plot_wind_speed_over_time(st.session_state.df)
        st.plotly_chart(fig_trend, use_container_width=True)

        # Saisonnalité des vitesses de vent
        fig_seasonality = wind_speed_seasonality(st.session_state.df)
        st.plotly_chart(fig_seasonality, use_container_width=True)

        # Dépassement de seuils de vent

        st.subheader(f"Nombre de jours avec une vitesse de vent maximale dépassant {st.session_state.threshold} km/h")
        threshold_count = count_wind_speed_thresholds(st.session_state.df, st.session_state.threshold)
        st.info(f"Sur la période analysée, le seuil a été franchi {threshold_count} fois.")
        

    
    # ==============================================================
    # Onglet 2 : Calcul de la prime d'assurance
    # ==============================================================
    with tab2:
        st.header("✅ Validation du modèle")
        # Visualisation de l'ajustement de la distribution de Weibull
        fig_weibull_fit = plot_weibull_fit(st.session_state.df)
        st.plotly_chart(fig_weibull_fit, use_container_width=True)

        # Visualisation du Q-Q plot pour évaluer l'ajustement de la distribution de Weibull
        fig_qq = plot_weibull_qq(st.session_state.df)
        st.plotly_chart(fig_qq, use_container_width=True)

       
