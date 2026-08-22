#main
import sys, os
from openpyxl import load_workbook
import time
from copy import copy
# telegram
import python_socks
from telethon import TelegramClient
#crypto
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Pack:
    def __init__(self, name_dir, name_file, size_file):
        self.name = ""
        for i in name_dir:
            if i == "-":
                break
            
            self.name += i 
        self.name_dir = name_dir
        self.name_file = name_file
        self.size_file = str(round(size_file / 1024 / 1024, 1)).replace(",", ".")
        print(self.name, name_dir, name_file, self.size_file)

class SafetyStorage:
    
        
class TelegramConnect:
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        self.proxy_type = python_socks.ProsyType.SOCK5
        self.proxy_host = "127.0.0.1"
        self.proxy_port = 1443
        self.proxy_user = None
        self.proxy_password = None

class AutoXML:

    def __init__(self):
        self.name = input("Имя: ")
        self.path = input("Путь до директории: ")
        self.source_path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])
        if not self.name:
            self.name = "2026-08-19_Координирование ОП TЕСТ"
        if not self.path:
            self.path = "C:\\Users\\user\\Desktop\\2026-08-04_ЮТэйр_2026\\Координирование\\2026_08_19_Ютэйр ОП(Воропанов)"

    def search_into_directory(self, path):
        list_= []
        for dir_ in os.listdir(path):
            dir_path = f"{path}\\{dir_}"
            if os.path.isdir(dir_path):
                
                file_name = []
                for name in os.listdir(dir_path):
                    if name[-4:] == ".jps":
                        file_name.append(name[:-4])

                if len(file_name) != 1:
                    raise ValueError(f"Слишком много файлов .jps в одной папке {dir_}")
                list_.append(Pack(dir_, file_name[0], os.path.getsize(f"{dir_path}\\{file_name[0]}.jps")))
        return list_

    def connect_to_telegram(self):
        pass

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
        for i, info in enumerate(list_info):
            self.full_copy_paste_string(ws, 4, 4+i, 10)
            self.fill_string(ws, 4+i, info)
            

        wb.save(f"{self.path}\\{self.name}.xlsx")

    def fill_string(self, ws, number_string, string):
        ws[f'A{number_string}'] = string.name
        ws[f'B{number_string}'] = string.name_dir
        ws[f'H{number_string}'] = string.name_file
        ws[f'I{number_string}'] = string.size_file
                
                
        
    def run(self):
        list_information = self.search_into_directory(self.path)
        self.create_XML(list_information)
        


            

if __name__ == "__main__":
    auto_xml = AutoXML()
    auto_xml.run()
    time.sleep(3)
