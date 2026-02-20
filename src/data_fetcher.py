
import requests
import pandas as pd

def get_wind_data(latitude, longitude, start_date, end_date):

    """
    Récupère les données historiques de vent depuis Open-Meteo API
    """
    
    # 1. Définir l'URL et les paramètres
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "wind_speed_10m_max",
        "timezone": "auto"
    }
    
    # 2. Faire la requête
    response = requests.get(url, params=params)
    
    # 3. Parser le JSON
    data = response.json()
    
    # 4. Créer le DataFrame
    df = pd.DataFrame({
    'date': data['daily']['time'],
    'wind_speed_max': data['daily']['wind_speed_10m_max']
})
    return df


# Test
if __name__ == "__main__":

    from utils.visualizations import plot_wind_speed_distribution, plot_wind_speed_over_time
    # Chargement des données de vent
    df = get_wind_data(44.2971, 0.1178, "2022-01-01", "2025-12-31")
    print(df.head())
    print(f"\nNombre de jours : {len(df)}")

    # Visualisation de la distribution des vitesses de vent
    fig=plot_wind_speed_distribution(df)
    fig.show()

    # Visualisation du trend des vitesses de vent dans le temps
    fig_trend=plot_wind_speed_over_time(df)
    fig_trend.show()

    from utils.visualizations import get_wind_speed_stats, count_wind_speed_thresholds, wind_speed_seasonality

    # Statistiques descriptives
    stats_df = get_wind_speed_stats(df)
    print(stats_df)

    # Dépassement de seuils de vent
    thresholds =40# Seuils en km/h
    threshold_counts = count_wind_speed_thresholds(df, thresholds)
    print(f"\nNombre de jours avec une vitesse de vent maximale dépassant {thresholds} km/h : {threshold_counts}")
    
    # Analyse de la saisonnalité
    seasonality_fig=wind_speed_seasonality(df) 
    seasonality_fig.show()