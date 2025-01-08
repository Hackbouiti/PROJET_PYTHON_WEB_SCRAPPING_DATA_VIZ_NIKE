import os
import json
import pandas as pd

# Répertoire où se trouvent les fichiers JSON
data_directory = "Data"

# Liste pour stocker les DataFrames individuels
data_frames = []

# Parcourir tous les fichiers JSON dans le répertoire
for file_name in os.listdir(data_directory):
    if file_name.endswith(".json"):  # Vérifie si le fichier est un fichier JSON
        file_path = os.path.join(data_directory, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as file:  # Utiliser UTF-8 pour lire les caractères spéciaux
            data = json.load(file)
            
            # Convertir les données JSON en DataFrame
            df = pd.DataFrame(data)
            df['Category'] = file_name.replace("Nike_Shoes_", "").replace(".json", "")  # Ajouter une colonne catégorie
            
            # Nettoyer et convertir la colonne 'price'
            if 'price' in df.columns:
                df['price'] = df['price'].str.replace('\u20ac', '')  # Retirer le symbole €
                df['price'] = df['price'].str.replace('\u00a0', '')  # Retirer l'espace insécable
                df['price'] = df['price'].str.replace(',', '.')  # Remplacer les virgules par des points
                df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Convertir en float, gérer les erreurs
            else:
                df['price'] = None  # Ajouter une colonne 'price' vide si elle n'existe pas
            
            # Ajouter les colonnes 'gender' et 'category'
            df['gender'] = df['Category'].apply(lambda x: 'Men' if 'Men' in x else ('Women' if 'Women' in x else 'Unisex'))
            df['category'] = df['Category'].apply(lambda x: x.split(' ')[-1])  # Prend le dernier mot comme catégorie (ex: "Basketball")
            
            # Vérifier et conserver la colonne image_url
            if 'image_url' not in df.columns:
                df['image_url'] = None  # Ajouter une colonne vide si elle n'existe pas
            
            # Supprimer la colonne 'Category'
            df = df.drop(columns=['Category'])

            data_frames.append(df)

# Concaténer tous les DataFrames en un seul
final_data = pd.concat(data_frames, ignore_index=True)

# Supprimer les doublons basés sur la colonne 'url'
if 'url' in final_data.columns:
    initial_count = len(final_data)
    final_data = final_data.drop_duplicates(subset='url', keep='first')
    removed_count = initial_count - len(final_data)
    print(f"{removed_count} doublons ont été supprimés dans la colonne 'url'.")

# Sauvegarder le DataFrame final dans un fichier Excel
output_file = "Nike_Shoes_Data.xlsx"
final_data.to_excel(output_file, index=False)

print(f"Les données ont été exportées avec succès dans le fichier {output_file}")
