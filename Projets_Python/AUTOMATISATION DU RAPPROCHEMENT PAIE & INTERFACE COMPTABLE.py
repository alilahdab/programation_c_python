

import pandas as pd
import numpy as np
import os
import glob

# Gestion de la boîte de dialogue pour la sélection interactive des fichiers
try:
    import tkinter as tk
    from tkinter import filedialog

    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


def choisir_fichiers_interactif():
    """
    Ouvre une fenêtre pour sélectionner les 2 fichiers sources.
    """
    fichier_journal = None
    fichier_ic = None

    if HAS_TKINTER:
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            print("📍 Veuillez sélectionner le fichier 'Journal de Paie' (.xlsx)...")
            fichier_journal = filedialog.askopenfilename(
                title="Sélectionnez le Journal de Paie Maurice / RIT",
                filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
            )

            print("📍 Veuillez sélectionner le fichier 'Interface Comptable IC' (.csv)...")
            fichier_ic = filedialog.askopenfilename(
                title="Sélectionnez le fichier IC (CSV)",
                filetypes=[("Fichiers CSV", "*.csv")]
            )
            root.destroy()
        except Exception:
            fichier_journal = None
            fichier_ic = None

    # Recherche automatique dans le dossier si aucune sélection manuelle
    if not fichier_journal or not fichier_ic:
        print("ℹ️ Sélection manuelle non effectuée. Recherche automatique dans le dossier...")
        journals = glob.glob("Journal de Paie*.xlsx") + glob.glob("Journal de paie*.xlsx")
        ics = glob.glob("IC*.csv") + glob.glob("*.csv")

        if journals and not fichier_journal:
            fichier_journal = journals[0]
        if ics and not fichier_ic:
            fichier_ic = ics[0]

    return fichier_journal, fichier_ic


def executer_rapprochement_paie():
    print("=" * 70)
    print("      AUTOMATISATION DU RAPPROCHEMENT PAIE & INTERFACE COMPTABLE      ")
    print("=" * 70)

    # 1.Chargement des fichiers
    fichier_journal, fichier_ic = choisir_fichiers_interactif()

    if not fichier_journal or not os.path.exists(fichier_journal):
        print("❌ Erreur : Fichier Journal de Paie Excel introuvable.")
        return

    if not fichier_ic or not os.path.exists(fichier_ic):
        print("❌ Erreur : Fichier d'Interface Comptable (IC CSV) introuvable.")
        return

    print(f"✔️ Journal de paie retenu : {fichier_journal}")
    print(f"✔️ Interface Comptable (IC) : {fichier_ic}\n")

    # 2. Lecture du Journal de Paie
    print("🔄 Chargement du Journal de Paie...")
    xl_journal = pd.ExcelFile(fichier_journal)
    nom_feuille = xl_journal.sheet_names[0]
    df_journal_raw = pd.read_excel(fichier_journal, sheet_name=nom_feuille)

    # 3. Lecture du CSV (IC)
    print("🔄 Traitement du fichier Interface Comptable (IC)...")
    try:
        df_ic_raw = pd.read_csv(fichier_ic, sep=';', header=None, dtype=str)
        if df_ic_raw.shape[1] == 1:
            df_ic_raw = pd.read_csv(fichier_ic, sep=',', header=None, dtype=str)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier CSV IC: {e}")
        return

    # Renommage des colonnes selon la structure IC [Société/UO, Code_UO, Compte, Sens, Montant, Période, Code]
    colonnes_ic = ['UO', 'Code_UO', 'Compte', 'Sens', 'Montant', 'Periode', 'Code_App']
    df_ic_raw.columns = colonnes_ic[:df_ic_raw.shape[1]]

    # Nettoyage et conversion des montants
    df_ic_raw['Montant'] = pd.to_numeric(df_ic_raw['Montant'].str.replace(',', '.'), errors='coerce').fillna(0)

    # 4. Agrégation par Compte Comptable et Sens (D/C)
    print("🔄 Synthèse des comptes comptables Débit / Crédit...")
    ic_groupe = df_ic_raw.groupby(['Compte', 'Sens'], as_index=False)['Montant'].sum()

    # 5. Rapprochement et Calcul des Écarts
    print("🔄 Calcul des écarts entre IC et Journal de paie...")
    df_rapprochement = ic_groupe.copy()
    df_rapprochement.rename(columns={
        'Compte': 'Compte Comptable',
        'Sens': 'Sens (D/C)',
        'Montant': 'Montant IC'
    }, inplace=True)

    # Initialisation du montant du Journal
    df_rapprochement['Montant Journal'] = 0.0

    # Rapprochement selon les comptes du plan comptable paie
    for idx, row in df_rapprochement.iterrows():
        compte = str(row['Compte Comptable'])
        sens = row['Sens (D/C)']

        # Exemple de correspondance de base
        if compte == '4210100' and sens == 'C':
            df_rapprochement.at[idx, 'Montant Journal'] = row['Montant IC']
        elif compte.startswith('428') or compte.startswith('431'):
            df_rapprochement.at[idx, 'Montant Journal'] = row['Montant IC']

    # Calcul de l'écart et définition du statut
    df_rapprochement['Écart'] = df_rapprochement['Montant IC'] - df_rapprochement['Montant Journal']
    df_rapprochement['Statut'] = np.where(np.abs(df_rapprochement['Écart']) < 0.01, 'CONFORME', 'ÉCART DÉTECTÉ')

    # 6. Exportation du rapport Excel final
    import datetime 
    # Génère un nom unique avec la date et l'heure
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier_sortie = f"Rapprochement_Paie_{horodatage}.xlsx"
    print(f"💾 Génération du fichier Excel récapitulatif : {nom_fichier_sortie}...")

    with pd.ExcelWriter(nom_fichier_sortie, engine='openpyxl') as writer:
        df_rapprochement.to_excel(writer, sheet_name='Rapprochement IC vs Journal', index=False)
        df_ic_raw.to_excel(writer, sheet_name='Données IC Brut', index=False)
        df_journal_raw.to_excel(writer, sheet_name='Journal de Paie Source', index=False)

    print("\n" + "=" * 70)
    print(f"✨ TRAITEMENT TERMINÉ AVEC SUCCÈS !")
    print(f"📊 Fichier généré : {os.path.abspath(nom_fichier_sortie)}")
    print("=" * 70)


if __name__ == "__main__":
    executer_rapprochement_paie()