import requests

# Remplacer l'URL par l'URL de l'API REST de Binance pour récupérer la liste des cryptomonnaies
url = "https://api.binance.com/api/v3/ticker/price"

# Envoyer une requête HTTP GET à l'URL pour récupérer la liste des cryptomonnaies
response = requests.get(url)

# Vérifier si la réponse est valide
if response.status_code == 200:
  # Récupérer les données de la réponse
  data = response.json()
  
  # Parcourir les données pour afficher le nom des cryptomonnaies
  for item in data:
    print(item["symbol"])
else:
  print("Erreur lors de la récupération de la liste des cryptomonnaies")