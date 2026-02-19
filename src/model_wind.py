from scipy.stats import weibull_min
import numpy as np

# 1. Calibration du modèle de Weibull
def fit_weibull_distribution(df):
    """
    Ajuste une distribution de Weibull aux données de vitesses de vent
    """
    # Extraire les vitesses de vent
    wind_speeds = df['wind_speed_max'].values

    # Filtrer les vitesses de vent pour éviter les valeurs négatives  ainsi que les valeurs manquantes
    wind_speeds = wind_speeds[~np.isnan(wind_speeds)] 
    wind_speeds = wind_speeds[wind_speeds >= 0]
    
    # Supprimer les valeurs NaN

    
    # Estimer les paramètres de la distribution de Weibull
    shape, loc, scale = weibull_min.fit(wind_speeds, floc=0)  # On fixe loc à 0 pour les vitesses de vent car elles ne peuvent pas être négatives
    
    return shape, loc, scale


# 2. Calcul de probabilité de dépassement d'un seuil de vent
def calculate_exceedance_probability(df, threshold):
    """
    Calcule la probabilité que la vitesse de vent maximale dépasse un certain seuil
    """
    shape, loc, scale = fit_weibull_distribution(df)
    
    # Calculer la probabilité de dépassement du seuil
    exceedance_probability = 1 - weibull_min.cdf(threshold, shape, loc=loc, scale=scale)
    
    return exceedance_probability


# Test
if __name__ == "__main__":
    from src.data_fetcher import get_wind_data

    # Chargement des données de vent
    df = get_wind_data(44.2971, 0.1178, "2022-01-01", "2025-12-31")
    
    # Ajustement de la distribution de Weibull
    shape, loc, scale = fit_weibull_distribution(df)
    print(f"Paramètres de la distribution de Weibull : shape={shape:.2f}, scale={scale:.2f}")

    # Calcul de la probabilité de dépassement d'un seuil de vent
    threshold = 35 #euil en km/h
    exceedance_prob = calculate_exceedance_probability(df, threshold)
    print(f"Probabilité que la vitesse de vent maximale dépasse {threshold} km/h : {exceedance_prob:.4f}")