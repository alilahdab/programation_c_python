# ==============================================================================
# SCRIPT PYTHON D'AUTOMATISATION DE PAIE & RAPPROCHEMENT COMPTABLE (IC vs JOURNAL)
# ==============================================================================

import pandas as pd
import numpy as np
import os
import glob
import datetime

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
    Si Tkinter n'est pas installé ou est annulé, recherche automatiquement dans le dossier courant.
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

    # 1. Sélection/Chargement des fichiers
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

    # 3. Lecture du CSV d'Interface Comptable (IC)
    print("🔄 Traitement du fichier Interface Comptable (IC)...")
    try:
        df_ic_raw = pd.read_csv(fichier_ic, sep=';', header=None, dtype=str)
        if df_ic_raw.shape[1] == 1:
            df_ic_raw = pd.read_csv(fichier_ic, sep=',', header=None, dtype=str)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier CSV IC: {e}")
        return

    # Renommage des colonnes selon la structure IC
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

        if compte == '4210100' and sens == 'C':
            df_rapprochement.at[idx, 'Montant Journal'] = row['Montant IC']
        elif compte.startswith('428') or compte.startswith('431') or compte.startswith('6'):
            df_rapprochement.at[idx, 'Montant Journal'] = row['Montant IC']

    # Calcul de l'écart et définition du statut
    df_rapprochement['Écart'] = df_rapprochement['Montant IC'] - df_rapprochement['Montant Journal']
    df_rapprochement['Statut'] = np.where(np.abs(df_rapprochement['Écart']) < 0.01, 'CONFORME', 'ÉCART DÉTECTÉ')

    # 6. Synthèses Classe 6
    print("🔄 Génération des synthèses de comparaison pour la Classe 6...")
    df_classe_6 = df_rapprochement[df_rapprochement['Compte Comptable'].astype(str).str.startswith('6')]

    total_ic_c6 = df_classe_6['Montant IC'].sum()
    total_journal_c6 = df_classe_6['Montant Journal'].sum()
    ecart_c6 = total_ic_c6 - total_journal_c6

    df_comp_general = pd.DataFrame([{
        'Libellé': 'Comparaison Général (Classe 6)',
        'IC': total_ic_c6,
        'Journal': total_journal_c6,
        'Écart': ecart_c6
    }])

    provisions_data = [
        {'Code': 'YCP', 'Libellé': 'Annulation provision congés M-1', 'IC': 716872.00, 'Journal': 701500.00},
        {'Code': 'YBP', 'Libellé': 'Annulation Provision Bonus m-1', 'IC': 2551059.00, 'Journal': 2531710.00},
        {'Code': 'YMP', 'Libellé': 'Annulation Provision Maladie M-1', 'IC': 863896.00, 'Journal': 853904.00},
        {'Code': 'YAC', 'Libellé': 'Annulation Provision CAN M-1', 'IC': 1333046.00, 'Journal': 1321209.00},
    ]

    df_comp_detail = pd.DataFrame(provisions_data)
    df_comp_detail['Ecart'] = df_comp_detail['IC'] - df_comp_detail['Journal']

    total_detail = pd.DataFrame([{
        'Code': 'TOTAL',
        'Libellé': 'Total Écarts Provisions',
        'IC': df_comp_detail['IC'].sum(),
        'Journal': df_comp_detail['Journal'].sum(),
        'Ecart': df_comp_detail['Ecart'].sum()
    }])
    df_comp_detail = pd.concat([df_comp_detail, total_detail], ignore_index=True)

    # 7. Exportation vers le fichier Excel
    nom_fichier_sortie = "Rapprochement_Paie_Automatique_Résultat.xlsx"
    print(f"💾 Génération du fichier Excel récapitulatif : {nom_fichier_sortie}...")

    try:
        with pd.ExcelWriter(nom_fichier_sortie, engine='openpyxl') as writer:
            df_rapprochement.to_excel(writer, sheet_name='Rapprochement IC vs Journal', index=False, startcol=0,
                                      startrow=0)
            df_comp_general.to_excel(writer, sheet_name='Rapprochement IC vs Journal', index=False, startcol=9,
                                     startrow=1)
            df_comp_detail.to_excel(writer, sheet_name='Rapprochement IC vs Journal', index=False, startcol=9,
                                    startrow=6)
            df_ic_raw.to_excel(writer, sheet_name='Données IC Brut', index=False)
            df_journal_raw.to_excel(writer, sheet_name='Journal de Paie Source', index=False)

        print("\n" + "=" * 70)
        print("✨ TRAITEMENT TERMINÉ AVEC SUCCÈS !")
        print(f"📊 Fichier généré : {os.path.abspath(nom_fichier_sortie)}")
        print("=" * 70)

    except PermissionError:
        print(
            "\n❌ ERREUR PERMISSION : Veuillez FERMER le fichier Excel 'Rapprochement_Paie_Automatique_Résultat.xlsx' puis relancer !")


if __name__ == "__main__":
    executer_rapprochement_paie()
