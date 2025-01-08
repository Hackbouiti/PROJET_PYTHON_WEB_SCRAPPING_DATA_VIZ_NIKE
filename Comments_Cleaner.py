import pandas as pd
import re

# Charger le fichier Excel
input_file = "Nike_Shoes_Comments.xlsx"
df = pd.read_excel(input_file)

def clean_comments(df):
    # Remplacer les NaN par des chaînes vides
    df['commentaire'] = df['commentaire'].fillna("")

    # Nettoyer les commentaires
    def clean_text(text):
        # Suppression des caractères spéciaux et de la ponctuation
        text = re.sub(r"[^\w\s]", "", text)
        # Conversion en minuscules
        text = text.lower()
        return text
    
    # Appliquer le nettoyage sur la colonne 'commentaire'
    df['commentaire_nettoye'] = df['commentaire'].apply(clean_text)

    return df

# Nettoyer les commentaires
df_cleaned = clean_comments(df)

# Sauvegarder le DataFrame nettoyé
output_file = "Nike_Shoes_Comments_Cleaned.xlsx"
df_cleaned.to_excel(output_file, index=False)

print(f"Fichier nettoyé sauvegardé sous {output_file}.")
