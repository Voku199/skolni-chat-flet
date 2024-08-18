import requests
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Nastavte API klíč a endpoint pro vyhledávání
API_KEY = 'AIzaSyDIC_OANSSp1qxXpkyxOCDwDKJCcPAvwss'
SEARCH_ENGINE_ID = 'a11dd8b6c54bb4419'
SEARCH_URL = f'https://www.googleapis.com/customsearch/v1?q={{query}}&key={API_KEY}&cx={SEARCH_ENGINE_ID}'


# Funkce pro získání dat z API
def fetch_search_results(query):
    response = requests.get(SEARCH_URL.format(query=query))
    results = response.json()
    return results.get('items', [])


# Funkce pro generování odpovědí na základě vyhledávání
def generate_answer_from_web(query):
    search_results = fetch_search_results(query)
    context = ' '.join(item['snippet'] for item in search_results)

    # Inicializace modelu a tokenizéru
    model_name = 'gpt2'
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Přidání kontextu a generování odpovědi
    input_text = f"Context: {context}\nQuestion: {query}\nAnswer:"
    inputs = tokenizer.encode(input_text, return_tensors='pt')
    outputs = model.generate(inputs, max_length=200, num_return_sequences=1)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer


# Testování
query = 'What is the capital of France?'
answer = generate_answer_from_web(query)
print(f"Answer: {answer}")
