import speech_recognition as sr
import csv
from nltk.tokenize import word_tokenize
import numpy as np
import json
import sys

print("Welcome! You are talking to Seidor's warehouse shopping list AI voice assistant.")
print("\n")
print("You can add items to the list by saying 'insert' followed by the item name.")
print("You can also specify the quantity by saying 'units' followed by the quantity.")
print("For example: 'insert oxyspeed 2 units'")
print("\n")
print("You can delete items from the list by saying 'delete' followed by the item name.")
print("For example: 'delete oxyspeed'")
print("\n")
print("You can confirm the shopping list by saying 'confirm'.")
print("If you want to cancel the shopping list, just say 'cancel'.")
print("\n")
print("Devoleped by Jaume Mora, Carlos Lopez, Sergi Adrover and Jordi Roca.")
print("\n")


list_id = 0
r = sr.Recognizer()

def initialize_json(filename='shoppingList.json'):
    initial_data = {"products": []}
    #print("Initializing JSON file..." + filename)
    with open(filename, 'w') as file:
        json.dump(initial_data, file)

# Call the function to initialize the JSON file
initialize_json()

words_in_csv = set()
with open('products.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)  # Skip the header
    for row in reader:
        words_in_csv.update(word_tokenize(row[1].lower()))  # Convert to lowercase for case-insensitive comparison

words_in_csv_easy = set()
quantity_in_csv = np.array([])
with open('productsCopy.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)  # Skip the header
    for row in reader:
        words_in_csv_easy.update(word_tokenize(row[0].lower()))
        quantity_in_csv = np.append(quantity_in_csv, row[1])

#print (words_in_csv_easy, "noonon")
#print(quantity_in_csv, "yeeys")
def save_csv(data, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def record_text():
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.1)
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            #textAux = find_closest_match(text.lower(), words_in_csv_easy)
            #print(f"I understood: {text}")
            return text.lower()
        
        except sr.UnknownValueError:
            print("Sorry I didn't get that, please try again.")
            return None
        
def add_to_list(text, quantity):
    try:
        # Load existing data from file
        with open('shoppingList.json', 'r') as file:
            data = json.load(file)
        #print("data",data,data['products'])
        
        # Add new item to the products
        data['products'].append({"name": text, "amount": quantity})

        # Write data back to file
        with open('shoppingList.json', 'w') as file:
            json.dump(data, file, indent=4)  # indent for better readability of the JSON file
        
        print(f"Added {quantity} {text} to the shopping list.")

    except FileNotFoundError:
        print("The file was not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")

def print_json():
    with open('shoppingList.json', 'r') as file:
        data = json.load(file)
    for product in data['products']:
        print(product)

def delete_from_list(text):
    # Load existing data
    try:
        with open('shoppingList.json', 'r') as file:
            data = json.load(file)

        # Remove item from the products
        data['products'] = [item for item in data['products'] if item["name"] != text]

        # Write data back to file
        with open('shoppingList.json', 'w') as file:
            json.dump(data, file)
        
        print(f"Deleted {text} from the shopping list.")
    except FileNotFoundError:
        print("The file was not found.")

def detect_ammount(text):
    try:
        words = word_tokenize(text)
        for word in words:
            if word.isdigit():
                return word
        return 1
    except TypeError:
        return 1

def interpret_text(text):
    global list_id  # Add this line to declare list_id as global
    if (check_substring(text, 'insert') or check_substring(text, 'insect')):
        auxText = text.split('insert')
        if (len(auxText) > 1):
            what_to_add = find_closest_match(auxText[1], words_in_csv)
            if (check_substring(text, 'units')):
                ammount = detect_ammount(auxText[1])
                print(f"Adding: {ammount} units of {what_to_add}")
                add_to_list(what_to_add, ammount)
                
            else:
                print(f"How many {what_to_add} do you want to add?")
                quantity = detect_ammount(record_text())
                add_to_list(what_to_add, quantity)
        else:
            print("Please specify the product you want to add.")
            add_to_list(find_closest_match(record_text(), words_in_csv), 3)
            

    elif (check_substring(text, 'delete')):
        auxText = text.split('delete')
        if (len(auxText) > 1):
            what_to_delete = find_closest_match(auxText[1], words_in_csv)
            print(f"Deleting: {what_to_delete}")
            delete_from_list(what_to_delete)
        else:
            print("Please specify the product you want to delete.")
            delete_from_list(find_closest_match(record_text(), words_in_csv))

    elif (check_substring(text, 'confirm')):
        print("Your shopping list:")
        print_json()
        print("Want to confirm?")
        confirmation = record_text()
        entering = True
        while entering:
            if check_substring(confirmation, 'yes') or check_substring(confirmation, 'confirm') or check_substring(confirmation, 'correct') or check_substring(confirmation, 'ok'):
                print("Saving shopping list...")
                print("...")
                print("Shopping list saved successfully. Have a nice day!")
                entering = False
                confirmed = True
                sys.exit()
            elif check_substring(confirmation, 'no') or check_substring(confirmation, 'cancel') or confirmation == 'wrong':
                print("Shopping list not saved, you can continue modifying it.")
                entering = False
            else:
                print("I'm sorry, I didn't understand that. Please try again.")
                confirmation = record_text()
    else:
        print("I'm sorry, I didn't understand that. Please try again.")


def check_substring(main_string, sub_string):
    try:
        if sub_string in main_string:
            return True
        else:
            return False
    except TypeError:
        return False

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def find_closest_match(text, words):
    min_distance = float('inf')
    closest_match = None
    for entry in words:
        distance = levenshtein(text, entry)
        if distance < min_distance:
            min_distance = distance
            closest_match = entry
    return closest_match
confirmed = False
while not confirmed:
    interpret_text(record_text())

