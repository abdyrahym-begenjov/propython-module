import json
import pickle
from collections import deque
from pandas import read_csv, concat, DataFrame, read_sql, read_excel, ExcelWriter
from numpy import issubdtype, integer, floating
from inspect import signature
from sqlalchemy import create_engine
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from os.path import exists

data_structures=(list, tuple, set, frozenset, deque)
data_types=(str, int, float, bool)
csvread_parameters=[i for i in signature(read_csv).parameters]
csvrewrite_parameters=[i for i in signature(DataFrame.to_csv).parameters]
excelread_parameters=[i for i in signature(read_excel).parameters]

colors={
    'black': '000000',
    'white': 'FFFFFF',
    'red': 'FF0000',
    'lime': '00FF00',
    'blue': '0000FF',
    'yellow': 'FF00FF',
    'cyan': '00FFFF',
    'grey': 'A9A9A9',
    'green': '008000',
    'orange': 'FFA500',
    'brown': '8B4513',
    'purple': '800080'
}

type_formats={
    'category': '@',
    'datetime64[ns]': 'yyyy-mm-dd',
    'object': '@',
    'integer': '#,##0',
    'float': '#,##0.##',
    'default': 'General'
}

def pyread(filename, *, encoding='utf-8', as_list=False, **kwargs):
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
        case filename if filename.endswith('.csv'):
            return read_csv(filename, encoding=encoding, **kwargs)
        case filename if filename.endswith('.xlsx'):
            return read_excel(filename, **kwargs)
        case _:
            raise ValueError('Unsupported File!!!')
        
def pyadd(filename, value, *, encoding='utf-8', sheet_name=None, **kwargs):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'a', encoding=encoding) as file:
                match value:
                    case value if type(value) in data_types:
                        file.write(value)
                    case _:
                        file.writelines(value)
        case filename if filename.endswith(('.json', '.pickle')):
            file=pyread(filename, encoding=encoding)
            file=pyupdate(file, value)
            pyrewrite(filename, file)
        case filename if filename.endswith('.csv'):
            kw1={i: j for i, j in kwargs.items() if i in csvread_parameters}
            file=pyread(filename, encoding=encoding, **kw1)
            file=concat([file, value])
            kw2={i: j for i, j in kwargs.items() if i in csvrewrite_parameters}
            pyrewrite(filename, file, **kw2)
        case filename if filename.endswith('.xlsx'):
            value=[value] if not isinstance(value, list) else value
            sheet_name=[sheet_name] if not isinstance(sheet_name, list) else sheet_name
            if len(value)==len(sheet_name):
                kw1={i: j for i, j in kwargs.items() if i in excelread_parameters}
                file=pyread(filename,  sheet_name=sheet_name, **kw1)
                df_list=[concat([i, j]) for i, j in zip(file.values(), value)]
                kw2={i: j for i, j in kwargs.items() if i in excelrewrite_parameters}
                pyrewrite(filename, df_list, sheet_name=sheet_name, **kw2)
            else:
                raise ValueError('The number of values should be equal to the number of sheet names!!!')
        case _:
            raise ValueError('Unsupported File!!!')

def pyupdate(d1, d2):
    for i in d2:
        if i in d1:
            if isinstance(d1[i], data_structures) and isinstance(d2[i], data_structures):
                d1[i]=d1[i]+d2[i]
            elif isinstance(d1[i], data_structures) and isinstance(d2[i], data_types):
                d1[i].append(d2[i])
            elif isinstance(d1[i], data_types) and isinstance(d2[i], data_structures):
                d1[i]=[d1[i]]
                d1[i].extend(d2[i])
            elif isinstance(d1[i], dict) and isinstance(d2[i], dict):
                pyupdate(d1[i], d2[i])
            else:
                d1[i]=[d1[i], d2[i]]
        else:
            d1[i]=d2[i]
    return d1
                     
def pyrewrite(filename, value, *, encoding='utf-8', sheet_name=None, head_font='Arial', head_size=12, 
              head_font_color='black', head_cell_color='white', font='Arial', size=11, font_color='black', 
              cell_color='white', **kwargs):
    match filename:
        case filename if filename.endswith('.txt'):
            with open(filename, 'w', encoding=encoding) as file:
                match value:
                    case value if type(value) in data_types:
                        file.write(value)
                    case _:
                        file.writelines(value)
        case filename if filename.endswith('.json'):
            with open(filename, 'w', encoding=encoding) as file:
                json.dump(value, file)
        case filename if filename.endswith('.pickle'):
            with open(filename, 'wb') as file:
                pickle.dump(value, file)
        case filename if filename.endswith('.csv'):
            value.to_csv(filename, encoding=encoding, **kwargs)
        case filename if filename.endswith('.xlsx'):
            value=[value] if not isinstance(value, list) else value
            if sheet_name is None:
                sheet_name=[f'Sheet{i}' for i in range(1, len(value)+1)]
            else:
                sheet_name=[sheet_name] if not isinstance(sheet_name, list) else sheet_name
            if len(value)==len(sheet_name):
                mode='a' if exists(filename) else 'w'
                if_sheet_exists='replace' if exists(filename) else 'error'
                with ExcelWriter(filename, mode=mode, if_sheet_exists=if_sheet_exists, engine='openpyxl') as writer:
                    for i, j in zip(value, sheet_name):
                        i.to_excel(writer, sheet_name=j, index=False)
                        worksheet=writer.sheets[j]
                        header_font=Font(name=head_font, size=head_size, bold=True, color=colors[head_font_color])
                        header_fill=PatternFill(start_color=colors[head_cell_color], 
                                                end_color=colors[head_cell_color], fill_type='solid')
                        data_font=Font(name=font, size=size, color=colors[font_color])
                        data_fill=PatternFill(start_color=colors[cell_color], 
                                              end_color=colors[cell_color], fill_type='solid')
                        center_alignment=Alignment(horizontal='center', vertical='center')
                        for col_idx in range(1, len(i.columns)+1):
                            cell=worksheet.cell(row=1, column=col_idx)
                            cell.font=header_font
                            cell.fill=header_fill
                            cell.alignment=center_alignment
                        for row in range(2, len(i)+2):
                            for col in range(1, len(i.columns)+1):
                                cell=worksheet.cell(row=row, column=col)
                                cell.font=data_font
                                cell.fill=data_fill
                                col_name=i.columns[col-1]
                                value_type=i[col_name].dtype
                                if str(value_type) in type_formats:
                                    config=type_formats[str(value_type)]
                                elif issubdtype(value_type, integer):
                                    config=type_formats['integer']
                                elif issubdtype(value_type, floating):
                                    config=type_formats['float']
                                else:
                                    config=type_formats['default']
                                cell.number_format=config
                        for col in worksheet.columns:
                            max_len=max(len(str(cell.value or '')) for cell in col)
                            header_len=len(str(col[0].value or ''))
                            col_letter=col[0].column_letter
                            worksheet.column_dimensions[col_letter].width=max(max_len, header_len)+5
            else:
                raise ValueError('The number of values should be equal to the number of sheet names!!!')
        case _:
            raise ValueError('Unsupported File!!!')

excelrewrite_parameters=[i for i in signature(
    DataFrame.to_excel).parameters]+[i for i in signature(pyrewrite).parameters]
excelrewrite_parameters.remove('kwargs')

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
        if isinstance(i, data_structures):
            result.extend(onelist(i))
        else:
            result.append(i)
    return result

def make_sqlengine(db_name, db_user=None, db_password=None, db_host='localhost', db_port=5432, db_type='postgres'):
    match db_type.lower():
        case 'postgresql' | 'postgres':
            db_path=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        case 'mysql':
            db_path=f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        case 'sqlite':
            db_path=f"sqlite:///{db_name}"
        case _:
            raise ValueError("Unsupported database type!!!")
    return create_engine(db_path)

def sqlread(query, db_name, db_user=None, db_password=None, db_host='localhost', 
            db_port=5432, db_type='postgres', **kwargs):
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    result=read_sql(query, con=engine, **kwargs)
    return result

def sqlrewrite(table_name, new_value, db_name, db_user=None, db_password=None, 
               db_host='localhost', db_port=5432, db_type='postgres', chunksize=50000, **kwargs):
    kwargs.pop('if_exists', None)
    kwargs.pop('method', None)
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    for n, i in enumerate(range(0, len(new_value), chunksize)):
        chunk=new_value.iloc[i:i+chunksize]
        mode="replace" if n==0 else "append"
        chunk.to_sql(table_name, con=engine, if_exists=mode, index=False, method='multi', **kwargs)

def sqladd(table_name, new_value, db_name, db_user=None, db_password=None, 
           db_host='localhost', db_port=5432, db_type='postgres', chunksize=50000, **kwargs):
    kwargs.pop('if_exists', None)
    kwargs.pop('method', None)
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    for i in range(0, len(new_value), chunksize):
        chunk=new_value.iloc[i:i+chunksize]
        chunk.to_sql(table_name, con=engine, if_exists="append", index=False, method='multi', **kwargs)