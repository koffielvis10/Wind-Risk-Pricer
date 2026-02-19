from scipy.stats import weibull_min
import pandas as pd

def calculate_premium(shape,scale, threshold, exposure, confidence_level=0.95):
    """
    Calcule la prime d'assurance basée sur la distribution de Weibull ajustée
    """
    # Calculer la probabilité de dépassement du seuil
    exceedance_probability = 1 - weibull_min.cdf(threshold, shape, loc=0, scale=scale)
    
    # Calculer la prime d'assurance
    premium = exceedance_probability * exposure
    
    # Ajouter une marge de sécurité basée sur le niveau de confiance
    margin_of_safety = premium * (1 - confidence_level)
    
    total_premium = premium + margin_of_safety
    
    results_dict = {
        "Probabilité de dépassement du seuil": exceedance_probability,
        "Exposition": exposure,
        "Prime pure": premium,
        "Marge de sécurité": margin_of_safety,
        "Prime totale": total_premium
    }

    results_df = pd.DataFrame([results_dict])
    return  results_df

