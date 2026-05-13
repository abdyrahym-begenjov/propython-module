import json
import pickle

def pyread(filename):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'r', encoding='utf-8') as file:
                return file.read().strip()
        case filename if filename.endswith('.json'):
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        case filename if filename.endswith('.pickle'):
            with open(filename, 'rb') as file:
                return pickle.load(file)
        case _:
            raise ValueError('Unsupported File!!!')

def cycleread(filename):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'r', encoding='utf-8') as file:
                for i in file:
                    print(i.strip())
        case _:
            raise ValueError('Unsupported File!!!')

def pyreadlines(filename):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'r', encoding='utf-8') as file:
                lst=file.readlines()
                return lst
        case _:
            raise ValueError('Unsupported File!!!')
        
def pyadd(filename, value):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'a', encoding='utf-8') as file:
                match value:
                    case value if type(value) in (str, int, float, bool):
                        file.write(value)
                    case _:
                        file.writelines(value)
        case _:
            raise ValueError('Unsupported File!!!')
                     
def pywrite(filename, value):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'w', encoding='utf-8') as file:
                match value:
                    case value if type(value) in (str, int, float, bool):
                        file.write(value)
                    case _:
                        file.writelines(value)
        case filename if filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(value, file)
        case filename if filename.endswith('.pickle'):
            with open(filename, 'wb') as file:
                pickle.dump(value, file)
        case _:
            raise ValueError('Unsupported File!!!')