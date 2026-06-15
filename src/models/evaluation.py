"""
Robust backtesting framework with statistical validation.

Implements time-series cross-validation, binomial tests, and Expected Value analysis.
"""

import pandas as pd
import numpy as np
from scipy.stats import binom_test
from sklearn.metrics import log_loss, confusion_matrix, classification_report
import logging
from typing import Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)


class BacktestFramework:
    """
    Marco robusto de backtesting con validación estadística.
    
    Característica clave: NUNCA asumamos que "pasó el test" = exitoso.
    
    Validamos si el modelo es mejor que un clasificador aleatorio.
    """
    
    def __init__(self, model, df: pd.DataFrame, test_size: float = 0.2):
        """
        Inicializa el framework de backtesting.
        
        Args:
            model: Modelo entrenado (sklearn/XGBoost)
            df: DataFrame con features y target (ordenado por fecha)
            test_size: Porcentaje para test (deben ser cronológicamente últimos)
        """
        self.model = model
        self.df = df.sort_values('date')
        self.split_idx = int(len(df) * (1 - test_size))
        self.train_df = df.iloc[:self.split_idx]
        self.test_df = df.iloc[self.split_idx:]
        self.results: Dict = {}
    
    def evaluate_accuracy(self) -> Dict[str, float]:
        """
        Evalúa precisión de predicciones vs resultado real.
        
        Métrica clave: Accuracy (% aciertos en clasificación)
        Benchmark: Random classifier = 33.33% (3 clases: 1, X, 2)
        
        Returns:
            Dict con:
                - accuracy: Precisión del modelo
                - random_baseline: Baseline aleatorio
                - improvement_pct: Mejora relativa (%)
                - n_predictions: Número de predicciones
        """
        feature_cols = [c for c in self.test_df.columns if c not in ['date', 'result', 'match_id']]
        X_test = self.test_df[feature_cols]
        y_true = self.test_df['result']
        
        predictions = self.model.predict(X_test)
        accuracy = (predictions == y_true).mean()
        
        # Comparar con random
        random_accuracy = 1/3  # 3 clases equiprobables
        improvement = (accuracy - random_accuracy) / random_accuracy * 100
        
        results = {
            'accuracy': accuracy,
            'random_baseline': random_accuracy,
            'improvement_pct': improvement,
            'n_predictions': len(y_true)
        }
        
        logger.info(f"✓ Accuracy: {accuracy:.2%} (vs random: {random_accuracy:.2%})")
        logger.info(f"  Mejora relativa: {improvement:+.1f}%")
        
        self.results['accuracy_metrics'] = results
        return results
    
    def statistical_significance_test(self, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Binomial test: ¿Es nuestro accuracy estadísticamente mejor que random?
        
        H0: accuracy = 33.33% (random)
        H1: accuracy > 33.33%
        
        Args:
            alpha: Nivel de significancia (default: 0.05 = 95% confianza)
        
        Returns:
            Dict con:
                - p_value: p-value del test
                - is_significant: ¿Rechazamos H0?
                - success_rate: Tasa de éxito observada
        """
        feature_cols = [c for c in self.test_df.columns if c not in ['date', 'result', 'match_id']]
        X_test = self.test_df[feature_cols]
        y_true = self.test_df['result']
        predictions = self.model.predict(X_test)
        
        successes = (predictions == y_true).sum()
        n_trials = len(y_true)
        p_random = 1/3
        
        # Binomial test (one-tailed: alternative='greater')
        p_value = binom_test(successes, n_trials, p_random, alternative='greater')
        is_significant = p_value < alpha
        
        results = {
            'p_value': p_value,
            'is_significant': is_significant,
            'alpha': alpha,
            'success_rate': successes / n_trials,
            'successes': successes,
            'total_trials': n_trials
        }
        
        logger.info(f"Binomial test p-value: {p_value:.4f}")
        logger.info(f"¿Estadísticamente significativo? {is_significant} (α={alpha})")
        
        if not is_significant:
            logger.warning(
                "⚠ NO hay evidencia de que el modelo sea mejor que random.\n"
                "   Recomendación: revisar features, check overfitting, considerar más datos."
            )
        
        self.results['statistical_test'] = results
        return results
    
    def log_loss_evaluation(self) -> Dict[str, float]:
        """
        Evalúa calibración de probabilidades (no solo aciertos/fallos).
        
        Métrica: Log Loss (menor = mejor)
        Penaliza predicciones confiadas pero erróneas.
        
        Returns:
            Dict con:
                - log_loss: Log loss del modelo
                - random_log_loss: Log loss de random
                - improvement_ratio: Factor de mejora
        """
        feature_cols = [c for c in self.test_df.columns if c not in ['date', 'result', 'match_id']]
        X_test = self.test_df[feature_cols]
        y_test = self.test_df['result']
        
        # Predicciones probabilísticas
        try:
            y_proba = self.model.predict_proba(X_test)
        except AttributeError:
            logger.warning("Modelo no soporta predict_proba, saltando log_loss")
            return {}
        
        ll = log_loss(y_test, y_proba)
        
        # Benchmark: log loss de predictor aleatorio
        random_proba = np.ones((len(y_test), 3)) / 3
        random_ll = log_loss(y_test, random_proba)
        
        improvement_ratio = random_ll / ll if ll > 0 else 0
        
        results = {
            'log_loss': ll,
            'random_log_loss': random_ll,
            'improvement_ratio': improvement_ratio
        }
        
        logger.info(f"✓ Log Loss: {ll:.4f} (vs random: {random_ll:.4f})")
        logger.info(f"  Ratio de mejora: {improvement_ratio:.2f}x")
        
        self.results['log_loss'] = results
        return results
    
    def walk_forward_validation(
        self,
        min_train_size: int = 100,
        step: int = 20
    ) -> pd.DataFrame:
        """
        Validación walk-forward: simula uso real en tiempo.
        
        Entrena en pasado, predice siguiente período, avanza ventana.
        
        Diagrama:
        ═════════════════════════════════════════
        Train[1-100]   | Test[101-120]
                         Train[1-120]   | Test[121-140]
                                         Train[1-140]   | Test[141-160]
        ═════════════════════════════════════════
        
        Args:
            min_train_size: Tamaño mínimo de conjunto de entrenamiento
            step: Número de ejemplos para cada paso
        
        Returns:
            DataFrame con predicciones y métricas por ventana
        """
        results = []
        feature_cols = [c for c in self.df.columns if c not in ['date', 'result', 'match_id']]
        
        for test_start in range(min_train_size, len(self.df) - step, step):
            test_end = test_start + step
            
            train = self.df.iloc[:test_start]
            test = self.df.iloc[test_start:test_end]
            
            # Re-entrenar en cada ventana
            X_train = train[feature_cols]
            y_train = train['result']
            
            try:
                self.model.fit(X_train, y_train)
            except Exception as e:
                logger.error(f"Error reentrenando en ventana {test_start}-{test_end}: {e}")
                continue
            
            # Evaluar
            X_test = test[feature_cols]
            y_test = test['result']
            predictions = self.model.predict(X_test)
            
            accuracy = (predictions == y_test).mean()
            
            results.append({
                'window': len(results),
                'period': f"{test_start}-{test_end}",
                'accuracy': accuracy,
                'n_tests': len(test),
                'successes': (predictions == y_test).sum()
            })
        
        results_df = pd.DataFrame(results)
        
        if len(results_df) > 0:
            mean_accuracy = results_df['accuracy'].mean()
            std_accuracy = results_df['accuracy'].std()
            logger.info(
                f"✓ Walk-forward validation completada\n"
                f"  Accuracy promedio: {mean_accuracy:.2%} ± {std_accuracy:.2%}"
            )
        
        self.results['walk_forward'] = results_df
        return results_df
    
    def confusion_matrix_analysis(self) -> Dict[str, Any]:
        """
        Analiza matriz de confusión para entender errores de clasificación.
        
        Returns:
            Dict con matriz y reporte de clasificación
        """
        feature_cols = [c for c in self.test_df.columns if c not in ['date', 'result', 'match_id']]
        X_test = self.test_df[feature_cols]
        y_true = self.test_df['result']
        predictions = self.model.predict(X_test)
        
        cm = confusion_matrix(y_true, predictions, labels=['1', 'X', '2'])
        report = classification_report(y_true, predictions, output_dict=True)
        
        results = {
            'confusion_matrix': cm,
            'classification_report': report
        }
        
        logger.info("✓ Confusion Matrix:")
        logger.info(f"\n{cm}")
        logger.info(f"\n{classification_report(y_true, predictions)}")
        
        self.results['confusion_matrix'] = results
        return results
    
    def expected_value_analysis(
        self,
        odds: Optional[pd.Series] = None
    ) -> Dict[str, float]:
        """
        Calcula EV (Expected Value) de las predicciones.
        
        EV = (P_predict * odds) - 1
        
        IMPORTANTE: Esto es PURA ESTADÍSTICA, no recomendación de apuesta.
        
        Simplemente valida: ¿nuestras predicciones tienen valor matemático?
        
        EV > 0: Estadísticamente favorable
        EV < 0: Estadísticamente desfavorable
        
        Args:
            odds: Serie de cuotas (default: usa 1.5x como proxy)
        
        Returns:
            Dict con análisis de EV
        """
        feature_cols = [c for c in self.test_df.columns if c not in ['date', 'result', 'match_id']]
        X_test = self.test_df[feature_cols]
        
        try:
            y_proba = self.model.predict_proba(X_test)
        except AttributeError:
            logger.warning("Modelo no soporta predict_proba, saltando EV analysis")
            return {}
        
        # Si no hay cuotas, usar cuotas proxy
        if odds is None:
            odds = pd.Series([1.5] * len(X_test), index=X_test.index)
        
        # Asumir que proba[:,0] = '1' (victoria local)
        home_win_proba = y_proba[:, 0]
        
        # EV = (P * odds) - 1
        ev_per_bet = (home_win_proba * odds.values) - 1
        
        mean_ev = ev_per_bet.mean()
        std_ev = ev_per_bet.std()
        positive_ev_count = (ev_per_bet > 0).sum()
        
        results = {
            'mean_ev': mean_ev,
            'std_ev': std_ev,
            'positive_ev_count': positive_ev_count,
            'total_opportunities': len(ev_per_bet),
            'positive_ev_pct': (positive_ev_count / len(ev_per_bet)) * 100
        }
        
        logger.info(f"Expected Value Analysis:")
        logger.info(f"  Mean EV: {mean_ev:+.4f}")
        logger.info(f"  Std EV: {std_ev:.4f}")
        logger.info(f"  Positive EV opportunities: {positive_ev_count}/{len(ev_per_bet)} ({results['positive_ev_pct']:.1f}%)")
        
        if mean_ev > 0:
            logger.info("✓ EV positivo: predicciones tienen valor matemático")
        else:
            logger.warning("✗ EV negativo: predicciones no tienen valor matemático")
        
        self.results['expected_value'] = results
        return results
    
    def get_full_report(self) -> Dict[str, Any]:
        """
        Retorna reporte completo de todas las evaluaciones.
        """
        return self.results
    
    def summary(self) -> str:
        """
        Genera resumen ejecutivo del backtesting.
        """
        summary_text = "\n" + "="*60
        summary_text += "\nBACKTESTING SUMMARY REPORT\n"
        summary_text += "="*60 + "\n"
        
        if 'accuracy_metrics' in self.results:
            acc = self.results['accuracy_metrics']
            summary_text += f"\nAccuracy Metrics:"
            summary_text += f"\n  Model Accuracy: {acc['accuracy']:.2%}"
            summary_text += f"\n  Random Baseline: {acc['random_baseline']:.2%}"
            summary_text += f"\n  Improvement: {acc['improvement_pct']:+.1f}%"
        
        if 'statistical_test' in self.results:
            stat = self.results['statistical_test']
            summary_text += f"\n\nStatistical Significance (Binomial Test):"
            summary_text += f"\n  p-value: {stat['p_value']:.4f}"
            summary_text += f"\n  Significant (α=0.05): {'YES ✓' if stat['is_significant'] else 'NO ✗'}"
            summary_text += f"\n  Success Rate: {stat['success_rate']:.2%}"
        
        if 'log_loss' in self.results:
            ll = self.results['log_loss']
            summary_text += f"\n\nProbability Calibration (Log Loss):"
            summary_text += f"\n  Model Log Loss: {ll['log_loss']:.4f}"
            summary_text += f"\n  Random Log Loss: {ll['random_log_loss']:.4f}"
            summary_text += f"\n  Improvement: {ll['improvement_ratio']:.2f}x"
        
        if 'expected_value' in self.results:
            ev = self.results['expected_value']
            summary_text += f"\n\nExpected Value:"
            summary_text += f"\n  Mean EV: {ev['mean_ev']:+.4f}"
            summary_text += f"\n  Positive EV Opportunities: {ev['positive_ev_pct']:.1f}%"
        
        summary_text += "\n" + "="*60 + "\n"
        
        return summary_text
