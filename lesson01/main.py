contacts = []

def show_menu():
    print("1 瘛餃??頂鈭?)
    print("2 ?亦??頂鈭?)
    print("3 ??頂鈭?)
    print("0 ???)

def get_choice():
    choice = input()
    return choice

def input_contact():
    name = input("憪?嚗?)
    phone = input("?菔?嚗?)
    person = [name, phone]
    return person

def add_contact(contacts, person):
    contacts.append(person)

def show_contacts(contacts):
    if not contacts:
        print("?悖敶蛹蝛?)
        return
    for person in contacts:
        print("憪?嚗?, person[0])
        print("?菔?嚗?, person[1])
        print("----------------")

def delete_contact(contacts):
    if not contacts:
        print("?悖敶蛹蝛?)
        return
    show_contacts(contacts)
    number = input("霂瑁??亦??瘀?") 
    number = int(number)
    if 1 <= number <= len(contacts):
        contacts.pop(number - 1)
        print("???")
    else:
        print("蝻銝???)


while True:
    show_menu()

    choice = get_choice()

    if choice == "0":
        break
    elif choice == "1":
        person = input_contact()
        add_contact(contacts, person)
    elif choice == "2":
        show_contacts(contacts)
    elif choice == "3":
        delete_contact(contacts)

print("??箇?摨?)