# Notebook für die Auswertungen in data/Gold

# Imports
import pandas as pd

# Functions

# Auswertung 1
def top10_lieferanten(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gibt die Top 10 Lieferanten basierend auf der Spendensumme in EUR zurück.

    Args:
        df (pd.DataFrame): Das DataFrame, das die Rechnungsdaten enthält.

    Returns:
        pd.DataFrame: Ein DataFrame mit den Top 10 Lieferanten mit den Spalten Lieferantennummer, Lieferantenname und Spend in EUR (aggregiert).
    """
    top10 = df.groupby("Lieferantenname")["Spend_EUR"].sum().nlargest(10).index

    result = (
        df[df["Lieferantenname"].isin(top10)]
        .groupby(["Lieferant_Nummer", "Lieferantenname"], as_index=False)["Spend_EUR"]
        .sum()
        .sort_values("Spend_EUR", ascending=False)
    )

    result["Spend_EUR"] = result["Spend_EUR"].round(2)

    return result.reset_index(drop=True).rename(columns={"Lieferant_Nummer": "Lieferantennummer",  "Spend_EUR": "Spend in EUR"})



# Auswertung 2
def top10_sachkonten(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gibt die Top 10 Sachkonten basierend auf der Anzahl der Rechnungen zurück.

    Args:
        df (pd.DataFrame): Das DataFrame mit den Rechnungsdaten.

    Returns:
        pd.DataFrame: Ein DataFrame mit den Top 10 Sachkonten, bestehend aus:
                      Sachkonto-Nummer, Sachkonto-Name und Anzahl der Rechnungen.
    """
    # Gruppierung nach Sachkonto-Nummer und -Name, Zählen der Einträge
    grouped = (
        df.groupby(["Sachkonto-Nummer", "Sachkonto-Name"])
        .size()
        .reset_index(name="Anzahl")
    )

    # Top 10 mit den meisten Rechnungen
    top10 = grouped.sort_values("Anzahl", ascending=False).head(10).reset_index(drop=True)

    return top10.rename(columns={"Sachkonto-Nummer": "Sachkontonummer", "Sachkonto-Name": "Sachkontoname"})


# Auswertung 3
def monatlicher_spendverlauf(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ermittelt den zeitlichen Verlauf des Spends in EUR (2023–2024) pro Monat.

    Args:
        df (pd.DataFrame): DataFrame mit einer Spalte 'Belegdatum' (datetime) und 'Spend_EUR' (float)

    Returns:
        pd.DataFrame: DataFrame mit den Spalten 'Jahr', 'Monat', 'Spend_EUR'
    """
    df = df.copy()

    # Belegdatum sicherstellen
    df["Belegdatum"] = pd.to_datetime(df["Belegdatum"], errors="coerce")

    # Jahr und Monat extrahieren
    df["Jahr"] = df["Belegdatum"].dt.year
    df["Monat"] = df["Belegdatum"].dt.month

    # Gruppieren und aufsummieren
    result = (
        df.groupby(["Jahr", "Monat"], as_index=False)["Spend_EUR"]
        .sum()
        .sort_values(["Jahr", "Monat"])
        .reset_index(drop=True)
    )
    result["Spend_EUR"] = result["Spend_EUR"].round(2)

    return result.rename(columns={"Spend_EUR": "Spend in EUR"})


# Hauptprogramm
if __name__ == "__main__":

    # load data from data/silver
    rechnungen_sap_2023 = pd.read_csv("/workspace/data/silver/Rechnungen_SAP_2023.csv", sep=";")
    rechnungen_sap_2024 = pd.read_csv("/workspace/data/silver/Rechnungen_SAP_2024.csv", sep=";")
    rechnungen_sap_2023_2024 = pd.read_csv("/workspace/data/silver/Rechnungen_SAP_2023_2024.csv", sep=";")

    # Auswertung 1
    auswertung_1_2023 = top10_lieferanten(rechnungen_sap_2023)
    auswertung_1_2024 = top10_lieferanten(rechnungen_sap_2024)
    auswertung_1_2023_2024 = top10_lieferanten(rechnungen_sap_2023_2024)

    # Auswertung 2
    auswertung_2_2023 = top10_sachkonten(rechnungen_sap_2023)
    auswertung_2_2024 = top10_sachkonten(rechnungen_sap_2024)
    auswertung_2_2023_2024 = top10_sachkonten(rechnungen_sap_2023_2024)

    # Auswertung 3
    auswertung_3_2023_2024 = monatlicher_spendverlauf(rechnungen_sap_2023_2024)

    # Speichern der Ergebnisse
    auswertung_1_2023.to_csv("/workspace/data/gold/auswertung_1_2023.csv", index=False, sep=";")
    auswertung_1_2024.to_csv("/workspace/data/gold/auswertung_1_2024.csv", index=False, sep=";")
    auswertung_1_2023_2024.to_csv("/workspace/data/gold/auswertung_1_2023_2024.csv", index=False, sep=";")

    auswertung_2_2023.to_csv("/workspace/data/gold/auswertung_2_2023.csv", index=False, sep=";")
    auswertung_2_2024.to_csv("/workspace/data/gold/auswertung_2_2024.csv", index=False, sep=";")
    auswertung_2_2023_2024.to_csv("/workspace/data/gold/auswertung_2_2023_2024.csv", index=False, sep=";")

    auswertung_3_2023_2024.to_csv("/workspace/data/gold/auswertung_3_2023_2024.csv", index=False, sep=";")

    print("Auswertung abgeschlossen und in data/gold gespeichert.")