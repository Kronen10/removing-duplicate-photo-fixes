import os
import hashlib
import shutil
import datetime

#Версия скрипта для работы с дубликатами jpg + json, созданием бекапа файлов и файла логов

def copy_directory(source):
    """Создает копию директории с текущей датой и временем."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_directory = f"{os.path.basename(source)}_backup_{timestamp}"
    
    shutil.copytree(source, backup_directory)
    print(f'Создана резервная копия директории: {backup_directory}')

def find_duplicate_files(directory):
    # Словарь для хранения хешей и путей к файлам
    hashes = {}
    duplicates = {}

    # Проходим по всем файлам в директории
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # Полный путь к файлу
            file_path = os.path.join(dirpath, filename)

            # Игнорируем файлы, которые не являются изображениями или JSON
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.json')):
                continue

            # Вычисляем хеш файла
            file_hash = hash_file(file_path)

            # Если хеш уже есть в словаре, добавляем путь к дубликатам
            if file_hash in hashes:
                if hashes[file_hash] in duplicates:
                    duplicates[hashes[file_hash]].append(file_path)
                else:
                    duplicates[hashes[file_hash]] = [hashes[file_hash], file_path]
                print(f'Найден дубликат: {file_path}')
            else:
                hashes[file_hash] = file_path

    return duplicates

def hash_file(file_path):
    #Возвращает хеш (SHA-1) файла (объект в двоичном формате)
    hasher = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def remove_duplicates(duplicates, log_file):
    #Удаляет дублирующиеся файлы и записывает информацию о них в лог-файл
    with open(log_file, 'w') as log:
        for original, duplicates_list in duplicates.items():
            for duplicate in duplicates_list[1:]:  # Пропускаем оригинал
                try:
                    os.remove(duplicate)
                    log.write(f'Удален дубликат: {duplicate} (оригинал: {duplicates_list[0]})\n')
                    print(f'Удален дубликат: {duplicate} (оригинал: {duplicates_list[0]})')
                except Exception as e:
                    log.write(f'Ошибка при удалении {duplicate}: {e}\n')

def main():
    directory = input("Введите путь к директории: ")
    duplicates = find_duplicate_files(directory)

    if duplicates:
        print(f'Найдено {sum(len(dup) - 1 for dup in duplicates.values())} дублирующихся файлов.')
        
        # Подтверждение на создание резервной копии и удаление
        confirm = input("Хотите создать резервную копию и удалить все дубликаты? (y/n): ")
        if confirm.lower() == 'y':
            copy_directory(directory)
            log_file = 'deleted_duplicates_log.txt'
            remove_duplicates(duplicates, log_file)
            print(f'Информация о удаленных дубликатах записана в файл: {log_file}')
        else:
            print('Удаление дубликатов отменено.')
    else:
        print('Дубликаты не найдены.')

if __name__ == "__main__":
    main()
