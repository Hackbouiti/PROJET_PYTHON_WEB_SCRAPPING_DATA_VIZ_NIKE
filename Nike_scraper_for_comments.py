from playwright.sync_api import sync_playwright
import pandas as pd
import sys

# Configurer UTF-8 pour la console
sys.stdout.reconfigure(encoding='utf-8')

def scrape_reviews(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False pour voir le navigateur
        page = browser.new_page()

        try:
            # Charger la page avec un délai d'attente prolongé
            page.goto(url, timeout=60000)
            print(f"Chargement de la page : {url}")

            # Fermer la fenêtre contextuelle si elle apparaît
            try:
                popup_close_button = page.locator("button[data-testid='modal-close-button']")
                popup_close_button.wait_for(state="visible", timeout=5000)
                popup_close_button.click()
                print("Fenêtre contextuelle fermée.")
            except:
                print("Aucune fenêtre contextuelle détectée.")

            # Forcer l'ouverture de la section des avis
            try:
                page.evaluate("document.querySelector('details#pdp-info-accordions__reviews-accordion').setAttribute('open', 'true')")
            except:
                print(f"Impossible d'ouvrir la section des avis pour l'URL : {url}")
                return []

            # Vérifier si le bouton "Avis supplémentaires" existe
            try:
                page.locator("button[data-testid='more-reviews-button']").wait_for(state="visible", timeout=5000)
                page.click("button[data-testid='more-reviews-button']")
                print("Bouton 'Avis supplémentaires' cliqué.")
            except:
                print(f"Pas de bouton 'Avis supplémentaires' trouvé pour l'URL : {url}. Aucun avis à collecter.")
                return []

            # Initialisation des avis collectés
            reviews = []

            while True:
                # Extraire les avis de la page actuelle
                review_elements = page.locator("span.tt-c-review__text-content")
                if review_elements.count() > 0:
                    for element in review_elements.all():
                        reviews.append(element.inner_text().strip())
                    print(f"Nombre d'avis récupérés jusqu'à présent pour {url}: {len(reviews)}")
                else:
                    print(f"Aucun avis trouvé sur cette page pour {url}.")

                # Vérifier si le bouton "Suivant" est présent et activé
                next_button = page.locator("button.tt-o-pagination__next:not([disabled])")
                if next_button.count() == 0:
                    print(f"Dernière page atteinte pour {url}.")
                    break

                # Cliquer sur le bouton "Suivant" pour passer à la page suivante
                next_button.click()
                print(f"Passage à la page suivante pour {url}...")
                page.wait_for_timeout(3000)  # Attendre un peu pour laisser la page se charger

            return reviews

        except Exception as e:
            print(f"Erreur lors du chargement de l'URL {url}: {e}")
            return []

        finally:
            browser.close()

# Charger le DataFrame existant
input_file = "Nike_Shoes_Data.xlsx"
df_urls = pd.read_excel(input_file)
urls = df_urls['url'].tolist()

# Collecter les commentaires pour chaque URL
all_reviews = []
for url in urls:
    reviews = scrape_reviews(url)
    if not reviews:
        reviews.append("")  # Si aucun avis, ajouter une ligne vide
    for review in reviews:
        all_reviews.append({'url': url, 'commentaire': review})

# Créer le nouveau DataFrame
df_reviews = pd.DataFrame(all_reviews)

# Sauvegarder le DataFrame dans un fichier Excel
output_file = "Nike_Shoes_Comments.xlsx"
df_reviews.to_excel(output_file, index=False)
print(f"Commentaires collectés sauvegardés dans {output_file}.")
