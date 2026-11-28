import json
import pickle
import re
from datetime import datetime
from collections import deque
from pandas import read_csv, concat, DataFrame, read_sql, read_excel, ExcelWriter, read_parquet, Timestamp, DateOffset, to_datetime
from numpy import issubdtype, integer, floating
from inspect import signature
from sqlalchemy import create_engine
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from os.path import exists
from os import makedirs
from pyarrow.parquet import write_to_dataset
from pyarrow import Table

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
    'yellow': 'FFFF00',
    'cyan': '00FFFF',
    'grey': 'A9A9A9',
    'green': '008000',
    'orange': 'FFA500',
    'brown': '8B4513',
    'purple': '800080'
}

type_formats={
    'category': '@',
    'object': '@',
    'integer': '#,##0',
    'float': '#,##0.##',
    'default': 'General'
}

timezones = {
    'utc': 'UTC',
    'gmt': 'GMT',
    'ashgabat': 'Asia/Ashgabat',
    'turkmenistan': 'Asia/Ashgabat',
    'tmt': 'Asia/Ashgabat',
    'tashkent': 'Asia/Tashkent',
    'uzbekistan': 'Asia/Tashkent',
    'almaty': 'Asia/Almaty',
    'astana': 'Asia/Almaty',
    'kazakhstan': 'Asia/Almaty',
    'bishkek': 'Asia/Bishkek',
    'dushanbe': 'Asia/Dushanbe',
    'baku': 'Asia/Baku',
    'yerevan': 'Asia/Yerevan',
    'tbilisi': 'Asia/Tbilisi',
    'minsk': 'Europe/Minsk',
    'moscow': 'Europe/Moscow',
    'msk': 'Europe/Moscow',
    'yekaterinburg': 'Asia/Yekaterinburg',
    'novosibirsk': 'Asia/Novosibirsk',
    'vladivostok': 'Asia/Vladivostok',
    'dubai': 'Asia/Dubai',
    'uae': 'Asia/Dubai',
    'istanbul': 'Europe/Istanbul',
    'turkey': 'Europe/Istanbul',
    'tehran': 'Asia/Tehran',
    'beijing': 'Asia/Shanghai',
    'china': 'Asia/Shanghai',
    'tokyo': 'Asia/Tokyo',
    'japan': 'Asia/Tokyo',
    'seoul': 'Asia/Seoul',
    'singapore': 'Asia/Singapore',
    'delhi': 'Asia/Kolkata',
    'india': 'Asia/Kolkata',
    'london': 'Europe/London',
    'uk': 'Europe/London',
    'berlin': 'Europe/Berlin',
    'paris': 'Europe/Paris',
    'rome': 'Europe/Rome',
    'madrid': 'Europe/Madrid',
    'warsaw': 'Europe/Warsaw',
    'new_york': 'America/New_York',
    'est': 'America/New_York',
    'chicago': 'America/Chicago',
    'cst': 'America/Chicago',
    'denver': 'America/Denver',
    'mst': 'America/Denver',
    'phoenix': 'America/Phoenix',
    'los_angeles': 'America/Los_Angeles',
    'pst': 'America/Los_Angeles',
    'toronto': 'America/Toronto',
    'sao_paulo': 'America/Sao_Paulo'
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
        case filename if filename.endswith('.parquet'):
            return read_parquet(filename, **kwargs)
        case filename if filename.endswith('.xlsx'):
            result=read_excel(filename, **kwargs)
            if isinstance(result, dict) and len(result)==1:
                result=[i for i in result.values()]
                result=result[0]
            return result
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
        case filename if filename.endswith('.parquet'):
            makedirs(filename, exist_ok=True)
            table=Table.from_pandas(value)
            write_to_dataset(table, root_path=filename, **kwargs)
        case filename if filename.endswith('.xlsx'):
            value=[value] if not isinstance(value, list) else value
            if sheet_name is None:
                c=load_workbook(filename, read_only=True)
                try:
                    sheet_name=c.sheetnames
                finally:
                    c.close()
            else:
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
              cell_color='white', border_color='white', date_format='yyyy-mm-dd', 
              time_format='hh:mm:ss', **kwargs):
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
        case filename if filename.endswith('.parquet'):
            value.to_parquet(filename, **kwargs)
        case filename if filename.endswith('.xlsx'):
            value=[value] if not isinstance(value, list) else value
            if sheet_name is None:
                if exists(filename):
                    c=load_workbook(filename, read_only=True)
                    try:
                        sheet_name=c.sheetnames
                    finally:
                        c.close()
                else:
                    sheet_name=[f'Sheet{i}' for i in range(1, len(value)+1)]
            else:
                sheet_name=[sheet_name] if not isinstance(sheet_name, list) else sheet_name
            if len(value)==len(sheet_name):
                ex={'mode': 'a', 'if_sheet_exists': 'replace'} if exists(filename) else {'mode': 'w'}
                with ExcelWriter(filename, engine='openpyxl', **ex) as writer:
                    for i, j in zip(value, sheet_name):
                        i.to_excel(writer, sheet_name=j, index=False, **kwargs)
                        worksheet=writer.sheets[j]
                        header_font=Font(name=head_font, size=head_size, bold=True, color=colors[head_font_color])
                        header_fill=PatternFill(start_color=colors[head_cell_color], 
                                                end_color=colors[head_cell_color], fill_type='solid')
                        data_font=Font(name=font, size=size, color=colors[font_color])
                        data_fill=PatternFill(start_color=colors[cell_color], 
                                              end_color=colors[cell_color], fill_type='solid')
                        thin_side=Side(border_style='thin', color=colors[border_color])
                        border=Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
                        center_alignment=Alignment(horizontal='center', vertical='center')
                        for col_idx in range(1, len(i.columns)+1):
                            cell=worksheet.cell(row=1, column=col_idx)
                            cell.font=header_font
                            cell.fill=header_fill
                            cell.alignment=center_alignment
                            cell.border=border
                        for row in range(2, len(i)+2):
                            for col in range(1, len(i.columns)+1):
                                cell=worksheet.cell(row=row, column=col)
                                cell.font=data_font
                                cell.fill=data_fill
                                cell.border=border
                                col_name=i.columns[col-1]
                                value_type=i[col_name].dtype
                                if str(value_type) in type_formats:
                                    config=type_formats[str(value_type)]
                                elif str(value_type)=='datetime64[ns]':
                                    valid_series=i[col_name].dropna()
                                    first_value=valid_series[0] if not valid_series.empty else None
                                    if first_value is not None:
                                        date_list=[str(i.date()) for i in valid_series]
                                        time_list=[str(i.time()) for i in valid_series]
                                        if all(i==time_list[0] for i in time_list):
                                            type_formats['datetime64[ns]']=date_format
                                        elif all(i==date_list[0] for i in date_list):
                                            type_formats['datetime64[ns]']=time_format
                                        else:
                                            type_formats['datetime64[ns]']=f'{date_format} {time_format}'
                                    else:
                                        type_formats['datetime64[ns]']='General'
                                    config=type_formats['datetime64[ns]']
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

pyread_parameters=[i for i in signature(pyread).parameters]
pyrewrite_parameters=[i for i in signature(pyrewrite).parameters]
excelrewrite_parameters=[i for i in signature(DataFrame.to_excel).parameters]+pyrewrite_parameters
excelrewrite_parameters.remove('kwargs')

def super_round(value, num=0):
    if '.' not in str(value):
        value=float(f'{value}.0')
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

def sqlread(query, db_name, *, db_user=None, db_password=None, db_host='localhost', 
            db_port=5432, db_type='postgres', **kwargs):
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    result=read_sql(query, con=engine, **kwargs)
    return result

def sqlrewrite(table_name, new_value, db_name, *, db_user=None, db_password=None, 
               db_host='localhost', db_port=5432, db_type='postgres', chunksize=50000, **kwargs):
    kwargs.pop('if_exists', None)
    kwargs.pop('method', None)
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    for n, i in enumerate(range(0, len(new_value), chunksize)):
        chunk=new_value.iloc[i:i+chunksize]
        mode="replace" if n==0 else "append"
        chunk.to_sql(table_name, con=engine, if_exists=mode, index=False, method='multi', **kwargs)

sqlread_parameters=[i for i in signature(sqlread).parameters]
sqlrewrite_parameters=[i for i in signature(sqlrewrite).parameters]

def sqladd(table_name, new_value, db_name, *, db_user=None, db_password=None, 
           db_host='localhost', db_port=5432, db_type='postgres', chunksize=50000, **kwargs):
    kwargs.pop('if_exists', None)
    kwargs.pop('method', None)
    engine=make_sqlengine(db_name, db_user, db_password, db_host, db_port, db_type)
    for i in range(0, len(new_value), chunksize):
        chunk=new_value.iloc[i:i+chunksize]
        chunk.to_sql(table_name, con=engine, if_exists="append", index=False, method='multi', **kwargs)

def transform_from_sql(filepath, query, db_name, **kwargs):
    match filepath:
        case filepath if filepath.endswith('.csv'):
            from_sql_parameters=[i for i in signature(DataFrame.to_csv).parameters]
        case filepath if filepath.endswith('.parquet'):
            from_sql_parameters=[i for i in signature(DataFrame.to_parquet).parameters]
        case filepath if filepath.endswith('.xlsx'):
            from_sql_parameters=[i for i in signature(DataFrame.to_excel).parameters]+pyrewrite_parameters
        case _:
            raise ValueError('Unsupported file!!!')
    k1={i: j for i, j in kwargs.items() if i in sqlread_parameters}
    result=sqlread(query, db_name, **k1)
    k2={i: j for i, j in kwargs.items() if i in from_sql_parameters}
    pyrewrite(filepath, result, **k2)

def transform_to_sql(filepath, table_name, db_name, **kwargs):
    match filepath:
        case filepath if filepath.endswith('.csv'):
            to_sql_parameters=[i for i in signature(read_csv).parameters]
        case filepath if filepath.endswith('.parquet'):
            to_sql_parameters=[i for i in signature(read_parquet).parameters]
        case filepath if filepath.endswith('.xlsx'):
            to_sql_parameters=[i for i in signature(read_excel).parameters]+pyread_parameters
        case _:
            raise ValueError('Unsupported file!!!')
    k1={i: j for i, j in kwargs.items() if i in to_sql_parameters}
    result=pyread(filepath, **k1)
    k2={i: j for i, j in kwargs.items() if i in sqlrewrite_parameters}
    sqlrewrite(table_name, result, db_name, **k2)

def take_month(value):
    if value in ('january', 'jan', 'январь', 'января', 'янв', '01', '1'):
        return [1, 31]
    elif value in ('february', 'feb', 'февраль', 'февраля', 'фев', '02', '2'):
        return [2, 28]
    elif value in ('march', 'mar', 'март', 'марта', 'мар', '03', '3'):
        return [3, 31]
    elif value in ('april', 'apr', 'апрель', 'апреля', 'апр', '04', '4'):
        return [4, 30]
    elif value in ('may', 'май', 'мая', '05', '5'):
        return [5, 31]
    elif value in ('june', 'jun', 'июнь', 'июня', 'июн', '06', '6'):
        return [6, 30]
    elif value in ('july', 'jul', 'июль', 'июля', 'июл', '07', '7'):
        return [7, 31]
    elif value in ('august', 'aug', 'август', 'августа', 'авг', '08', '8'):
        return [8, 31]
    elif value in ('september', 'sep', 'сентябрь', 'сентября', 'сен', '09', '9'):
        return [9, 30]
    elif value in ('october', 'oct', 'октябрь', 'октября', 'окт', '10'):
        return [10, 31]
    elif value in ('november', 'nov', 'ноябрь', 'ноября', 'ноя', '11'):
        return [11, 30]
    elif value in ('december', 'dec', 'декабрь', 'декабря', 'дек', '12'):
        return [12, 31]
    else:
        raise ValueError('The entered month does not exist!!!')

def take_weekday(value, start_zero, start_sunday):
    numweek_list=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                  '01', '02', '03', '04', '05', '06', '07', '08', '09']
    if value.startswith(('monday', 'mon', 'mo', 'понедельник', 'пон', 'пн', '01', '1')):
        result=1
    elif value.startswith(('tuesday', 'tue', 'tu', 'вторник', 'вто', 'вт', '02', '2')):
        result=2
    elif value.startswith(('wednesday', 'wed', 'we', 'среда', 'сре', 'ср', '03', '3')):
        result=3
    elif value.startswith(('thursday', 'thu', 'th', 'четверг', 'чет', 'чт', '04', '4')):
        result=4
    elif value.startswith(('friday', 'fri', 'fr', 'пятница', 'пят', 'пт', '05', '5')):
        result=5
    elif value.startswith(('saturday', 'sat', 'sa', 'суббота', 'суб', 'сб', '06', '6')):
        result=6
    elif value.startswith(('sunday', 'sun', 'su', 'воскресенье', 'вос', 'вс', '07', '7')):
        result=7
    else:
        raise ValueError('The entered day of the week does not exist!!!')
    if start_zero==True and value in numweek_list:
        result+=1
    if start_sunday==True:
        result-=1
        if result==0:
            result=7
    return result

def distributor(s):
    s=[i for i in s if i!=' ']
    result=[]
    elem=[]
    isnum=True
    for i in s:
        if i.isdigit() and isnum==True:
            elem.append(i)
        elif (i.isalpha() or i==',') and isnum==False:
            elem.append(i)
        else:
            ready_elem=''.join(elem)
            if ready_elem.endswith('and'):
                ready_elem=ready_elem[:-3]
            elif ready_elem.endswith(',') or ready_elem.endswith('и'):
                ready_elem=ready_elem[:-1]
            result.append(ready_elem)
            elem=[i]
            isnum=not isnum
    result.append(''.join(elem))
    result=[i.strip() for i in result if i!='']
    return result

def work_timezone1(value, to_tz, from_tz):
    if to_tz in timezones:
        if from_tz is None:
            from_tz=datetime.now().astimezone().tzinfo
        else:
            from_tz=timezones[from_tz.lower()]
        to_tz=timezones[to_tz.lower()]
        value=value.tz_localize(from_tz).tz_convert(to_tz)
    elif from_tz in timezones:
        from_tz=timezones[from_tz.lower()]
        value=value.tz_localize(from_tz)
    return value

def work_timezone2(value, keyword, to_tz, from_tz):
    if to_tz not in timezones and from_tz not in timezones:
        return value.strftime('%X') if keyword=='time' else value.strftime('%Y-%m-%d %X')
    value=value.strftime('%X %z') if keyword=='time' else value.strftime('%Y-%m-%d %X %z')
    value=list(value)
    value.insert(-2, ':')
    value=''.join(value)
    return value.strip()

dt_list={'yesterday', 'the day before yesterday', 'tomorrow', 'the day after tomorrow', 'today', 'now', 'ago', 
         'in', 'half an hour ago', 'in half an hour', 'an hour and a half ago', 'in an hour and a half', 'next',
         'last', 'this', 'вчера', 'позавчера', 'завтра', 'послезавтра', 'сегодня', 'сейчас', 'назад', 'через',
         'полчаса назад', 'через полчаса', 'полтора часа назад', 'через полтора часа', 'следующ', 'прошл',
         'предыдущ', 'эт'}

def relative_datetime(value, keyword, *, current_date='now', current_time='now', current_datetime='now', 
             from_tz=None, to_tz=None):
    value=value.lower()
    if keyword=='date':
        current=Timestamp(current_date)
    elif keyword=='time':
        current=work_timezone1(Timestamp(current_time), to_tz, from_tz)
    else:
        current=work_timezone1(Timestamp(current_datetime), to_tz, from_tz)
    if value in ('yesterday', 'вчера'):
        result=current-DateOffset(days=1)
    elif value in ('the day before yesterday', 'позавчера'):
        result=current-DateOffset(days=2)
    elif value in ('tomorrow', 'завтра'):
        result=current+DateOffset(days=1)
    elif value in ('the day after tomorrow', 'послезавтра'):
        result=current+DateOffset(days=2)
    elif value in ('today', 'now', 'сегодня', 'сейчас'):
        result=current
    elif value in ('half an hour ago', 'полчаса назад'):
        result=current-DateOffset(minutes=30)
    elif value in ('an hour and a half ago', 'полтора часа назад'):
        result=current-DateOffset(minutes=90)
    elif value in ('in half an hour', 'через полчаса'):
        result=current+DateOffset(minutes=30)
    elif value in ('in an hour and a half', 'через полтора часа'):
        result=current+DateOffset(minutes=90)
    else:
        value=value.split()
        value=[i for i in value if i not in {'в', 'на', 'к', 'со'}]
        if value[0].startswith(('next', 'следующ')):
            if value[-1].startswith(('year', 'год')):
                result=current+DateOffset(years=1)
            elif value[-1].startswith(('month', 'месяц')):
                result=current+DateOffset(months=1)
            elif value[-1].startswith(('week', 'недел')):
                result=current+DateOffset(weeks=1)
            else:
                current_day=current.dayofweek+1
                next_day=take_weekday(value[-1], False, False)
                result=current+DateOffset(days=7+(next_day-current_day))
        elif value[0].startswith(('last', 'прошл', 'предыдущ')):
            if value[-1].startswith(('year', 'год')):
                result=current-DateOffset(years=1)
            elif value[-1].startswith(('month', 'месяц')):
                result=current-DateOffset(months=1)
            elif value[-1].startswith(('week', 'недел')):
                result=current-DateOffset(weeks=1)
            else:
                current_day=current.dayofweek+1
                next_day=take_weekday(value[-1], False, False)
                result=current-DateOffset(days=7-(next_day-current_day))
        elif value[0].startswith(('this', 'эт')):
            if value[-1].startswith(('year', 'month', 'week', 'год', 'месяц', 'недел')):
                result=current
            else:
                current_day=current.dayofweek+1
                next_day=take_weekday(value[-1], False, False)
                result=current-DateOffset(days=current_day-next_day)
        else:
            if value[-1] in ('ago', 'назад'):
                if value[0] in ('a', 'an'):
                    value[0]='1'
                elif len(value)==2:
                    value.insert(0, '1')
                word=''.join(value[:-1])
            else:
                if value[1] in ('a', 'an'):
                    value[1]='1'
                elif len(value)==2:
                    value.insert(1, '1')
                word=''.join(value[1:])
            years, weeks, months, days, hours, minutes, seconds=0, 0, 0, 0, 0, 0, 0
            distrub_list=distributor(word)
            for i in range(0, len(distrub_list), 2):
                if any(x==distrub_list[i+1] for x in ['day', 'days', 'день', 'дня', 'дней']):
                    days+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['week', 'weeks', 'неделю', 'недель', 'недели']):
                    weeks+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['month', 'months', 'месяц', 'месяца', 'месяцев']):
                    months+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['year', 'years', 'год', 'года', 'лет']):
                    years+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['h', 'hour', 'hours', 'ч', 'час', 'часа', 'часов']):
                    hours+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['m', 'min', 'minute', 'minutes', 'м', 'мин', 'минут', 'минуту']):
                    minutes+=int(distrub_list[i])
                if any(x==distrub_list[i+1] for x in ['s', 'sec', 'second', 'seconds', 'с', 'сек', 'секунд', 'секунду']):
                    seconds+=int(distrub_list[i])
            offset=DateOffset(years=years, weeks=weeks, months=months, days=days, 
                          hours=hours, minutes=minutes, seconds=seconds)
            if value[-1] in ('ago', 'назад'):
                result=current-offset
            elif value[0] in ('in', 'через'):
                result=current+offset
    if keyword=='date':
        return result.strftime('%Y-%m-%d')
    return work_timezone2(result, keyword, to_tz, from_tz)

def make_date(value, *, order='ymd', current_date='now', century=21, start_sunday=False, start_zero=False):
    if isinstance(value, str):
        keyword='date'
        value=value.lower().strip()
        if any(i in value for i in dt_list):
            return relative_datetime(value, keyword, current_date=current_date)
        lst=re.split(r'[-/.,: ]', value)
        lst=[i.strip() for i in lst if i!='']
    else:
        lst=value
    lst=lst[:len(order)]
    if 'y' not in order:
        current_year=Timestamp(current_date).year
        lst.append(str(current_year))
        year_idx=2
    else:
        year_idx=order.index('y')
    if len(lst[year_idx])==2:
        lst[year_idx]=f'{str(century-1)}{lst[year_idx]}'
    elif len(lst[year_idx])<2:
        raise ValueError('The year should not be less than 100!!!')
    if 'n' in order and 'w' in order:
        numweek_idx=order.index('n')
        weekday_idx=order.index('w')
        weekday_value=take_weekday(lst[weekday_idx], start_zero, start_sunday)
        if lst[numweek_idx].startswith('w'):
            lst[numweek_idx]=lst[numweek_idx][1:]
        first_day_year=str(Timestamp(lst[year_idx]).dayofweek+1)
        if (int(lst[year_idx])%4==0 and first_day_year in ('3', '4')) or first_day_year=='4':
            max_numweek=53
        else:
            max_numweek=52
        if 0<int(lst[numweek_idx])<=max_numweek:
            result=f'{lst[year_idx]}-W{lst[numweek_idx]}-{weekday_value}'
            return str(to_datetime(result, format='%G-W%V-%u').date())
        raise ValueError('The week number must not exceed the maximum number of the specified year!!!')
    else:
        month_idx=order.index('m')
        day_idx=order.index('d')
        month_values=take_month(lst[month_idx].lower())
        if int(lst[year_idx])%4==0 and month_values[0]==2:
            month_values[1]+=1
        lst[month_idx]=month_values[0]
        if 0<int(lst[day_idx])<=month_values[1]:
            return f'{lst[year_idx]}-{str(lst[month_idx]).zfill(2)}-{str(lst[day_idx]).zfill(2)}'
        raise ValueError('A month cannot be more than 12!!!')
    
def make_time(value, *, order='HMS', current_time='now', from_tz=None, to_tz=None):
    keyword='time'
    if isinstance(value, str):
        value=value.lower()
        if any(i in value for i in dt_list):
            return relative_datetime(value, keyword, current_time=current_time, from_tz=from_tz, to_tz=to_tz)
        pattern=r'\s*(?<![a-zA-Z])(?:a\.m|p\.m|am|pm)\.?(?![a-zA-Z])\s*|\s*[-/.,: ]\s*'
        lst=re.split(pattern, value)
        lst=[i.strip() for i in lst if i!='']
    else:
        lst=value.copy()
        lst=[i.strip() for i in lst if i.strip() not in ['am', 'pm', 'a.m', 'p.m']]
    order=order[:len(lst)]
    if not any(i in {'H', 'M', 'S'} for i in order):
        raise ValueError('Error!!!')
    if 'H' not in order:
        hour_value='00'
    else:
        hour_idx=order.index('H')
        if 'pm' in value or 'p.m.' in value:
            if lst[hour_idx]=='12':
                lst[hour_idx]='12'
            elif 0<=int(lst[hour_idx])<12:
                lst[hour_idx]=str(int(lst[hour_idx].strip())+12)
        if 'am' in value or 'a.m.' in value:
            if lst[hour_idx]=='12':
                lst[hour_idx]='00'
            elif 12<int(lst[hour_idx])<=24:
                lst[hour_idx]=str(int(lst[hour_idx].strip())-12)
        if 0<=int(lst[hour_idx])<24:
            hour_value=lst[hour_idx]
        elif int(lst[hour_idx])==24:
            hour_value='00'
        else:
            raise ValueError('Hours cannot be greater than 24 and less than 0!!!')
    if 'M' not in order:
        minute_value='00'
    else:
        minute_idx=order.index('M')
        if 0<=int(lst[minute_idx])<60:
            minute_value=lst[minute_idx]
        elif int(lst[minute_idx])==60:
            minute_value='00'
        else:
            raise ValueError('Minutes cannot be more than 60 and less than 0!!!')
    if 'S' not in order:
        second_value='00'
    else:
        second_idx=order.index('S')
        if 0<=int(lst[second_idx])<60:
            second_value=lst[second_idx]
        elif int(lst[second_idx])==60:
            second_value='00'
        else:
            raise ValueError('Seconds cannot be greater than 60 and less than 0!!!')
    result=f'{hour_value.zfill(2)}:{minute_value.zfill(2)}:{second_value.zfill(2)}'
    result=work_timezone1(Timestamp(result), to_tz, from_tz)
    return work_timezone2(result, keyword, to_tz, from_tz)

def make_datetime(value, *, order_date='ymd', order_time='HMS', century=21, isfirsttime=False,
                  start_sunday=False, start_zero=False, current_datetime='now', from_tz=None, to_tz=None):
    value=value.lower().strip()
    if any(i in value for i in dt_list):
        return relative_datetime(value, 'datetime', current_datetime=current_datetime, from_tz=from_tz, to_tz=to_tz)
    pattern1=r'\s*(?<![a-zA-Z])(?:a\.m|p\.m|am|pm)\.?(?![a-zA-Z])\s*|\s*[-/.,: ]\s*'
    pattern2=r'\s*(?<![a-zA-Z])(?:a\.m|p\.m|am|pm)\.?(?![a-zA-Z])'
    lst=re.split(pattern1, value)
    lst=[i.strip() for i in lst if i!='']
    special_symbol=re.findall(pattern2, value)[:1]
    special_symbol=''.join(special_symbol).strip()
    part1, part2='', ''
    if isfirsttime is False:
        part1=make_date(lst[:len(order_date)], order=order_date, century=century, start_sunday=start_sunday, start_zero=start_zero)
        if lst[len(order_date):]!=[]:
            part2=make_time(lst[len(order_date):]+[special_symbol], order=order_time)
    else:
        if lst[len(order_time):]!=[]:
            part1=make_date(lst[len(order_time):], order=order_date, century=century, start_sunday=start_sunday, start_zero=start_zero)
        part2=make_time(lst[:len(order_time)]+[special_symbol], order=order_time)
    result=f'{part1} {part2}'.strip()
    result=work_timezone1(Timestamp(result), to_tz, from_tz)
    return work_timezone2(result, 'datetime', to_tz, from_tz)
