import requests
from bs4 import BeautifulSoup
import re


def google_search(query, api_key, cse_id):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    response = requests.get(url)
    results = response.json()
    return results.get('items', [])


def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paragraphs])
        print("Extracted text (first 1000 characters):", text[:1000])  # Print first 1000 chars for debugging
        return text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""


def extract_person_name(text):
    # Improved regex pattern to capture common name formats
    names = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b', text)
    print("Detected names:", names)  # Print detected names for debugging
    if names:
        return names[0]  # Returning the first name found
    return "Name not found"


def generate_answer(query, api_key, cse_id):
    results = google_search(query, api_key, cse_id)

    if not results:
        return "Sorry, I couldn't find any information."

    # Extract text from the top result
    top_result = results[0]
    link = top_result.get('link', '')
    print(f"Fetching URL: {link}")  # Debugging output
    text = extract_text_from_url(link)

    # Extract a name or key person from the text
    person_name = extract_person_name(text)

    return f"The person you're looking for is: {person_name}"


# Main function to start the script
def main():
    choice = input("Chcete (1) zpracovávat CSV soubor nebo (2) vyhledávat na internetu? (zadejte 1 nebo 2): ").strip()

    if choice == '1':
        file_path = input("Zadejte cestu k CSV souboru: ").strip()
        # Add your CSV handling code here (not included in this snippet)

    elif choice == '2':
        query = input("Zadejte dotaz pro vyhledávání: ").strip()
        api_key = 'AIzaSyCd9ShNXjjD7ANDs9cJuWbSacn5tnQdBGs'
        cse_id = '6036cfc841708424c'
        answer = generate_answer(query, api_key, cse_id)
        print(answer)

    else:
        print("Neplatná volba. Prosím, zadejte 1 nebo 2.")


if __name__ == '__main__':
    main()
