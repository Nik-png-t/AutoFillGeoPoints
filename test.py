#main
import sys, os
from openpyxl import load_workbook
import time
from copy import copy
import json
import asyncio
from datetime import datetime, timezone, date
import re
# telegram
import python_socks
from telethon import TelegramClient, sync, utils, connection
import telethon
#crypto
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Pack:
    def __init__(self, name_dir=None, name_file=None, size_file=None, high=None, receiver_number=None):
        self.name = name_dir.split("-")[0] # [ГТСП, ОП, ТСП, ТСП-ОП]
        self.high = high
        self.name_dir = name_dir # полное название
        self.name_file = name_file # название файла .jps
        self.size_file = size_file
        self.receiver_number = self.receiver_number

class SafetyStorage:
    def __init__(self):
        if not os.path.exists('log.enc'):
            print("Файла log.bin нет, создаем...")
            password = self.any_way_answer("Новый пароль: ")
            api_id = self.any_way_answer("Новый API ID: ")
            api_hash = self.any_way_answer("Новый API HASH: ")
            is_proxy = bool(self.any_way_answer("Нужен прокси: "))
            if is_proxy:
                proxy_host = self.any_way_answer("Нужен прокси host: ")
                proxy_port = self.any_way_answer("Нужен прокси port: ")
                proxy_secret = self.any_way_answer("Нужен прокси secret: ")
            else:
                proxy_host = None
                proxy_port = None
                proxy_secret = None
            name = None
            path = None
            target_date = None
            self.data = {
                "password": password,
                "api_id": api_id,
                "api_hash": api_hash,
                "is_proxy": is_proxy,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "proxy_secret": proxy_secret,
                "name": name,
                "path": path
            }
            self.save_data()
            return
            
        with open('log.enc', 'rb') as file:
            self.data_crypted = file.read()
        
        password = input("Пароль: ")
        used_salt = self.data_crypted[:16]
        data_crypted = self.data_crypted[16:]
        
        try:
            data = self.decrypt_data(data_crypted, password, used_salt)
            self.data = json.loads(data)
            print(f"Успешно расшифровано")
            
        except Exception as e:
            raise ValueError(f"\nОшибка расшифровки! Неверный пароль или данные повреждены. {e}")

        self.question_print_data()
        self.question_change_data()
        self.save_data()

    def save_data(self):
        data = json.dumps(self.data, ensure_ascii=False, indent=4)
        with open('log.enc', 'wb') as f:
            encrypted_data, salt = self.encrypt_data(data, self.data['password'])
            f.write(salt+encrypted_data)
            
    def any_way_answer(self, text):
        a = None
        while not a:
            a = input(text)
        return a

    def not_any_way_answer(self, text, a_):
        a = input(text)
        if a:
            return a
        return a_

    def question_print_data(self):
        if input("Вывести данные: "):
            print(f"    Пароль: {self.data['password']}\n    API ID: {self.data['api_id']}\n    API HASH: {self.data['api_hash']}")
            print(f"    Нужен ли прокси: {self.data['is_proxy']}")
            if self.data['is_proxy']:
                print(f"    Прокси HOST: {self.data['proxy_host']}\n    Прокси PORT: {self.data['proxy_port']}\n Проки SECRET: {self.data['proxy_secret']}")
            
    
    def question_change_data(self):
        if input("Изменить что-то: "):
            self.data['password'] = self.not_any_way_answer("Новый пароль: ", self.data['password'])
            self.data['api_id'] = self.not_any_way_answer("Новый API ID: ", self.data['api_id'])
            self.data['api_hash'] = self.not_any_way_answer("Новый API HASH: ", self.data['api_hash'])
            is_proxy = input("Нужен прокси: ")
            if is_proxy == "no":
                self.data['is_proxy'] = False
            elif is_proxy == "yes" or self.data["is_proxy"]:
                self.data['is_proxy'] = True
                self.data['proxy_host'] = self.not_any_way_answer("Новый прокси host: ", self.data['proxy_host'])
                self.data['proxy_port'] = self.not_any_way_answer("Новый прокси port: ", self.data['proxy_port'])
                self.data['proxy_secret'] = self.not_any_way_answer("Новый прокси secret: ", self.data['proxy_secret'])
        today = date.today().strftime("%Y-%m-%d")
        self.data['date'] = self.not_any_way_answer(f"Дата ({today}): ", today)
        name = re.sub(r"\d{4}([_-]\d{2}){2}", self.data['date'], self.data['name'])
        path = re.sub(r"\d{4}([_-]\d{2}){2}", self.data['date'], self.data['path'])
        self.data['name'] = self.not_any_way_answer(f"Имя файла xml({name}): ", name)
        self.data['path'] = self.not_any_way_answer(f"Путь до директории({path}): ", path)
        
            
        
    def generate_key(self, password: str, salt: bytes) -> bytes:
        """Генерирует криптографический ключ на основе пароля и соли."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_000_000, 
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data: str, password: str) -> tuple[bytes, bytes]:
        """Шифрует данные по паролю. Возвращает (зашифрованные_данные, соль)."""
        salt = os.urandom(16) 
        key = self.generate_key(password, salt)
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data, salt

    def decrypt_data(self, encrypted_data: bytes, password: str, salt: bytes) -> str:
        """Расшифровывает данные, используя исходный пароль и соль."""
        key = self.generate_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()
    
        
class TelegramConnect:
    def __init__(self, storage):
        self.storage = storage
        self.packed = []
        if self.storage.data["is_proxy"]:
            
            mtproto = (self.storage.data["proxy_host"], int(self.storage.data["proxy_port"]), self.storage.data["proxy_secret"])
            mtproto_connection = connection.tcpmtproxy.ConnectionTcpMTProxyAbridged
            self.client = telethon.TelegramClient('session',api_id=self.storage.data["api_id"],api_hash=self.storage.data["api_hash"],proxy=mtproto,connection=mtproto_connection)

        else:
            self.client = TelegramClient('autofillgeo', self.storage.data["api_id"], self.storage.data["api_hash"])

        with self.client:
            self.client.loop.run_until_complete(self.start_client())
            self.client.loop.run_until_complete(self.find_message())

    async def start_client(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f'Привет, {me.first_name}! Соединение успешно установлено.')

        

    async def find_message(self):
        try:
            target_date = datetime.strptime(self.storage.data["date"], "%Y-%m-%d").date()
        except:
            raise ValueError("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
        
        start_of_day = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, datetime.max.time(), tzinfo=timezone.utc)

        os.makedirs(self.storage.data["path"], exist_ok=True)
        async for message in self.client.iter_messages('me', offset_date=end_of_day):
            if message.date < start_of_day:
                break
            text = message.text.split(" ")
            if text[-1].isdigit() and text[0].split("-")[0] in ["ТСП-ОП", "ОП", "ГТСП"] and message.photo:
                if text[-2].isdigit():
                    receiver_number = int(text[-1])
                    name_point = " ".join(text[:-2])
                    high_point = int(text[-2])
                else:
                    name_point = " ".join(text[:-1])
                    high_point = int(text[-1])
                    receiver_number = None
                print(f"Найдено имя: {name_point}, высота {high_point}, номер приемника {receiver_number}")
                full_path =  f"{self.storage.data['path']}\\{name_point}"
                os.makedirs(full_path, exist_ok=True)
                self.packed.append(Pack(name_dir=name_point, high=high_point, receiver_number=receiver_number))
                idx = 1
                async for msg in self.client.iter_messages('me', limit=60, min_id=message.id - 30, max_id=message.id + 30):
                    full_path_img = os.path.join(full_path, f"{idx}.jpg")
                    if msg.grouped_id == message.grouped_id:
                        if not os.path.isfile(full_path_img):
                            await self.client.download_media(msg, file=full_path_img)
                        idx += 1
                        await asyncio.sleep(0.5)
        
        
            

class AutoXML:

    def __init__(self):
        self.storage = SafetyStorage()
        self.tg = TelegramConnect(self.storage)
        folder_distribution_of_files(f"{'\\'.join(self.storage.data['path'].split('\\')[:-1])}\\Новая папка", self.storage.data["path"], self.tg.packed)
        self.source_path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])

    def search_into_directory(self, path):
        for dir_ in os.listdir(path):
            dir_path = f"{path}\\{dir_}"
            if os.path.isdir(dir_path):
                
                file_names = []
                for name in os.listdir(dir_path):
                    if name[-4:] == ".jps":
                        file_names.append(name[:-4])

                if len(file_names) != 1:
                    raise ValueError(f"Слишком много файлов .jps в одной папке {dir_}")
                is_ = False
                name_file = file_names[0]
                size_file = str(round(os.path.getsize(f"{dir_path}\\{file_names[0]}.jps") / 1024 / 1024, 1)).replace(",", ".")
                for pck in self.tg.packed:
                    if pck.name_dir == dir_:
                        pck.size_file = size_file
                        pck.name_file = name_file
                        is_ = True
                if not is_:
                    self.tg.packed.append(Pack(name_dir=dir_, name_file=name_file, size_file=size_file, high=None))



    def full_copy_paste(self, copy_target, paste_target):
        paste_target.value = copy_target.value
        paste_target.font = copy(copy_target.font)
        paste_target.fill = copy(copy_target.fill)
        paste_target.border = copy(copy_target.border)
        paste_target.alignment = copy(copy_target.alignment)
        paste_target.number_format = copy(copy_target.number_format)
        paste_target.protection = copy(copy_target.protection)

    def full_copy_paste_string(self, ws, copy_target_number, paste_target_number, length):
        for i in range(length):
            copy_ = ws.cell(row=copy_target_number, column=i+1)
            paste_ = ws.cell(row=paste_target_number, column=i+1)
            self.full_copy_paste(copy_, paste_)
        

    def create_XML(self, list_info):
        wb = load_workbook(f"{self.source_path}\\pattern.xlsx")
        ws = wb.active  
        ws.title = "Данные координирования"

        number_of_end_string = 5+len(list_info)
        
        self.full_copy_paste(ws["A5"], ws[f"A{number_of_end_string}"])
        self.full_copy_paste(ws["B5"], ws[f"B{number_of_end_string}"])
        ws.unmerge_cells("B5:I5") 
        ws.delete_rows(idx=5)
        ws.merge_cells(f"B{number_of_end_string-1}:I{number_of_end_string-1}")
        ws.row_dimensions[5].height = 15
        sorted_list_info = sorted(list_info, key=lambda x: x.name_dir)
        for i, info in enumerate(sorted_list_info):
            self.full_copy_paste_string(ws, 4, 4+i, 10)
            self.fill_string(ws, 4+i, info)
            

        wb.save(f"{self.storage.data['path']}\\{self.storage.data['name']}.xlsx")

    def fill_string(self, ws, number_string, string):
        ws[f'A{number_string}'] = string.name
        ws[f'B{number_string}'] = string.name_dir
        ws[f'H{number_string}'] = string.name_file
        ws[f'G{number_string}'] = string.high
        ws[f'I{number_string}'] = string.size_file
                        
    def run(self):
        input("Можно создать XML файл? ")
        self.search_into_directory(self.storage.data["path"])
        self.create_XML(self.tg.packed)

        
def folder_distribution_of_files(path_to_files, path_to_folders, list_info):
    input("Начать распределение файлов: ")
    jps_files = os.listdir(path_to_files)
    empty_folder = []
    folder_bases = []
    
    # отсеиваем только папки без .jps файла в них
    for folder in os.listdir(path_to_folders):
        full_path_to_folder = f"{path_to_folders}\\{folder}"
        if os.path.isdir(full_path_to_folder) and "jps" not in [file.split(".")[-1] for file in os.listdir(full_path_to_folder)]:
            if "ГТСП" == folder.split("-")[0] or "ГТСП" == folder.split(" ")[0]:
                print("Пустая папка ГТСП найдена")
                folder_bases.append(folder)
            else:
                empty_folder.append(folder)
                print(f"Пустая папка {folder}")
                
    # подсчитываем сколько файлов от каждого приемника
    count_of_type_jps_files = {}
    for file in jps_files:
        file_name = file.split("_")[0]
        if file_name in list(count_of_type_jps_files):
            count_of_type_jps_files[file_name].append(file)
        else:
            count_of_type_jps_files[file_name] = [file]
    
    
    # отсеиваем базу или базы
    if len(folder_bases):
        #folder_base = [ГТСП-2, ГТСП-3 Ульт-Ягун]
        #base_files = [purple, [23_purple.jps]), (white, [white.jps])]
        #list_info = [.name_dir=ГТСП-2, .receiver_number=12]
        base_files = {{file_name: files} for file_name, files in count_of_type_jps_files.items() if len(files) == 1}
        for info in list_info:
            if info.name_dir in folder_bases and info.receiver_number is not None:
                base_file_name = change_rec_num_to_file(info.receiver_number) # purple, white, black
                if base_file_name in base_files.keys():
                    base_file = base_files[base_file_name][0]
                else:
                    raise ValueError("Указаный {base_file_name} not in {base_files.keys()}")
                print(f"Найдена база {info.name_dir} = {base_file}")
                os.rename(f"{path_to_files}\\{base_file}", f"{path_to_folders}\\{info.name_dir}\\{base_file}")
                folder_bases.pop(info.name_dir)
                base_files.pop(base_file_name)
                count_of_type_jps_files.pop(base_file_name)
                
        if len(base_files) == 1:
            file_name = base_files.keys()[0]
            file = base_files[file_name][0]
            print(f"Найдена база {folder_bases[0]} = {file}")
            count_of_type_jps_files.pop(file_name)
            os.rename(f"{path_to_files}\\{file}", f"{path_to_folders}\\{folder_bases[0]}\\{file}")
        else:
            input("Не получилось переместить файлы. Сделайте самостоятельно")


    # распределяем помеченые файлы
    if
    # -> queue = [None, purple, purple, None, None, None]
    # распределяем остальные файлы
    file_names = list(count_of_type_jps_files.keys())
    if len(file_names) == 1:
        print("Применена одиночная сортировка")
        files = count_of_type_jps_files[file_names[0]]
        for pack_info in list_info:
            if pack_info.name_dir in empty_folder:
                if len(files):
                    print(files[0], pack_info.name_dir)
                    os.rename(f"{path_to_files}\\{files[0]}", f"{path_to_folders}\\{pack_info.name_dir}\\{files[0]}")
                    files.pop(0)
    elif len(file_names) == 2:
        
        type_ = input(f"Какой тип двойной сортировки выберите первый файл (1 вариант: {file_names[0]}, 2 вариант: {file_names[1]}): ")
        if not type_:
            type_ = 0
        else:
            type_ = int(type_)-1

        queue_files = [None for i in range(len(empty_folder))]
        files = []
        for i in range(len(count_of_type_jps_files[file_names[0]])):
            if type_:
                x = -1
            else:
                x = 0
            files.append(count_of_type_jps_files[file_names[x]][i])
            files.append(count_of_type_jps_files[file_names[x+1]][i])
        for i, q in enumerate(queue_files):
            if q is None:
                queue_files[i] = files.pop(0)
                
        for pack_info in list_info[::-1]:
            if pack_info.name_dir in empty_folder:
                if len(files):
                    print(files[0], pack_info.name_dir)
                    os.rename(f"{path_to_files}\\{files[0]}", f"{path_to_folders}\\{pack_info.name_dir}\\{files[0]}")
                    files.pop(0)

        


if __name__ == "__main__":
    auto_xml = AutoXML()
    auto_xml.run()
    time.sleep(3)
