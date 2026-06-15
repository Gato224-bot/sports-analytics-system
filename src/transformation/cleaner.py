"""
Data cleaning pipeline with outlier detection and data quality gates.

Implements statistical methods for data validation and transformation.
"""

import pandas as pd
import numpy as np
from scipy import stats
import logging
from typing import Tuple, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Pipeline de limpieza: outliers, duplicados, imputación.
    
    Métodos:
        - Detección de duplicados por match_id
        - Outlier detection usando IQR (Interquartile Range)
        - Imputación de valores faltantes
        - Validación de tipos de datos
    """
    
    def __init__(self, iqr_multiplier: float = 1.5):
        """
        Inicializa el limpiador de datos.
        
        Args:
            iqr_multiplier: Multiplicador de IQR para detectar outliers.
                           1.5 = estándar (68% de datos dentro)
                           3.0 = severo (95% de datos dentro)
        """
        self.iqr_multiplier = iqr_multiplier
        self.report: Dict = {}
    
    def remove_duplicates(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """
        Elimina partidos duplicados.
        
        Args:
            df: DataFrame a limpiar
            subset: Columnas sobre las que detectar duplicados (default: ['match_id'])
        
        Returns:
            DataFrame sin duplicados, mantiene el registro más reciente
        """
        if subset is None:
            subset = ['match_id']
        
        before = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep='last')
        after = len(df_clean)
        removed = before - after
        
        self.report['duplicates_removed'] = removed
        logger.info(f"✓ Duplicados removidos: {removed}")
        
        return df_clean
    
    def detect_outliers_iqr(
        self,
        df: pd.DataFrame,
        column: str,
        k: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Detecta outliers usando Interquartile Range (IQR).
        
        Formula:
            Q1 = percentil 25
            Q3 = percentil 75
            IQR = Q3 - Q1
            lower_bound = Q1 - k * IQR
            upper_bound = Q3 + k * IQR
        
        Args:
            df: DataFrame a analizar
            column: Columna numérica a revisar
            k: Multiplicador (None = usa self.iqr_multiplier)
        
        Returns:
            DataFrame con columna adicional '{column}_is_outlier' (bool)
        """
        if k is None:
            k = self.iqr_multiplier
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - k * IQR
        upper_bound = Q3 + k * IQR
        
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        n_outliers = outliers.sum()
        pct_outliers = (n_outliers / len(df)) * 100
        
        df[f'{column}_is_outlier'] = outliers
        
        if n_outliers > 0:
            logger.warning(
                f"⚠ Outliers detectados en '{column}': {n_outliers} ({pct_outliers:.2f}%)\n"
                f"  Rango válido: [{lower_bound:.2f}, {upper_bound:.2f}]"
            )
            self.report[f'{column}_outliers'] = n_outliers
        
        return df
    
    def detect_outliers_zscore(
        self,
        df: pd.DataFrame,
        column: str,
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Detecta outliers usando Z-score (desviaciones estándar).
        
        Formula:
            z = (x - media) / desv_std
            outlier si |z| > threshold
        
        Args:
            df: DataFrame a analizar
            column: Columna numérica
            threshold: Número de desviaciones estándar (3.0 = 99.7% de datos)
        
        Returns:
            DataFrame con columna adicional '{column}_zscore_outlier'
        """
        z_scores = np.abs(stats.zscore(df[column].dropna()))
        outliers = z_scores > threshold
        
        df[f'{column}_zscore_outlier'] = False
        df.loc[df[column].notna(), f'{column}_zscore_outlier'] = outliers.values
        
        n_outliers = outliers.sum()
        if n_outliers > 0:
            logger.warning(f"⚠ Z-score outliers en '{column}': {n_outliers}")
        
        return df
    
    def impute_missing(
        self,
        df: pd.DataFrame,
        strategy: str = 'mean',
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        Imputa valores faltantes con estrategia configurable.
        
        Args:
            df: DataFrame a rellenar
            strategy: 'mean', 'median', 'forward_fill', 'drop'
            threshold: Si % missing > threshold, dropea la columna (rango 0-1)
        
        Returns:
            DataFrame con valores imputados
        """
        for col in df.select_dtypes(include=[np.number]).columns:
            missing_pct = df[col].isnull().sum() / len(df)
            
            # Si missing % > threshold, dropear columna
            if missing_pct > threshold:
                logger.warning(
                    f"⚠ Columna '{col}' tiene {missing_pct*100:.1f}% missing. Eliminada."
                )
                df = df.drop(col, axis=1)
                continue
            
            # Aplicar estrategia de imputación
            if df[col].isnull().sum() > 0:
                if strategy == 'mean':
                    fill_value = df[col].mean()
                    df[col].fillna(fill_value, inplace=True)
                    logger.info(f"✓ '{col}' imputado con media: {fill_value:.4f}")
                
                elif strategy == 'median':
                    fill_value = df[col].median()
                    df[col].fillna(fill_value, inplace=True)
                    logger.info(f"✓ '{col}' imputado con mediana: {fill_value:.4f}")
                
                elif strategy == 'forward_fill':
                    df[col].fillna(method='ffill', inplace=True)
                    logger.info(f"✓ '{col}' imputado con forward fill")
        
        return df
    
    def validate_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Valida y convierte tipos de datos.
        
        Returns:
            Tuple de (DataFrame limpio, reporte de conversiones)
        """
        conversions = {}
        
        # Convertir fechas
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                    conversions[col] = 'datetime64'
                    logger.info(f"✓ '{col}' convertido a datetime")
                except Exception as e:
                    logger.error(f"✗ Error convirtiendo '{col}' a datetime: {e}")
        
        return df, conversions
    
    def get_report(self) -> Dict:
        """
        Retorna reporte de todas las operaciones de limpieza.
        """
        return self.report


class FeatureEngineer:
    """
    Ingeniería de features: creación de variables derivadas basadas en lógica estadística.
    
    Features generadas:
        - Rolling averages (últimos N partidos)
        - Head-to-head statistics
        - Temporal weighting (decaimiento de importancia temporal)
        - Rest days between matches
    """
    
    def __init__(self, rolling_window: int = 10, h2h_lookback: int = 5):
        """
        Inicializa el ingeniero de features.
        
        Args:
            rolling_window: Número de partidos anteriores a considerar
            h2h_lookback: Número de enfrentamientos directos a considerar
        """
        self.rolling_window = rolling_window
        self.h2h_lookback = h2h_lookback
        self.report: Dict = {}
    
    def rolling_team_stats(
        self,
        df: pd.DataFrame,
        window: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Calcula promedios móviles de goles por equipo.
        
        Formula:
            avg_goals_last_N = media(goles últimos N partidos del equipo)
        
        Args:
            df: DataFrame con columnas 'home_team', 'away_team', 'home_goals', 'away_goals', 'date'
            window: Tamaño de ventana (None = usa self.rolling_window)
        
        Returns:
            DataFrame con nuevas columnas:
                - home_avg_goals_last_n
                - away_avg_goals_last_n
                - home_avg_conceded_last_n
                - away_avg_conceded_last_n
        """
        if window is None:
            window = self.rolling_window
        
        df = df.sort_values('date').reset_index(drop=True)
        
        # Home teams: goles marcados
        home_goals_window = (
            df.groupby('home_team')['home_goals']
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(drop=True)
        )
        df['home_avg_goals_last_n'] = home_goals_window
        
        # Home teams: goles concedidos
        home_conceded_window = (
            df.groupby('home_team')['away_goals']
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(drop=True)
        )
        df['home_avg_conceded_last_n'] = home_conceded_window
        
        # Away teams: goles marcados
        away_goals_window = (
            df.groupby('away_team')['away_goals']
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(drop=True)
        )
        df['away_avg_goals_last_n'] = away_goals_window
        
        # Away teams: goles concedidos
        away_conceded_window = (
            df.groupby('away_team')['home_goals']
            .rolling(window=window, min_periods=1)
            .mean()
            .reset_index(drop=True)
        )
        df['away_avg_conceded_last_n'] = away_conceded_window
        
        logger.info(f"✓ Rolling stats calculadas (window={window})")
        self.report['rolling_window'] = window
        
        return df
    
    def head_to_head(
        self,
        df: pd.DataFrame,
        lookback: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Calcula historial head-to-head entre equipos.
        
        Formula:
            h2h_home_win_pct = (victorias local / total enfrentamientos) en últimos N
        
        Args:
            df: DataFrame con partidos históricos
            lookback: Número de enfrentamientos a considerar
        
        Returns:
            DataFrame con columna 'h2h_home_win_pct'
        """
        if lookback is None:
            lookback = self.h2h_lookback
        
        df = df.sort_values('date').reset_index(drop=True)
        
        def calculate_h2h_record(home_team: str, away_team: str, current_idx: int) -> float:
            """
            Calcula % de victorias del equipo local en enfrentamientos previos.
            """
            # Obtener todos los enfrentamientos previos entre estos equipos
            h2h_matches = df.loc[:current_idx - 1].copy()
            h2h_matches = h2h_matches[
                ((h2h_matches['home_team'] == home_team) & 
                 (h2h_matches['away_team'] == away_team)) |
                ((h2h_matches['home_team'] == away_team) & 
                 (h2h_matches['away_team'] == home_team))
            ].tail(lookback)
            
            if len(h2h_matches) == 0:
                return 0.5  # Sin datos: equiprobable
            
            # Contar victorias del equipo local
            home_wins = (
                (h2h_matches['home_team'] == home_team) & 
                (h2h_matches['home_goals'] > h2h_matches['away_goals'])
            ).sum()
            
            return home_wins / len(h2h_matches)
        
        df['h2h_home_win_pct'] = df.apply(
            lambda row: calculate_h2h_record(row['home_team'], row['away_team'], row.name),
            axis=1
        )
        
        logger.info(f"✓ Head-to-head stats calculadas (lookback={lookback})")
        self.report['h2h_lookback'] = lookback
        
        return df
    
    def time_decay(
        self,
        df: pd.DataFrame,
        decay_rate: float = 0.95
    ) -> pd.DataFrame:
        """
        Aplica decaimiento temporal: datos recientes pesan más.
        
        Formula:
            time_weight = decay_rate ^ (días_atrás / 30)
        
        Args:
            df: DataFrame con columna 'date'
            decay_rate: Factor de decaimiento (0.95 = 5% menos peso por mes)
        
        Returns:
            DataFrame con columna 'time_weight'
        """
        df = df.sort_values('date').reset_index(drop=True)
        df['date'] = pd.to_datetime(df['date'])
        
        max_date = df['date'].max()
        df['days_ago'] = (max_date - df['date']).dt.days
        
        # Decaimiento por mes (30 días)
        df['time_weight'] = decay_rate ** (df['days_ago'] / 30)
        
        logger.info(f"✓ Temporal weighting aplicado (decay_rate={decay_rate})")
        self.report['decay_rate'] = decay_rate
        
        return df
    
    def days_rest_between_matches(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calcula días de descanso antes de cada partido.
        
        Args:
            df: DataFrame con columna 'date'
        
        Returns:
            DataFrame con columnas:
                - days_rest_home
                - days_rest_away
        """
        df = df.sort_values('date').reset_index(drop=True)
        df['date'] = pd.to_datetime(df['date'])
        
        def get_rest_days(team: str, current_date: pd.Timestamp, current_idx: int) -> int:
            """
            Calcula días desde el último partido del equipo.
            """
            previous_matches = df.loc[:current_idx - 1].copy()
            previous_matches = previous_matches[
                (previous_matches['home_team'] == team) | 
                (previous_matches['away_team'] == team)
            ]
            
            if len(previous_matches) == 0:
                return 7  # Asumir una semana de descanso si es el primer partido
            
            last_match_date = previous_matches['date'].max()
            rest_days = (current_date - last_match_date).days
            
            return max(rest_days, 0)
        
        df['days_rest_home'] = df.apply(
            lambda row: get_rest_days(row['home_team'], row['date'], row.name),
            axis=1
        )
        
        df['days_rest_away'] = df.apply(
            lambda row: get_rest_days(row['away_team'], row['date'], row.name),
            axis=1
        )
        
        logger.info("✓ Days of rest calculados")
        
        return df
    
    def create_result_label(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea etiqueta de resultado (1=victoria local, X=empate, 2=victoria visitante).
        
        Args:
            df: DataFrame con 'home_goals' y 'away_goals'
        
        Returns:
            DataFrame con columna 'result'
        """
        def determine_result(home_goals: int, away_goals: int) -> str:
            if home_goals > away_goals:
                return "1"  # Home win
            elif home_goals == away_goals:
                return "X"  # Draw
            else:
                return "2"  # Away win
        
        df['result'] = df.apply(
            lambda row: determine_result(row['home_goals'], row['away_goals']),
            axis=1
        )
        
        logger.info("✓ Result labels creadas")
        
        return df
    
    def get_report(self) -> Dict:
        """
        Retorna reporte de features creadas.
        """
        return self.report
