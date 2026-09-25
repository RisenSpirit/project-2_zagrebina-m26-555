import prompt

def welcome():
    print("Первая попытка запустить проект!")
    # print("\n")
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            print()
            continue
        else:
            print(f"Неизвестная команда: {command}\n")
