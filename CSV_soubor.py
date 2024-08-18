import wikipediaapi
import pandas as pd

# Inicializace API pro anglickou Wikipedii s user_agent
user_agent = 'my-wikipedia-api-script/1.0 (your-email@example.com)'
wiki_wiki = wikipediaapi.Wikipedia('en', user_agent=user_agent)


# Funkce pro získání obsahu článku
def get_page_content(title):
    page = wiki_wiki.page(title)
    return page.text


# Seznam článků k stažení
titles = [
    'Python (programming language)',
    'Data science',
    'Machine learning',
    'Artificial intelligence',
    'Czech Republic',
    'Czech language',
    'Czech grammar',
    'Quantum computing',
    'Blockchain',
    'Cryptocurrency',
    'Climate change',
    'Global warming',
    'Neural networks',
    'Deep learning',
    'Computer vision',
    'Natural language processing',
    'Robotics',
    'Internet of Things',
    'Big data',
    'Statistics',
    'Algorithms',
    'Software engineering',
    'Cybersecurity',
    'Database management',
    'Cloud computing',
    'Augmented reality',
    'Virtual reality',
    'Game development',
    'User interface design',
    'User experience',
    'Human-computer interaction',
    'Bioinformatics',
    'Genomics',
    'Nanotechnology',
    'Materials science',
    'Astronomy',
    'Space exploration',
    'Astrophysics',
    'Cosmology',
    'Particle physics',
    'Relativity',
    'Quantum mechanics',
    'String theory',
    'Theoretical physics',
    'Organic chemistry',
    'Inorganic chemistry',
    'Physical chemistry',
    'Biochemistry',
    'Environmental science',
    'Artificial neural network',
    'Supervised learning',
    'Unsupervised learning',
    'Reinforcement learning',
    'Support vector machines',
    'Decision trees',
    'Ensemble learning',
    'Feature engineering',
    'Dimensionality reduction',
    'Bias-variance tradeoff',
    'Overfitting and underfitting',
    'Model evaluation',
    'Gradient descent',
    'Backpropagation'
]

# Stažení článků a uložení do seznamu
data = []
for title in titles:
    content = get_page_content(title)
    data.append({'title': title, 'content': content})

# Vytvoření DataFrame a uložení do CSV
df = pd.DataFrame(data)
df.to_csv('wikipedia_articles.csv', index=False)

print("Data byla uložena do 'wikipedia_articles.csv'.")
