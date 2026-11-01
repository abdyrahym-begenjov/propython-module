# propython-module
## English
## ProPython: Utilities of Files, Databases, and Math 🐍
ProPython is a simple and helpful Python library. It helps you work with different files, connect to databases, and do math operations without writing long code. It is great for automating your daily programming tasks.
> **Note:** This library requires Python 3.10+ because it uses the modern match-case feature.

## Key Features
* **All-in-One File Tools:** Read, write, and append `.txt`, `.json`, `.pickle`, `.csv`, `.parquet`, and `.xlsx` (Excel) files easily.
* **Smart Excel Styles:** Automatically makes Excel columns wide enough for your data and adds nice colors and fonts.
* **Simple SQL Database Tools:** Connect to PostgreSQL, MySQL, or SQLite, and move data between files and databases quickly.
* **Better Math:** Easy functions for math rounding, finding roots, and solving equations.

## API Reference & Function Capabilities

### `pyread(filename, *, encoding='utf-8', as_list=False, **kwargs)`
* **Description:** Reads data from a file. It automatically knows the format by looking at the file extension.
* **Capabilities:**
  * Automatically handles 6 formats: `.txt`, `.json`, `.pickle`, `.csv`, `.parquet`, and `.xlsx`.
  * If you read a `.txt` file with `as_list=True`, it automatically splits the text into a clean list of lines.
  * If you read an Excel file with only one sheet, it automatically extracts it as a single DataFrame instead of a dictionary.
  * Passes extra options (`**kwargs`) directly to internal readers like `pandas.read_csv` or `pandas.read_excel`.

### `pyrewrite(filename, value, *, encoding='utf-8', sheet_name=None, ...)`
* **Description:** Clears the target file and writes completely new data into it.
* **Capabilities:**
  * Supports writing strings and lists to `.txt`, dictionaries to `.json`/`.pickle`, and dataframes to `.csv`/`.parquet`/`.xlsx`.
  * For Excel (`.xlsx`), it automatically designs your table: adds bold headers, custom colors, fonts, and clean thin borders.
  * Automatically auto-fits the Excel column widths based on the longest text in each column.
  * Automatically sets cell data formats in Excel (detects categories, integers, floats, dates, and times).

### `pyadd(filename, value, *, encoding='utf-8', sheet_name=None, **kwargs)`
* **Description:** Adds new data to the end of an existing file without deleting the old content.
* **Capabilities:**
  * For `.txt` files, it appends new text lines directly to the end.
  * For `.json` and `.pickle`, it reads the old data first, merges it safely with the new data using `pyupdate`, and overwrites the file.
  * For `.csv` and `.xlsx` dataframes, it automatically separates and filters arguments for reading and writing so your code does not crash.

### `pyupdate(d1, d2)`
* **Description:** A helper function that merges two dictionaries recursively.
* **Capabilities:**
  * If the same key exists in both dictionaries, it combines their values into a list or extends them instead of overwriting.
  * Safely merges Python lists, tuples, sets, frozensets, and deques.
  * Supports deep nested dictionary updates at any level.

### `make_sqlengine(db_name, db_user=None, db_password=None, db_host='localhost', db_port=5432, db_type='postgres')`
* **Description:** Creates a connection object (engine) for your database using SQLAlchemy.
* **Capabilities:**
  * Supports 3 popular database systems: PostgreSQL/Postgres, MySQL, and SQLite.
  * Automatically builds the correct connection string URL so you do not have to memorize syntax.

### `sqlread(query, db_name, **kwargs)`
* **Description:** Runs an SQL query and returns the result table as a `pandas.DataFrame`.
* **Capabilities:**
  * Automatically opens and closes the database connection for you.
  * Accepts all configuration parameters from `make_sqlengine`.

### `sqlrewrite(table_name, new_value, db_name, ..., chunksize=50000, **kwargs)`
* **Description:** Replaces an old table in the database with a new DataFrame.
* **Capabilities:**
  * Uploads data in small parts (chunks) to protect your computer's RAM.
  * Uses the fast multi insert method to send data to the database quickly.

### `sqladd(table_name, new_value, db_name, ..., chunksize=50000, **kwargs)`
* **Description:** Appends new rows from a DataFrame to the end of an existing database table.
* **Capabilities:**
  * Never deletes old database data; it only appends.
  * Uses the same fast chunk-by-chunk processing system as `sqlrewrite`.

### `transform_from_sql(filepath, query, db_name, **kwargs)`
* **Description:** Takes data from a database query and saves it directly into a file.
* **Capabilities:**
  * Exports database tables to `.csv`, `.parquet`, or styled `.xlsx` with one line of code.
  * Automatically filters valid writing parameters depending on the chosen file extension.

### `transform_to_sql(filepath, table_name, db_name, **kwargs)`
* **Description:** Reads data from a file and uploads it directly into a database table.
* **Capabilities:**
  * Connects `pyread` and `sqlrewrite` together automatically.
  * Detects and links file reading parameters with database writing rules.

### `onelist(lst)`
* **Description:** Takes a complex nested collection and flattens it into one simple, single list.
* **Capabilities:**
  * Uses recursion to unpack structures of any depth.
  * Unpacks list, tuple, set, frozenset, and deque all at once.

### `super_round(value, num=0)`
* **Description:** Rounds numbers using standard symmetric school math rules (where 0.5 always rounds up away from zero).
* **Capabilities:**
  * Bypasses Python's built-in "banker's rounding" (round-to-even) for predictable math results.
  * Uses optimized string slices and list reversals for reliable parsing.

### `root(number, base=2, precision=2)`
* **Description:** Finds the root of a number with a specific degree and rounds the result.
* **Capabilities:**
  * Supports square roots, cube roots, and higher degrees.
  * Automatically blocks impossible operations (like even roots of negative numbers or degrees less than 2).
  * Cleans the output using `super_round`.

### `quadratic_equation(a, b=0, c=0)`
* **Description:** Solves standard quadratic equations (ax² + bx + c = 0).
* **Capabilities:**
  * Safely processes linear cases if a = 0 or b = 0.
  * Returns `None` if there are no real roots, one number if there is one root, or a tuple `(x1, x2)` if there are two roots.


## Русский
## Propython: утилиты файлов, баз данных и математики 🐍

ProPython — это простая и полезная библиотека для Python. Она помогает работать с различными файлами, подключаться к базам данных и выполнять математические операции без написания длинного кода. Отлично подходит для автоматизации ваших повседневных задач программирования.

> **Примечание:** Для работы библиотеки требуется Python 3.10+, так как в ней используется современный механизм сопоставления шаблонов (match-case).

## Основные возможности

* **Универсальные файлы:** Легкое чтение, запись и добавление данных в `.txt`, `.json`, `.pickle`, `.csv`, `.parquet` и `.xlsx` (Excel).
* **Красивый Excel:** Автоматически подбирает ширину колонок и добавляет красивые шрифты и цвета в таблицы.
* **Простая работа с SQL:** Подключение к PostgreSQL, MySQL или SQLite и быстрый перенос данных между файлами и базой.
* **Полезная математика:** Удобные функции для округления чисел, поиска корней и решения уравнений.

---

## Описание функций и их возможностей

### `pyread(filename, *, encoding='utf-8', as_list=False, **kwargs)`

* **Описание:** Читает данные из файла. Автоматически определяет нужный формат по его расширению.
* **Возможности:**
  * Работает с 6 популярными форматами: `.txt`, `.json`, `.pickle`, `.csv`, `.parquet` и `.xlsx`.
  * Если читать `.txt` с параметром `as_list=True`, функция автоматически разобьет текст на список строк.
  * При чтении Excel с одним листом автоматически извлекает его как чистый DataFrame, а не словарь.
  * Пробрасывает дополнительные параметры (`**kwargs`) во внутренние методы `pandas`.

### `pyrewrite(filename, value, *, encoding='utf-8', sheet_name=None, ...)`

* **Описание:** Полностью удаляет старое содержимое файла и записывает в него новые данные.
* **Возможности:**
  * Поддерживает запись строк/списков в `.txt`, словарей в `.json`/`.pickle` и таблиц в `.csv`/`.parquet`/`.xlsx`.
  * При сохранении в Excel автоматически наводит красоту: делает жирные заголовки, рамки ячеек, настраивает цвета и шрифты.
  * Автоматически растягивает ширину колонок Excel под самый длинный текст в столбце.
  * Сама выставляет форматы данных для ячеек Excel (текст, целые числа, дроби, даты и время).

### `pyadd(filename, value, *, encoding='utf-8', sheet_name=None, **kwargs)`

* **Описание:** Добавляет новые данные в конец существующего файла без удаления старой информации.
* **Возможности:**
  * В `.txt` файлах просто дописывает новые строки в самый конец.
  * В `.json` и `.pickle` сначала считывает старые данные, безопасно объединяет их с новыми через `pyupdate` и перезаписывает файл.
  * Для таблиц `.csv` и `.xlsx` автоматически разделяет и фильтрует аргументы чтения и записи, предотвращая ошибки.

### `pyupdate(d1, d2)`

* **Описание:** Помощник для рекурсивного (глубокого) объединения двух словарей.
* **Возможности:**
  * Если ключи в словарях совпадают, функция не перезаписывает данные, а объединяет их элементы в один общий список.
  * Безопасно работает со структурами `list`, `tuple`, `set`, `frozenset` и `deque`.
  * Поддерживает слияние вложенных словарей на любой глубине.

### `make_sqlengine(db_name, db_user=None, db_password=None, db_host='localhost', db_port=5432, db_type='postgres')`

* **Описание:** Создает объект подключения (engine) к базе данных через SQLAlchemy.
* **Возможности:**
  * Поддерживает 3 популярные СУБД: PostgreSQL/Postgres, MySQL и SQLite.
  * Сама собирает правильную строку подключения, избавляя вас от необходимости писать её вручную.

### `sqlread(query, db_name, **kwargs)`

* **Описание:** Выполняет SQL-запрос и возвращает полученную таблицу в виде `pandas.DataFrame`.
* **Возможности:**
  * Сама открывает и закрывает соединение с базой данных «под капотом».
  * Принимает все те же настройки подключения, что и `make_sqlengine`.

### `sqlrewrite(table_name, new_value, db_name, ..., chunksize=50000, **kwargs)`

* **Описание:** Полностью удаляет старую таблицу в базе данных и записывает на её место новый DataFrame.
* **Возможности:**
  * Загружает данные небольшими частями (chunks), что защищает оперативную память компьютера от перегрузки.
  * Использует быстрый метод `multi` для ускоренной пакетной вставки строк в БД.

### `sqladd(table_name, new_value, db_name, ..., chunksize=50000, **kwargs)`

* **Description:** Добавляет новые строки из DataFrame в конец существующей таблицы в базе данных.
* **Возможности:**
  * Никогда не удаляет старые данные в БД, только дописывает новые.
  * Использует ту же производительную систему разбивки на чанки, что и `sqlrewrite`.

### `transform_from_sql(filepath, query, db_name, **kwargs)`

* **Описание:** Берет данные из базы данных по SQL-запросу и сохраняет их напрямую в файл.
* **Возможности:**
  * Экспортирует таблицы из БД в файлы `.csv`, `.parquet` или стилизованный `.xlsx` одной строчкой кода.
  * Сама подбирает корректные параметры записи в зависимости от выбранного расширения файла.

### `transform_to_sql(filepath, table_name, db_name, **kwargs)`

* **Описание:** Читает данные из файла и сразу загружает их в таблицу базы данных.
* **Возможности:**
  * Автоматически объединяет логику функций `pyread` и `sqlrewrite`.
  * Самостоятельно связывает параметры чтения файлов с правилами записи в SQL.

### `onelist(lst)`

* **Описание:** Принимает сложную вложенную коллекцию и превращает её в один плоский простой список.
* **Возможности:**
  * Использует рекурсию, позволяя разбирать структуры любой глубины вложенности.
  * Успешно извлекает элементы из `list`, `tuple`, `set`, `frozenset` и `deque`.

### `super_round(value, num=0)`

* **Описание:** Округляет числа по стандартным школьным правилам математики (где 0.5 всегда округляется в большую сторону от нуля).
* **Возможности:**
  * Позволяет обойти встроенное в Python «банковское округление» (к ближайшему четному) для получения предсказуемых результатов.
  * Использует строковые срезы и развороты списков для точного разбора долей числа.

### `root(number, base=2, precision=2)`

* **Описание:** Находит корень числа любой степени и округляет итоговый результат.
* **Возможности:**
  * Считает квадратные, кубические и любые корни высших степеней.
  * Автоматически блокирует невозможные операции (например, извлечение четного корня из отрицательного числа или степень корня меньше 2).
  * Финально обрабатывает результат через `super_round`.

### `quadratic_equation(a, b=0, c=0)`

* **Описание:** Решает стандартные квадратные уравнения (ax² + bx + c = 0).
* **Возможности:**
  * Безопасно обрабатывает линейные случаи, если коэффициенты `a` или `b` равны нулю.
  * Возвращает `None`, если вещественных корней нет, одно число при единственном корне или кортеж `(x1, x2)`, если корней два.
