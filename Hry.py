from tkinter import *
import random

class Quiz:
    def __init__(self, master, questions):
        self.master = master
        self.questions = questions
        self.score = 0
        self.current_question_index = 0

        self.question_label = Label(master, text="", font=("Arial", 14))
        self.question_label.pack()

        self.answer_entry = Entry(master, font=("Arial", 12))
        self.answer_entry.pack()

        self.submit_button = Button(master, text="Odeslat", command=self.check_answer)
        self.submit_button.pack()

        self.next_question()

    def next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.config(text=question["question"])
            self.answer_entry.delete(0, END)
        else:
            self.show_score()

    def check_answer(self):
        user_answer = self.answer_entry.get().strip().lower()
        correct_answer = self.questions[self.current_question_index]["answer"].lower()
        if user_answer == correct_answer:
            self.score += 1
        self.current_question_index += 1
        self.next_question()

    def show_score(self):
        self.question_label.config(text=f"Konečné skóre: {self.score}/{len(self.questions)}")
        self.answer_entry.pack_forget()
        self.submit_button.pack_forget()

if __name__ == "__main__":
    questions = [
        {"question": "Kolik je 2 + 2?", "answer": "4"},
        {"question": "Kolik je 3 * 4?", "answer": "12"},
        {"question": "Kolik je 8 / 2?", "answer": "4"}
    ]

    root = Tk()
    root.title("Kvíz")
    quiz = Quiz(root, questions)
    root.mainloop()
