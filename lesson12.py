from collections import UserDict
from datetime import datetime
import pickle

class AddressBook(UserDict):

    def __init__(self):
        super().__init__()
        self.load_book()

    def add_record(self, name):
        self.check_record(name)
        new_user = Record(name)
        while True:
            user_phone = input(f'What phone you wanna add to {name}? (skip it if you don\'t want): ')
            if user_phone:
                new_user.add_phone(user_phone)
                print(f'New phone added to {name}')
            else:
                break
        while True:
            birthday = input(f'Add birthday of {name} in format "dd.mm.yyyy" (skip it if you don\'t want): ')
            if birthday:
                try:
                    new_user.add_birthday(birthday)
                    break
                except AttributeError:
                    pass
            else:
                break

        self.data[new_user.name.value] = new_user

    def check_days_to_birthday(self, name):
        checking = self.find_user(name)
        if checking:
            checking.days_to_birthday()
        else:
            print(f'{name} doesn\'t exist')

    def check_record(self, name):
        try:
            checker = self.data[name]
            if checker:
                raise ValueError(f'{name} already added! Try another name.')
        except KeyError:
            pass

    def find_user(self, name):
        return self.data.get(name)

    def show_all_records(self):
        result = ""
        for name, fields in self.data.items():
            if fields.birthday:
                if fields.birthday.value:
                    result += f"{name}: phones: {[phone.value for phone in fields.phones]}, " \
                              f"birthday {fields.birthday.value.date()}\n"
                else:
                    result += f"{name}: phones: {[phone.value for phone in fields.phones]}\n"
            else:
                result += f"{name}: phones: {[phone.value for phone in fields.phones]}\n"
        print(result)

    def search(self, information):
        result = ""
        for name, fields in self.data.items():
            if information.lower() in name.lower():
                result += f"{name}: phones: {[phone.value for phone in fields.phones]}\n"
            for item in [phone.value for phone in fields.phones]:
                if information in item:
                    result += f"{name}: phones: {[phone.value for phone in fields.phones]}\n"
        if not result:
            print(f'I didn\'t find any {information}')
        else:
            print(result)

    def remove_phones(self, name):
        checking = self.find_user(name)
        if checking:
            checking.remove_phone()
        else:
            print(f'{name} doesn\'t exist')

    def change_phones(self, name):
        checking = self.find_user(name)
        if checking:
            checking.change_phone()
            print(f'New phone added to {name}!')
        else:
            print(f'{name} doesn\'t exist')

    def change_birthday(self, name):
        checking = self.find_user(name)
        if checking:
            checking.change_birthday()
        else:
            print(f'{name} doesn\'t exist')

    def iterator(self):
        for name, fields in self.data.items():
            if fields.birthday:
                if fields.birthday.value:
                    yield f"{name}: phones: {[phone.value for phone in fields.phones]}, " \
                          f"birthday {fields.birthday.value.date()}"
                else:
                    yield f"{name}: phones: {[phone.value for phone in fields.phones]}"
            else:
                yield f"{name}: phones: {[phone.value for phone in fields.phones]}"

    def save_book(self):
        with open('users_book.bin', 'wb') as file:
            pickle.dump(self.data, file)

    def load_book(self):
        try:
            with open('users_book.bin', 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

class Name(Field):
    pass

class Phone(Field):
    @Field.value.setter
    def value(self, value):
        fixed_phone = self.sanitize_phone_number(value)
        if len(fixed_phone) < 10 or len(fixed_phone) > 12:
            raise ValueError('Wrong format of phone, must be 10 or 12 numbers')
        if not fixed_phone.isnumeric():
            raise ValueError('Wrong format of phone, must be only numbers')
        self._value = fixed_phone

    def sanitize_phone_number(self, phone):
        new_phone = (
            phone.strip()
            .replace("+", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        return new_phone

class Birthday(Field):
    @Field.value.setter
    def value(self, value):
        try:
            value = datetime.strptime(value, '%d.%m.%Y')
            self._value = value
        except ValueError:
            print('Wrong format of date, must be "dd.mm.yyyy"')

class Record:

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def days_to_birthday(self):
        if self.birthday:
            if self.birthday.value:
                current_date = datetime.now()
                birthday = self.birthday.value
                birthday = birthday.replace(year=current_date.year)
                if birthday < current_date:
                    birthday = birthday.replace(year=current_date.year + 1)
                result = birthday - current_date
                print(f'{result.days} left to {self.name.value} birthday.')
            else:
                print('I don\'t know when he have birthday')
        else:
            print('I don\'t know when he have birthday')

    def change_phone(self):
        new_phone = input('Input new phone: ')
        self.add_phone(new_phone)
        return new_phone

    def remove_phone(self):
        if self.phones:
            showing = dict(enumerate(self.phones, 1))
            while True:
                try:
                    print(f'What phone you want to remove? {showing}')
                    choosing = int(input('Choose № of this phone >>>'))
                    self.phones.remove(showing[choosing])
                    print(f'{showing[choosing]} removed')
                    break
                except ValueError:
                    print(f'{choosing} is not a number!')
                except KeyError:
                    print(f'{choosing} is out of range!')

        else:
            print('Phones list is empty')

    def change_birthday(self):
        new_birthday = input('Input new birthday: ')
        self.add_birthday(new_birthday)


USERS = AddressBook()

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return 'This contact doesnt exist, please try again.'
        except ValueError as exception:
            return exception.args[0]
        except IndexError:
            return 'This contact cannot be added, it exists already'
        except TypeError:
            return 'Unknown command or parameters, please try again.'
    return inner


@input_error
def add_user(name):
    USERS.add_record(name)
    return f"User {name} added"

@input_error
def remove_phone(name):
    USERS.remove_phones(name)
    return f'Do you wanna do something else?'

@input_error
def change_phone(name):
    USERS.change_phones(name)
    return f'Do you wanna do something else?'

@input_error
def change_birthday(name):
    USERS.change_birthday(name)
    return f'Do you wanna do something else?'

@input_error
def show_days_to_birthday(name):
    USERS.check_days_to_birthday(name)
    return f'Do you wanna do something else?'

def iter_book(n):
    try:
        n = int(n)
        iter_b = USERS.iterator()
        for i in range(n):
            print(next(iter_b))
        ask = input(f'Do you wanna show next {n} contacts? (skip it if you don\'t want): ')
        while ask:
            for i in range(n):
                print(next(iter_b))
            ask = input(f'Do you wanna show next {n} contacts? (skip it if you don\'t want): ')

    except ValueError:
        print('You must write only numbers of how many contacts you want to see.')
    except StopIteration:
        print('There are no other numbers in the book.')
    return f'Do you wanna do something else?'

@input_error
def show_number(name):
    result = USERS.find_user(name)
    if result:
        return f"{name}: {[phone.value for phone in result.phones]}"
    else:
        print(f'User {name} doesn\'t exist.')
        return f'Do you wanna do something else?'

@input_error
def search_information(information):
    USERS.search(information)
    return f'Do you wanna do something else?'

HANDLERS = {

    "add": add_user,
    "change_phone": change_phone,
    "change_birthday": change_birthday,
    "remove_phone": remove_phone,
    "phone": show_number,
    "when": show_days_to_birthday,
    "iter": iter_book,
    "search": search_information
}

EXIT_COMMANDS = ("exit", "close", "good bye", "off", "stop", "quit")
SHOW_ALL_LIST_COMMANDS = ("show", "show_all", "show all")


def parser_input(user_input):
    try:
        inputed = user_input.split()
        cmd = inputed[0]
        name = inputed[1]
        handler = HANDLERS[cmd.lower()]
        return handler, name
    except IndexError:
        print('Write something else')


def main():
    while True:
        user_input = input(">>>")
        if user_input.lower() in EXIT_COMMANDS:
            print("Good bye!")
            break
        elif user_input.lower() in SHOW_ALL_LIST_COMMANDS:
            USERS.show_all_records()
            continue

        try:
            handler, name = parser_input(user_input)
            result = handler(name)
        except KeyError:
            result = f'Unknown command "{user_input}", please try again.'
        except TypeError:
            result = f'You wrote something strange'
        finally:
            USERS.save_book()

        print(result)


if __name__ == "__main__":
    main()