
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- Configurações ---
URL = 'https://www.imdb.com/chart/moviemeter/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
CSV_FILENAME = 'movies.csv'

def scrape_imdb_movies(url: str, headers: dict) -> list:
    """
    Acessa o site do IMDb, extrai os dados dos filmes e retorna uma lista de dicionários.
    """
    print(f"Acessando a URL: {url}")
    
    try:
        # 1. Acessar o site
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Lança uma exceção para erros HTTP (4xx ou 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL: {e}")
        return []

    # 2. Analisar o HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar a tabela de filmes (o seletor pode mudar se o IMDb alterar o layout)
    movie_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
    
    movie_data = []
    
    # 3. Extrair os dados
    print(f"Encontrados {len(movie_items)} filmes. Extraindo dados...")
    for item in movie_items:
        try:
            # Título
            title_tag = item.find('h3', class_='ipc-title__text')
            title = title_tag.text.split('.', 1)[-1].strip() if title_tag else 'N/A'
            
            # Posição no Ranking (é o número antes do título)
            position_text = title_tag.text.split('.', 1)[0] if title_tag else 'N/A'
            position = int(position_text) if position_text.isdigit() else 'N/A'

            # Metadados: Ano, Duração, Classificação (estão em um grupo)
            metadata_tags = item.find_all('span', class_='sc-b189961a-8')
            year = metadata_tags[0].text if metadata_tags and len(metadata_tags) > 0 else 'N/A'
            
            # Nota (Rating)
            rating_tag = item.find('span', class_='ipc-rating-star--imdb')
            rating = rating_tag.find('span').text if rating_tag and rating_tag.find('span') else 'N/A'

            movie_data.append({
                'Posicao': position,
                'Titulo': title,
                'Ano': year,
                'Nota_IMDb': rating,
            })
            
        except Exception as e:
            # Captura erros de extração para um item específico e segue para o próximo
            print(f"Erro ao processar um item de filme: {e}")
            continue

    return movie_data

def export_to_csv(data: list, filename: str):
    """
    Converte a lista de dicionários para um DataFrame do Pandas e exporta para CSV.
    """
    if not data:
        print("Nenhum dado para exportar.")
        return

    # 4. Tratamento e Exportação com Pandas
    df = pd.DataFrame(data)
    
    # Ordenar por Posição, se o campo for numérico
    df['Posicao'] = pd.to_numeric(df['Posicao'], errors='coerce')
    df = df.sort_values(by='Posicao', ascending=True).reset_index(drop=True)
    
    # Salvar
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\nDados exportados com sucesso para '{filename}'")
    print(f"Total de {len(df)} filmes salvos.")

if __name__ == '__main__':
    # 5. Execução principal
    movies = scrape_imdb_movies(URL, HEADERS)
    export_to_csv(movies, CSV_FILENAME)