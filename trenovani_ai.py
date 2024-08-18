import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import random
import pickle
import matplotlib.pyplot as plt

# Načtení dat z CSV
df = pd.read_csv('video_game_questions.csv')
texts = df['question'].tolist()
answers = df['answer'].tolist()

# Tokenizace textu
tokenizer = Tokenizer()
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
data = pad_sequences(sequences)

# Konverze na numpy array
data = np.array(data)
labels = np.array(range(len(texts)))


# Model
def create_model(vocab_size, input_length):
    model = Sequential()
    model.add(Embedding(input_dim=vocab_size, output_dim=10, input_length=input_length))
    model.add(LSTM(20))
    model.add(Dense(len(texts), activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


vocab_size = len(tokenizer.word_index) + 1
input_length = data.shape[1]

model = create_model(vocab_size, input_length)
history = model.fit(data, labels, epochs=10, validation_split=0.1, verbose=1)

# Plot training & validation accuracy and loss
plt.plot(history.history['accuracy'])
plt.title('Model accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.show()

plt.plot(history.history['loss'])
plt.title('Model loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.show()

# Mapování identifikátorů na otázky a odpovědi
id_to_question = {i: q for i, q in enumerate(texts)}
id_to_answer = {i: a for i, a in enumerate(answers)}

# Sada šablon pro otázky a odpovědi
templates = [
    ("What's the capital of {}?", "The capital of {} is {}."),
    ("Who is the president of {}?", "The president of {} is {}."),
    ("Tell me a fun fact about {}.", "A fun fact about {} is that {}."),
    ("What is the population of {}?", "The population of {} is {}."),
    ("What is the largest city in {}?", "The largest city in {} is {}."),
    ("What is the official language of {}?", "The official language of {} is {}."),
    ("What currency is used in {}?", "The currency used in {} is {}."),
    ("What is the area of {}?", "The area of {} is {} square kilometers."),
    ("When was {} founded?", "{} was founded in {}."),
    ("What is the highest mountain in {}?", "The highest mountain in {} is {}."),
]

# Sada náhodných slov pro šablony
words = [
    ("France", "Paris"),
    ("USA", "Joe Biden"),
    ("the Sun", "it's a star."),
    ("China", "Beijing"),
    ("India", "New Delhi"),
    ("Brazil", "Brasília"),
    ("Canada", "Ottawa"),
    ("Australia", "Canberra"),
    ("Russia", "Moscow"),
    ("Japan", "Tokyo"),
    ("Germany", "Berlin"),
    ("Mexico", "Mexico City"),
    ("Italy", "Rome"),
    ("South Africa", "Pretoria"),
    ("Egypt", "Cairo"),
    ("Spain", "Madrid"),
    ("United Kingdom", "London"),
    ("Argentina", "Buenos Aires"),
    ("Kenya", "Nairobi"),
    ("Thailand", "Bangkok"),
]


# Funkce pro generování vlastní otázky a odpovědi
def generuj_otazku_odpoved():
    template = random.choice(templates)
    word = random.choice(words)
    question = template[0].format(word[0])
    answer = template[1].format(word[0], word[1])
    return question, answer


# Použití modelu pro predikci
def predikce(text):
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=data.shape[1])
    pred = model.predict(padded)
    pred_index = pred.argmax()
    return pred_index, id_to_question[pred_index], id_to_answer[pred_index]


# Ověření odpovědi a přidání nové otázky a odpovědi na základě zpětné vazby
def overeni(text, pred_question, pred_answer):
    global data, labels, tokenizer, model, vocab_size, input_length
    print(f"Predikce pro '{text}':")
    print(f"Otázka: {pred_question}")
    print(f"Odpověď: {pred_answer}")
    user_input = input("Je to správně? (ano/ne): ").strip().lower()
    if user_input == 'ano':
        print("Děkuji, odpověď byla správná.")
    else:
        nova_otazka = input("Zadejte správnou otázku: ")
        nova_odpoved = input("Zadejte správnou odpověď: ")
        texts.append(nova_otazka)
        answers.append(nova_odpoved)
        tokenizer.fit_on_texts([nova_otazka])
        new_sequence = tokenizer.texts_to_sequences([nova_otazka])
        new_padded = pad_sequences(new_sequence, maxlen=data.shape[1])
        data = np.append(data, new_padded, axis=0)
        labels = np.append(labels, [len(labels)])

        # Update model
        retrain_model(texts, answers)

        print("Nová otázka a odpověď byly přidány do modelu.")


# Funkce pro retrénování modelu na nových datech
def retrain_model(new_texts, new_answers):
    global data, labels, tokenizer, model, vocab_size, input_length

    # Přidání nových dat
    tokenizer.fit_on_texts(new_texts)
    new_sequences = tokenizer.texts_to_sequences(new_texts)
    new_data = pad_sequences(new_sequences, maxlen=input_length)
    data = np.append(data, new_data, axis=0)
    labels = np.append(labels, np.arange(len(labels), len(labels) + len(new_texts)))

    # Aktualizace modelu
    vocab_size = len(tokenizer.word_index) + 1
    model = create_model(vocab_size, input_length)
    history = model.fit(data, labels, epochs=10, validation_split=0.1, verbose=1)

    # Plot training & validation accuracy and loss
    plt.plot(history.history['accuracy'])
    plt.title('Model accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.show()

    plt.plot(history.history['loss'])
    plt.title('Model loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.show()


# Generování a ověřování více otázek
def generuj_a_over_otazky(pocet):
    global data, labels, tokenizer, model, vocab_size, input_length
    for _ in range(pocet):
        generated_question, generated_answer = generuj_otazku_odpoved()
        print(f"Generovaná otázka: {generated_question}")
        print(f"Generovaná odpověď: {generated_answer}")
        user_input = input("Je tato odpověď správná? (ano/ne): ").strip().lower()
        if user_input == 'ano':
            print("Děkuji, odpověď byla správná.")
        else:
            nova_otazka = input("Zadejte správnou otázku: ")
            nova_odpoved = input("Zadejte správnou odpověď: ")
            texts.append(nova_otazka)
            answers.append(nova_odpoved)
            tokenizer.fit_on_texts([nova_otazka])
            new_sequence = tokenizer.texts_to_sequences([nova_otazka])
            new_padded = pad_sequences(new_sequence, maxlen=data.shape[1])
            data = np.append(data, new_padded, axis=0)
            labels = np.append(labels, [len(labels)])

            # Update model
            retrain_model(texts, answers)

            print("Nová otázka a odpověď byly přidány do modelu.")
        print()


# Testování
text = 'How are you?'
pred_index, pred_question, pred_answer = predikce(text)
print(f"Predikce pro '{text}': {pred_question}")
print(f"Predikovaná odpověď: {pred_answer}")
overeni(text, pred_question, pred_answer)

# Generování a ověřování více otázek
pocet_otazek = 5
generuj_a_over_otazky(pocet_otazek)

# Uložení modelu a tokenizátoru
model.save('qa_model.h5')
with open('tokenizer.pkl', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
