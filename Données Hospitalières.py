
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix


# ================================================================ #
#  1. GÉNÉRATION DES DONNÉES                                       #
# ================================================================ #
def generate_hospital_data(n: int) -> pd.DataFrame:
    np.random.seed(42)

    patient_id = np.arange(1, n + 1)
    sex        = np.random.binomial(1, 0.5, size=n)
    age        = np.random.uniform(20, 80, size=n).round(1)

    severity_probs   = [0.5, 0.3, 0.2]
    severity_levels  = ['Low', 'Medium', 'High']
    severity_indices = np.random.choice(len(severity_levels),
                                        size=n, p=severity_probs)
    severity = [severity_levels[i] for i in severity_indices]

    blood_pressure = np.random.normal(loc=120, scale=15, size=n).round(1)
    readmissions   = np.random.poisson(lam=2, size=n)

    return pd.DataFrame({
        'patient_id'    : patient_id,
        'sex'           : sex,
        'age'           : age,
        'severity'      : severity,
        'blood_pressure': blood_pressure,
        'readmissions'  : readmissions,
    })


# ================================================================ #
#  2. VISUALISATION DES DONNÉES                                    #
# ================================================================ #
def visualize_hospital_data(df: pd.DataFrame):
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    axes = axes.flatten()

    sns.countplot(x='sex', data=df, ax=axes[0], palette="Set2")
    axes[0].set_title('Sex Distribution (0=Female, 1=Male)')

    sns.histplot(df['age'], bins=20, kde=True, ax=axes[1], color='skyblue')
    axes[1].axvline(df['age'].mean(), color='red', linestyle='--',
                    label=f"Mean: {df['age'].mean():.2f}")
    axes[1].legend()
    axes[1].set_title('Age Distribution')

    sns.countplot(x='severity', data=df, ax=axes[2], palette="pastel")
    axes[2].set_title('Severity Levels')

    sns.histplot(df['blood_pressure'], bins=20, kde=True,
                 ax=axes[3], color='orange')
    axes[3].axvline(df['blood_pressure'].mean(), color='red', linestyle='--',
                    label=f"Mean: {df['blood_pressure'].mean():.2f}")
    axes[3].legend()
    axes[3].set_title('Blood Pressure Distribution')

    sns.histplot(df['readmissions'], bins=10, kde=False,
                 ax=axes[4], color='lightgreen')
    axes[4].axvline(df['readmissions'].mean(), color='red', linestyle='--',
                    label=f"Mean: {df['readmissions'].mean():.2f}")
    axes[4].legend()
    axes[4].set_title('Readmissions Distribution')

    fig.delaxes(axes[5])
    plt.tight_layout()
    plt.show()


# ================================================================ #
#  3. EXPORT DES DONNÉES                                           #
# ================================================================ #
def save_hospital_data(df: pd.DataFrame, format: str, filename: str):
    format = format.lower()

    if format == 'csv':
        df.to_csv(f"{filename}.csv", index=False)
        print(f"[OK] {filename}.csv")
    elif format == 'excel':
        df.to_excel(f"{filename}.xlsx", index=False)
        print(f"[OK] {filename}.xlsx")
    elif format == 'json':
        df.to_json(f"{filename}.json", orient='records', indent=4)
        print(f"[OK] {filename}.json")
    elif format == 'xml':
        df.to_xml(f"{filename}.xml", index=False)
        print(f"[OK] {filename}.xml")
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        col_width  = pdf.w / (len(df.columns) + 1)
        row_height = 10
        spacing    = 1
        for col in df.columns:
            pdf.cell(col_width, row_height * spacing, str(col), border=1)
        pdf.ln(row_height * spacing)
        for _, row in df.head(30).iterrows():
            for item in row:
                pdf.cell(col_width, row_height * spacing,
                         str(item), border=1)
            pdf.ln(row_height * spacing)
        pdf.output(f"{filename}.pdf")
        print(f"[OK] {filename}.pdf")


# ================================================================ #
#  4. PRÉPARATION MACHINE LEARNING                                 #
# ================================================================ #
def prepare_data_for_classification(df, target_col):
    df_encoded     = df.copy()
    label_encoders = {}

    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    X = df_encoded.drop(columns=[target_col, 'patient_id'])
    y = df_encoded[target_col]

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X_scaled, y, test_size=0.4, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42)

    print(f"  Train : {X_train.shape[0]} | Val : {X_val.shape[0]} | Test : {X_test.shape[0]}")

    return X_train, X_val, X_test, y_train, y_val, y_test, label_encoders


# ================================================================ #
#  5. ENTRAÎNEMENT DES MODÈLES                                     #
# ================================================================ #
def train_and_evaluate_models(X_train, X_val, y_train, y_val):
    models = {
        'KNN'       : KNeighborsClassifier(n_neighbors=3),
        'Perceptron': Perceptron(max_iter=1000),
        'NaiveBayes': GaussianNB(),
        'NeuralNet' : MLPClassifier(hidden_layer_sizes=(50,), max_iter=1000),
    }

    results = {}
    for name, model in models.items():
        print(f"\n── {name} ──")
        model.fit(X_train, y_train)
        y_pred   = model.predict(X_val)
        report   = classification_report(y_val, y_pred, output_dict=True)
        conf_mat = confusion_matrix(y_val, y_pred)
        results[name] = {
            'model'      : model,
            'report'     : report,
            'conf_matrix': conf_mat,
        }
        print(classification_report(y_val, y_pred))

    return results


# ================================================================ #
#  6. MATRICES DE CONFUSION                                        #
# ================================================================ #
def plot_confusion_heatmaps(results, class_names):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, (name, result) in enumerate(results.items()):
        sns.heatmap(result['conf_matrix'], annot=True, fmt='d',
                    cmap='Blues', ax=axes[i],
                    xticklabels=class_names,
                    yticklabels=class_names)
        axes[i].set_title(f"{name} - Confusion Matrix")
        axes[i].set_xlabel('Predicted')
        axes[i].set_ylabel('Actual')

    plt.tight_layout()
    plt.show()


# ================================================================ #
#  7. DIAGRAMME DE KIVIAT                                          #
# ================================================================ #
def plot_kiviat(results, metric='f1-score'):
    labels = ['Low', 'Medium', 'High']
    angles = np.linspace(0, 2 * np.pi, len(labels),
                         endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(8, 6))
    ax  = plt.subplot(111, polar=True)

    for model_name, result in results.items():
        stats  = [result['report'][str(i)][metric] for i in range(3)]
        stats += stats[:1]
        ax.plot(angles, stats, label=model_name)
        ax.fill(angles, stats, alpha=0.1)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    plt.title(f"Radar Plot: {metric}")
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    plt.show()


# ================================================================ #
#  MAIN                                                            #
# ================================================================ #
if __name__ == "__main__":

    print("=" * 55)
    print("  TP 5 — Machine Learning : Données Hospitalières")
    print("=" * 55)

    print("\n[1] Génération des données...")
    df = generate_hospital_data(300)
    print(df.head(10).to_string())

    print("\n[2] Visualisation...")
    visualize_hospital_data(df)

    print("\n[3] Export...")
    save_hospital_data(df, 'csv',   'hospital_data')
    save_hospital_data(df, 'excel', 'hospital_data')
    save_hospital_data(df, 'json',  'hospital_data')
    save_hospital_data(df, 'pdf',   'hospital_data')

    print("\n[4] Préparation ML...")
    X_train, X_val, X_test, y_train, y_val, y_test, encoders = \
        prepare_data_for_classification(df, target_col='severity')

    print("\n[5] Entraînement des modèles...")
    results = train_and_evaluate_models(X_train, X_val, y_train, y_val)

    print("\n[6] Visualisations finales...")
    plot_confusion_heatmaps(results, class_names=['Low', 'Medium', 'High'])
    plot_kiviat(results, metric='f1-score')

    print("\n[INFO] Terminé !")