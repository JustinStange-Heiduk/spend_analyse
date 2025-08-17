# Notebook für die Daten Transformation und laden in data/silver

# Imports
import pandas as pd
import requests
from tqdm import tqdm
import os
from datetime import datetime, timedelta


# functions

# lfa1
# Drop duplizierte Lieferanten
def drop_duplicates_lieferanten(df: pd.DataFrame) -> pd.DataFrame:
    """
    Entfernt duplizierte Lieferanten basierend auf den Spalten 'Lieferant' und 'Name'.

    Args:
        df (pd.DataFrame): Der DataFrame, aus dem Duplikate entfernt werden sollen.

    Returns:
        pd.DataFrame: Ein DataFrame ohne duplizierte Lieferanten.
    """
    return df.drop_duplicates(subset=["Lieferant", "Name"], keep='first').reset_index(drop=True)


# sap rechnungen
# Merge lieferantenname
def merge_lieferanten_names(df: pd.DataFrame, lfa1_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Lieferanten-Namen aus dem LFA1 DataFrame in das Rechnungen DataFrame.

    Args:
        df (pd.DataFrame): Das Rechnungen DataFrame, in das die Namen eingefügt werden sollen.
        lfa1_df (pd.DataFrame): Das LFA1 DataFrame, das die Lieferantennamen enthält.

    Returns:
        pd.DataFrame: Ein DataFrame mit den Lieferantennamen aus dem LFA1 DataFrame.
    """
    return df.merge(lfa1_df[['Lieferant', 'Name']], left_on='Lieferant_Nummer', right_on='Lieferant', how='left').drop(columns='Lieferant')


# drop Zeilen mit Zahlungsdatum < 2022
def drop_invalid_payments(df: pd.DataFrame, min_date: str) -> pd.DataFrame:
    """
    Entfernt Zeilen mit einem Zahlungsdatum vor dem angegebenen Mindestdatum.

    Args:
        df (pd.DataFrame): Das DataFrame, aus dem die ungültigen Zahlungen entfernt werden sollen.
        min_date (str): Das Mindestdatum im Format 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: Ein DataFrame ohne ungültige Zahlungen.
    """

    return df[df["Zahlungsdatum"] >= min_date]


# Wechselkurs den Rechnungen Df hinzufügen
def add_wechselkurse_to_rechnungen(rechnungen_df: pd.DataFrame, wechselkurse_df: pd.DataFrame, währung_column: str, zahlungsdatum_column: str) -> pd.DataFrame:
    """
    Fügt Wechselkurse zu den Rechnungsdaten hinzu.
    
    Args:
    - rechnungen_df (pd.DataFrame): DataFrame mit Rechnungsdaten
    - wechselkurse_df (pd.DataFrame): DataFrame mit Wechselkursen
    - währung_column (str): Der Name der Währungsspalte im Rechnungs-DataFrame
    - zahlungsdatum_column (str): Der Name der Zahlungsdatumsspalte im Rechnungs-DataFrame

    Returns:
    - pd.DataFrame: DataFrame mit hinzugefügten Wechselkursen
    """
    wechselkurs_liste = []

    for _, row in rechnungen_df.iterrows():
        datum = row[zahlungsdatum_column]
        währung = row[währung_column]

        if pd.isna(datum) or pd.isna(währung):
            print("Daten fehlen")
            break

        if währung == "EUR":
            wechselkurs_liste.append(1.0)
        else:
            kurs_row = wechselkurse_df[wechselkurse_df["Datum"] == datum]
            if kurs_row.empty:
                wechselkurs_liste.append(None)
            else:
                if währung == "USD":
                    wechselkurs_liste.append(kurs_row["Wechselkurs_USD"].values[0])
                elif währung == "GBP":
                    wechselkurs_liste.append(kurs_row["Wechselkurs_GBP"].values[0])
                else:
                    wechselkurs_liste.append(None)

    rechnungen_df["Wechselkurs"] = wechselkurs_liste

    return rechnungen_df


# Alle Rechnungen in Euro rechnen
def calc_spendeuro(rechnungen_df: pd.DataFrame, spend_column: str) -> pd.DataFrame:
    """
    Berechnet den Betrag in Euro für jede Zeile basierend auf der Währung und dem Wechselkurs.

    Args:
        rechnungen_df (pd.DataFrame): Das DataFrame, das die Spalten 'Spend', 'Wechselkurs' enthält.
        spend_column (str): Der Name der Spalte, die den Betrag in der ursprünglichen Währung enthält.

    Returns:
        pd.DataFrame: Ein DataFrame mit einer neuen Spalte 'Spend_EUR'
    """
    rechnungen_df["Spend_EUR"] = rechnungen_df[spend_column] * rechnungen_df["Wechselkurs"]

    return rechnungen_df


# Anpassen des Belegdatum von mm/tt/jjjj zu jjjj-mm-tt
def datum_anpassen(df: pd.DataFrame, datum_spalte: str) -> pd.DataFrame:
    """
    Konvertiert die Werte in der angegebenen Datums-Spalte von mm/tt/jjjj zu jjjj-mm-tt

    Args:
        df (pd.DataFrame): Das DataFrame, das die Datums-Spalte enthält.
        datum_spalte (str): Der Name der Datums-Spalte, die konvertiert werden soll.

    Returns:
        pd.DataFrame: Das aktualisierte DataFrame mit der konvertierten Datums-Spalte.
    """
    df[datum_spalte] = pd.to_datetime(df[datum_spalte], format='%m/%d/%Y', errors='coerce').dt.date
    return df


# Baue Sachkonto- nummer und Name Dict
def sachkonto_dict(df: pd.DataFrame) -> dict:
    """
    Erstellt ein Dictionary aus Sachkonto-Nummer und Sachkonto-Name.

    Args:
        df (pd.DataFrame): DataFrame, das die Spalten 'Sachkonto-Nummer' und 'Sachkonto-Name' enthält.

    Returns:
        dict: Ein Dictionary mit Sachkonto-Nummer als Schlüssel und Sachkonto-Name als Wert.
    """
    return dict(zip(df['Sachkonto-Nummer'], df['Sachkonto-Name']))


# Mappe die fehlenden Sachkonten in Rechungen SAP 2024 mit diesen Dict
def sachkonto_mapping(df: pd.DataFrame, sachkonto_dict: dict, sachkonto_name: str, sachkonto_nummer: str) -> pd.DataFrame:
    """
    Mappt die Sachkonto-Nummern auf die Sachkonto-Namen basierend auf dem gegebenen Dictionary.

    Args:
        df (pd.DataFrame): DataFrame, das die Spalte 'Sachkonto-Nummer' enthält.
        sachkonto_dict (dict): Dictionary mit Sachkonto-Nummer als Schlüssel und Sachkonto-Name als Wert.
        sachkonto_name (str): Der Name der Spalte, die die Sachkonto-Namen enthält.
        sachkonto_nummer (str): Der Name der Spalte, die die Sachkonto-Nummern enthält.

    Returns:
        pd.DataFrame: DataFrame mit den aktualisierten Sachkonto-Nummern und -Namen.
    """

    reverse_dict = {v: k for k, v in sachkonto_dict.items()}

    df[sachkonto_name] = df[sachkonto_name].fillna(df[sachkonto_nummer].map(sachkonto_dict))
    df[sachkonto_nummer] = df[sachkonto_nummer].fillna(df[sachkonto_name].map(reverse_dict))

    return df


# Anpassen der Columnnames
def rename_columns(df: pd.DataFrame, column_mapping: dict) -> pd.DataFrame:
    """
    Bennennt die Spalten eines DataFrames um basierend auf einem gegebenen Mapping.

    Args:
        df (pd.DataFrame): Das DataFrame, dessen Spalten umbenannt werden sollen.
        column_mapping (dict): Ein Dictionary, das die alten Spaltennamen den neuen zuordnet.

    Returns:
        pd.DataFrame: Das DataFrame mit umbenannten Spalten.
    """
    return df.rename(columns=column_mapping)

# Wechselkurs
# Bauen eines Wechselkurs df
def get_exchange_rates_df(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Holt Wechselkurse von USD und GBP zu EUR für jeden Tag im angegebenen Zeitraum.
    
    Parameter:
    - start_date (str): Startdatum im Format "YYYY-MM-DD"
    - end_date (str): Enddatum im Format "YYYY-MM-DD"
    
    Rückgabe:
    - DataFrame mit Spalten: Datum, Wechselkurs_USD, Wechselkurs_GBP
    """
    start_date  = datetime.strptime(start_date, "%Y-%m-%d")
    end_date  = datetime.strptime(end_date, "%Y-%m-%d")
    
    data = []

    # Tagesweise iterieren
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime("%Y-%m-%d")
        
        usd_rate, gbp_rate = None, None

        # USD → EUR
        resp_usd = requests.get(f"https://api.frankfurter.app/{formatted_date}?from=USD&to=EUR")
        if resp_usd.ok:
            usd_rate = resp_usd.json()["rates"]["EUR"]

        # GBP → EUR
        resp_gbp = requests.get(f"https://api.frankfurter.app/{formatted_date}?from=GBP&to=EUR")
        if resp_gbp.ok:
            gbp_rate = resp_gbp.json()["rates"]["EUR"]
        
        data.append({
            "Datum": formatted_date,
            "Wechselkurs_USD": usd_rate,
            "Wechselkurs_GBP": gbp_rate
        })
        
        current_date += timedelta(days=1)

        df = pd.DataFrame(data)

        if df.isnull().values.any():
            print(f"Fehlende Wechselkurse für das Datum: {formatted_date}")

    return df






# Hauptprogramm
if __name__ == "__main__":

    # load data from data/bronze
    lfa1 = pd.read_csv("/workspace/data/bronze/LFA1.csv", sep=";")
    rechnungen_sap_2023 = pd.read_csv("/workspace/data/bronze/Rechnungen_SAP_2023.csv", sep=";")
    rechnungen_sap_2024 = pd.read_csv("/workspace/data/bronze/Rechnungen_SAP_2024.csv", sep="|")

    # lfa1
    # Drop duplizierte Lieferanten
    lfa1_cleaned = drop_duplicates_lieferanten(lfa1)

    # wechselkurs
    # Bauen eines Wechselkurs df
    try:
        wechselkurse_df = pd.read_csv("/workspace/data/silver/wechselkurse.csv", sep=";")
    except FileNotFoundError:
        print("Wechselkurs Datei noch nicht vorhanden muss erst gebaut werden")
        wechselkurse_df = get_exchange_rates_df("2023-01-01", "2024-12-31")
        print("Wechselkurs Datei wird gebaut")
        wechselkurse_df.to_csv("/workspace/data/silver/wechselkurse.csv", index=False, sep=";")
        print("Wechselkurs Datei wird gespeichert")
        


    # sap Rechnungen
    # sap Rechnungen 2023
    rechnungen_sap_2023_lieferantenname = merge_lieferanten_names(rechnungen_sap_2023, lfa1_cleaned).rename(columns={'Name': 'Lieferantenname'})
    # drop Zeilen mit Zahlungsdatum < 2022
    rechnungen_sap_2023_lieferantenname_valid = drop_invalid_payments(rechnungen_sap_2023_lieferantenname, "2022-01-01")
    # Wechselkurs den Rechnungen Df hinzufügen
    rechnungen_sap_2023_lieferantenname_valid_wechselkurs = add_wechselkurse_to_rechnungen(rechnungen_sap_2023_lieferantenname_valid, wechselkurse_df, "Währung", "Zahlungsdatum")
    # Alle Rechnungen in Euro rechnen
    rechnungen_sap_2023_lieferantenname_valid_wechselkurs_spendeuro = calc_spendeuro(rechnungen_sap_2023_lieferantenname_valid_wechselkurs, "Spend")

    # sap rechunungen 2024
    # Anpassen des Belegdatum von mm/tt/jjjj zu jjjj-mm-tt
    rechnungen_sap_2024_datum = datum_anpassen(rechnungen_sap_2024, "BelegDatum")
    # Lieferantenname hinzufügen
    rechnungen_sap_2024_datum_lieferantenname = merge_lieferanten_names(rechnungen_sap_2024_datum, lfa1_cleaned).rename(columns={'Name': 'Lieferantenname'})
    # Wechselkurs den Rechnungen Df hinzufügen
    rechnungen_sap_2024_datum_lieferantenname_wechselkurs = add_wechselkurse_to_rechnungen(rechnungen_sap_2024_datum_lieferantenname, wechselkurse_df, "Rechnungswährung", "Zahlungsdatum")
    # Alle Rechnungen in Euro rechnen
    rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro = calc_spendeuro(rechnungen_sap_2024_datum_lieferantenname_wechselkurs, "Rechnungswert")
    # Baue Sachkonto- nummer und Name Dict
    sachkonto_dict_2023 = sachkonto_dict(rechnungen_sap_2023)
    # Mappe die fehlenden Sachkonten in Rechungen SAP 2024 mit diesen Dict
    rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro_sachkonto = sachkonto_mapping(rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro, sachkonto_dict_2023, 'Sachkonto-Name', 'Sachkonto-Nummer')
    # Anpassen der Columnnames
    column_mapping = {
        'Rechnungsnummer_SAP': 'Rechnungsnummer',
        'BelegDatum': 'Belegdatum',
        'Rechnungswert': 'Spend',
        'Rechnungswährung': 'Währung'
    }
    rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro_sachkonto_rename = rename_columns(rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro_sachkonto, column_mapping)

    # Concat Rechungen 2023 und 2024
    rechnungen_2023_2024 = pd.concat([rechnungen_sap_2023_lieferantenname_valid_wechselkurs_spendeuro, rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro_sachkonto_rename], ignore_index=True)

    # Save dfs to csv in /workspace/data/silver
    lfa1_cleaned.to_csv("/workspace/data/silver/LFA1_cleaned.csv", index=False, sep=";")
    rechnungen_sap_2023_lieferantenname_valid_wechselkurs_spendeuro.to_csv("/workspace/data/silver/Rechnungen_SAP_2023.csv", index=False, sep=";")
    rechnungen_sap_2024_datum_lieferantenname_wechselkurs_spendeuro_sachkonto_rename.to_csv("/workspace/data/silver/Rechnungen_SAP_2024.csv", index=False, sep=";")
    rechnungen_2023_2024.to_csv("/workspace/data/silver/Rechnungen_SAP_2023_2024.csv", index=False, sep=";")


    print("Silver Script ausgeführt")
