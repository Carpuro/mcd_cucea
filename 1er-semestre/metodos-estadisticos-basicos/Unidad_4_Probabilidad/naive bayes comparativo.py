import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import accuracy_score, confusion_matrix
import time
import os

# ============================================================================
# CARGAR DATOS
# ============================================================================

def cargar_datos():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "emails_spam_sample.csv")
    df = pd.read_csv(csv_path)
    
    # Separar datos y etiquetas
    category_row = df[df['Feature'] == 'Category']
    data_rows = df[df['Feature'] != 'Category']
    
    # Matriz X (emails como filas, features como columnas)
    email_columns = [str(i) for i in range(1, 11)]
    X = data_rows[email_columns].T.values.astype(int)
    
    # Vector y (0: No Spam, 1: Spam)
    categories = category_row[email_columns].values[0]
    y = np.array([1 if cat == 'Spam' else 0 for cat in categories])
    
    # Nombres de features
    features = data_rows['Feature'].tolist()
    
    return X, y, features

# ============================================================================
# IMPLEMENTACIÓN MANUAL
# ============================================================================

class NaiveBayesManual:
    def fit(self, X, y):
        # Separar por clase
        X_spam = X[y == 1]
        X_no_spam = X[y == 0]
        
        # Probabilidades a priori
        self.prior_spam = len(X_spam) / len(y)
        self.prior_no_spam = len(X_no_spam) / len(y)
        
        # Probabilidades condicionales
        self.prob_spam = np.sum(X_spam, axis=0) / len(X_spam)
        self.prob_no_spam = np.sum(X_no_spam, axis=0) / len(X_no_spam)
    
    def predict_proba(self, X):
        n_samples = X.shape[0]
        probas = np.zeros((n_samples, 2))
        
        for i in range(n_samples):
            x = X[i]
            
            # Likelihood
            likelihood_spam = np.prod(np.where(x == 1, self.prob_spam, 1 - self.prob_spam))
            likelihood_no_spam = np.prod(np.where(x == 1, self.prob_no_spam, 1 - self.prob_no_spam))
            
            # Posterior
            joint_spam = likelihood_spam * self.prior_spam
            joint_no_spam = likelihood_no_spam * self.prior_no_spam
            evidence = joint_spam + joint_no_spam
            
            probas[i, 0] = joint_no_spam / evidence
            probas[i, 1] = joint_spam / evidence
        
        return probas
    
    def predict(self, X):
        probas = self.predict_proba(X)
        return (probas[:, 1] > 0.5).astype(int)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CLASIFICADOR NAIVE BAYES - COMPARACIÓN")
    print("="*80)

    # Cargar datos
    X, y, features = cargar_datos()
    print(f"\n✓ Datos cargados: {X.shape[0]} emails, {X.shape[1]} features")
    print(f"✓ Spam: {np.sum(y)}, No Spam: {len(y) - np.sum(y)}")

    # ============================================================================
    # PARTE A: IMPLEMENTACIÓN MANUAL
    # ============================================================================

    print("\n" + "="*80)
    print("PARTE A: IMPLEMENTACIÓN MANUAL")
    print("="*80)

    modelo_manual = NaiveBayesManual()

    start = time.time()
    modelo_manual.fit(X, y)
    pred_manual = modelo_manual.predict(X)
    proba_manual = modelo_manual.predict_proba(X)
    time_manual = time.time() - start

    # Tabla 2: Probabilidades condicionales
    print("\nTABLA 2: PROBABILIDADES CONDICIONALES")
    print(f"{'#':<3} {'Feature':<15} {'P(xj=1|Spam)':<18} {'P(xj=1|No Spam)':<18}")
    print("-"*80)
    for i, feature in enumerate(features):
        print(f"{i+1:<3} {feature:<15} {modelo_manual.prob_spam[i]:.4f}{' '*14} {modelo_manual.prob_no_spam[i]:.4f}")

    print(f"\nProbabilidades a priori:")
    print(f"  P(Spam) = {modelo_manual.prior_spam:.4f}")
    print(f"  P(No Spam) = {modelo_manual.prior_no_spam:.4f}")

    # ============================================================================
    # PARTE B: SCIKIT-LEARN
    # ============================================================================

    print("\n" + "="*80)
    print("PARTE B: SCIKIT-LEARN (BernoulliNB)")
    print("="*80)

    modelo_sklearn = BernoulliNB()

    start = time.time()
    modelo_sklearn.fit(X, y)
    pred_sklearn = modelo_sklearn.predict(X)
    proba_sklearn = modelo_sklearn.predict_proba(X)
    time_sklearn = time.time() - start

    print(f"\n✓ Modelo entrenado")

    # ============================================================================
    # PARTE C: COMPARACIÓN
    # ============================================================================

    print("\n" + "="*80)
    print("PARTE C: COMPARACIÓN")
    print("="*80)

    # Resultados por email
    print("\nRESULTADOS POR EMAIL:")
    print(f"{'Email':<8} {'Real':<10} {'Manual':<10} {'P(Spam)':<12} {'Sklearn':<10} {'P(Spam)':<12}")
    print("-"*80)
    for i in range(len(y)):
        real = "Spam" if y[i] == 1 else "No Spam"
        manual = "Spam" if pred_manual[i] == 1 else "No Spam"
        sklearn = "Spam" if pred_sklearn[i] == 1 else "No Spam"
        print(f"{i+1:<8} {real:<10} {manual:<10} {proba_manual[i,1]:.4f}{' '*8} {sklearn:<10} {proba_sklearn[i,1]:.4f}")

    # Métricas
    print("\nMÉTRICAS:")
    print(f"  Precisión Manual:     {accuracy_score(y, pred_manual):.4f}")
    print(f"  Precisión Sklearn:    {accuracy_score(y, pred_sklearn):.4f}")
    print(f"  Tiempo Manual:        {time_manual*1000:.2f} ms")
    print(f"  Tiempo Sklearn:       {time_sklearn*1000:.2f} ms")

    # Matriz de confusión
    print("\nMATRIZ DE CONFUSIÓN (Manual):")
    cm = confusion_matrix(y, pred_manual)
    print(f"  VP: {cm[1,1]}  FP: {cm[0,1]}")
    print(f"  FN: {cm[1,0]}  VN: {cm[0,0]}")

    print("\n" + "="*80)
    print("CLASIFICACIÓN: 'congratulations, you won free gift'")
    print("="*80)

    mensaje = "congratulations you won free gift"
    palabras = mensaje.split()
    vector = np.array([[1 if f in palabras else 0 for f in features]])

    print(f"Vector: {vector[0].tolist()}")

    # Manual
    proba_m = modelo_manual.predict_proba(vector)
    pred_m = modelo_manual.predict(vector)
    print(f"\nManual:  P(Spam)={proba_m[0,1]:.4f} → {'SPAM' if pred_m[0]==1 else 'NO SPAM'}")

    # Sklearn
    proba_s = modelo_sklearn.predict_proba(vector)
    pred_s = modelo_sklearn.predict(vector)
    print(f"Sklearn: P(Spam)={proba_s[0,1]:.4f} → {'SPAM' if pred_s[0]==1 else 'NO SPAM'}")

    print("\n" + "="*80)
    print("✓ ANÁLISIS COMPLETADO")
    print("="*80 + "\n")