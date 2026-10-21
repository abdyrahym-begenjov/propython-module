import json
import pickle

def pyread(filename, encoding='utf-8', as_list=False):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'r', encoding=encoding) as file:
                result=file.read().strip()
                return result if as_list==False else result.split('\n')
        case filename if filename.endswith('.json'):
            with open(filename, 'r', encoding=encoding) as file:
                return json.load(file)
        case filename if filename.endswith('.pickle'):
            with open(filename, 'rb') as file:
                return pickle.load(file)
        case _:
            raise ValueError('Unsupported File!!!')
        
def pyadd(filename, value, encoding='utf-8'):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'a', encoding=encoding) as file:
                match value:
                    case value if type(value) in (str, int, float, bool):
                        file.write(value)
                    case _:
                        file.writelines(value)
        case filename if filename.endswith(('.json', '.pickle')):
            file=pyread(filename)
            file=pyupdate(file, value)
            pywrite(filename, file)
        case _:
            raise ValueError('Unsupported File!!!')
        
def pyupdate(d1, d2):
    for i in d2:
        if i in d1:
            if isinstance(d1[i], list) and isinstance(d2[i], list):
                d1[i]=d1[i]+d2[i]
            elif isinstance(d1[i], list) and isinstance(d2[i], (str, int, float, bool)):
                d1[i].append(d2[i])
            elif isinstance(d1[i], (str, int, float, bool)) and isinstance(d2[i], list):
                d1[i]=[d1[i]]
                d1[i].extend(d2[i])
            elif isinstance(d1[i], dict) and isinstance(d2[i], dict):
                pyupdate(d1[i], d2[i])
            else:
                d1[i]=[d1[i], d2[i]]
        else:
            d1[i]=d2[i]
    return d1
                     
def pywrite(filename, value, encoding='utf-8'):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'w', encoding=encoding) as file:
                match value:
                    case value if type(value) in (str, int, float, bool):
                        file.write(value)
                    case _:
                        file.writelines(value)
        case filename if filename.endswith('.json'):
            with open(filename, 'w', encoding=encoding) as file:
                json.dump(value, file)
        case filename if filename.endswith('.pickle'):
            with open(filename, 'wb') as file:
                pickle.dump(value, file)
        case _:
            raise ValueError('Unsupported File!!!')

def super_round(value, num=0):
    n1=1 if value>=0 else -1
    a, b=str(f"{abs(value)}").split('.')
    if b=='0':
        return int(a)
    if len(b)<num+1:
        b=b.ljust(len(b)+(num+1-len(b)), '0')
    elif len(b)>num+1:
        b=b[:num+1]
    b_list=list(b[::-1])
    if b_list[0] in ['5', '6', '7', '8', '9']:
        n2=1
        for i in range(1, len(b_list)):
            b_list[i]=str(int(b_list[i])+n2)
            if b_list[i]=='10':
                b_list[i]='0'
                n2=1
            else:
                n2=0
                break
    else:
        n2=0
    b_list[0]='0'
    b_list=reversed(b_list)
    result=f'{n2+int(a)}.{''.join(b_list)}'
    return n1*float(result)

def root(number, base=2, precision=2):
    if base<2:
        raise ValueError("The degree of the root must be greater than or equal to 2!!!")
    if number<0 and base%2==0:
        raise ValueError("You can't extract the root of an even power from a negative number!!!")
    else:
        n=1 if number>=0 else -1
        result=abs(number)**(1/base)
        return super_round(n*result, precision)

def quadratic_equation(a, b=0, c=0):
    if a==0:
        if b==0:
            return None
        return -c/b
    d=b**2-(4*a*c)
    if d<0:
        return None
    elif d==0:
        return -b/(2*a)
    else:
        x1=((-b)+root(d))/(2*a)
        x2=((-b)-root(d))/(2*a)
        return (x1, x2)
    
def onelist(lst):
    result=[]
    for i in lst:
        if isinstance(i, list):
            result.extend(onelist(i))
        else:
            result.append(i)
    return result