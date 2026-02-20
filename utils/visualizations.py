import plotly.graph_objects as go
import pandas as pd

# Fonction pour visualiser la distribution des vitesses de vent
def plot_wind_speed_distribution(df):
    fig=go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df['wind_speed_max'],
            nbinsx=20,
            marker_color='blue',
            name='vitesses de vent'
        )
    )

    fig.update_layout(
        title='Distribution des vitesses de vent',
        xaxis_title='Vitesse de vent maximale (km/h)',
        yaxis_title='Fréquence',
        bargap=0.2
    )
    

    return fig

# Fonction pour visualiser le trend des vitesses de vent dans le temps
def plot_wind_speed_over_time(df):
    """
    Graphique de l'évolution temporelle des vitesses de vent avec range slider
    """
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['wind_speed_max'],
            mode='lines',
            name='Vitesse max quotidienne',
            line=dict(color='blue', width=1),
            hovertemplate='<b>Date:</b> %{x}<br><b>Vent:</b> %{y:.1f} km/h<extra></extra>'
        )
    )
    
    # Ajouter une ligne de tendance (moyenne mobile sur 30 jours)
    df['rolling_mean'] = df['wind_speed_max'].rolling(window=30, center=True).mean()
    
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['rolling_mean'],
            mode='lines',
            name='Tendance (moyenne 30j)',
            line=dict(color='red', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>Moyenne:</b> %{y:.1f} km/h<extra></extra>'
        )
    )
    
    fig.update_layout(
        title='Évolution temporelle des vitesses de vent',
        xaxis_title='Date',
        yaxis_title='Vitesse du vent (km/h)',
        hovermode='x unified',
        
        # LE RANGE SLIDER ICI ⬇️
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                thickness=0.05  # Hauteur du slider (5% du graphique)
            ),
            type="date"
        )
    )
    
    return fig

# Statistiques descriptives
def get_wind_speed_stats(df):
    print("Statistiques descriptives des vitesses de vent :")

    stats_dict = {
        'Nombre de jours': len(df),
        'Vitesse de vent maximale moyenne (km/h)': df['wind_speed_max'].mean(),
        'Vitesse de vent maximale médiane (km/h)': df['wind_speed_max'].median(),
        'Vitesse de vent minimale sur la période (km/h)': df['wind_speed_max'].min(),
        'Vitesse de vent maximale sur la période (km/h)': df['wind_speed_max'].max()
    }
    
    df_stats = pd.DataFrame(stats_dict, index=[0])

    return df_stats

# Dépassement de seuils de vent
def count_wind_speed_thresholds(df, thresholds):
    count = (df['wind_speed_max'] > thresholds).sum()
    return count

# Saisonnalité des vitesses de vent
def wind_speed_seasonality(df):
    df['month'] = pd.to_datetime(df['date']).dt.month
    monthly_avg = df.groupby('month')['wind_speed_max'].mean().reset_index()

    # Couleurs en fonction de la vitesse (vert = calme, rouge = venteux)
    colors = monthly_avg['wind_speed_max'].values
    
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly_avg['month'],
            y=monthly_avg['wind_speed_max'],
            marker=dict(
                color=colors,
                colorscale='Viridis',  # ou 'Blues', 'Reds', etc.
                showscale=True,
                colorbar=dict(title="Vitesse (km/h)")
            ),
            name='Vitesse moyenne',
            text=monthly_avg['wind_speed_max'].round(1),  # Afficher les valeurs
            textposition='outside'
        )
    )

    fig.update_layout(
        title='Saisonnalité des vitesses de vent',
        xaxis_title='Mois',
        yaxis_title='Vitesse de vent maximale moyenne (km/h)',
        xaxis=dict(
            tickmode='array', 
            tickvals=list(range(1, 13)), 
            ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                      'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        ),
        showlegend=False
    )

    return fig

# ==== Validation du modèle ====
from scipy.stats import weibull_min
import numpy as np
from src.model_wind import fit_weibull_distribution

# Visualisation de l'ajustement de la distribution de Weibull
def plot_weibull_fit(df):
    shape, loc, scale = fit_weibull_distribution(df)
    
    # Générer des données pour la distribution de Weibull ajustée
    x = np.linspace(0, df['wind_speed_max'].max(), 100)
    y = weibull_min.pdf(x, shape, loc=loc, scale=scale)

    fig=go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df['wind_speed_max'],
            nbinsx=20,
            marker_color='blue',
            name='Données réelles',
            histnorm='probability density'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Distribution de Weibull ajustée',
            line=dict(color='red')
        )
    )

    fig.update_layout(
        title='Ajustement de la distribution de Weibull aux vitesses de vent',
        xaxis_title='Vitesse de vent maximale (km/h)',
        yaxis_title='Densité de probabilité',
        bargap=0.2
    )

    return fig

# QQ plot pour évaluer l'ajustement de la distribution de Weibull
def plot_weibull_qq(df):
    shape, loc, scale = fit_weibull_distribution(df)
    
    # Générer des quantiles théoriques de la distribution de Weibull
    theoretical_quantiles = weibull_min.ppf(np.linspace(0.01, 0.99, len(df)), shape, loc=loc, scale=scale)
    
    # Quantiles empiriques
    empirical_quantiles = np.sort(df['wind_speed_max'].values)

    fig=go.Figure()
    fig.add_trace(
        go.Scatter(
            x=theoretical_quantiles,
            y=empirical_quantiles,
            mode='markers',
            name='Quantiles empiriques vs théoriques'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, max(theoretical_quantiles)],
            y=[0, max(theoretical_quantiles)],
            mode='lines',
            name='Ligne d\'identité',
            line=dict(color='red', dash='dash')
        )
    )

    fig.update_layout(
        title='QQ Plot pour évaluer l\'ajustement de la distribution de Weibull',
        xaxis_title='Quantiles théoriques (Weibull)',
        yaxis_title='Quantiles empiriques (Données réelles)'
    )

    return fig


# test
if __name__ == "__main__":
    from src.data_fetcher import get_wind_data

    # Chargement des données de vent
    df = get_wind_data(44.2971, 0.1178, "2022-01-01", "2025-12-31")
    
    # Visualisation de l'ajustement de la distribution de Weibull
    fig_weibull_fit = plot_weibull_fit(df)
    fig_weibull_fit.show()

    # Visualisation du QQ plot pour évaluer l'ajustement de la distribution de Weibull
    fig_qq = plot_weibull_qq(df)
    fig_qq.show()