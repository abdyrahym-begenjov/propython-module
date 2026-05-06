# propython-module
# ProPython File Utility 🐍
# English
ProPython is a minimalist Python module for quickly writing and reading data in TXT, JSON, and PICKLE formats. It eliminates the need to write repetitive contextual open(...) code and automatically handles file extensions.
## Key Features
* General-Purpose Reader (pyread): Automatically detects the file format based on the extension and returns the processed data (a string, dictionary/list, or Python object).
* General-Purpose Writer (pywrite): Saves the passed data in the required format based on the file extension.
* Security: Basic exception handling is built in for cases where the file is not found or the extension is invalid.
* Requirements: Python 3.10+ (uses the match-case operator).

#Файловая утилита ProPython 🐍
#Русский
**ProPython** — это минималистичный Python-модуль для быстрой записи и чтения данных в форматах **TXT**, **JSON** и **PICKLE**. Он избавляет от написания повторяющегося контекстного кода with open(...) и автоматически обрабатывает расширения файлов.
## Основные возможности
 * **Универсальное чтение (pyread):** Автоматически определяет формат файла по расширению и возвращает обработанные данные (строку, словарь/список или объект Python).
 * **Универсальная запись (pywrite):** Сохраняет переданные данные в нужном формате, опираясь на расширение файла.
 * **Безопасность:** Встроена базовая обработка исключений для случаев, когда файл не найден или указано неверное расширение.
* **Требования:** Python 3.10+ (используется оператор match-case).
