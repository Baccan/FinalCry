# Monitorar mudanças de arquivos e pegar o PID do processo que o modificou

import os
import time
import psutil
import json

import watchdog.events
import watchdog.observers

import win32evtlog
import xml.etree.ElementTree as ET


# os.system("auditpol.exe /get /category:*")
# quit()


# def get_pid(process_name):
#       for proc in psutil.process_iter():
#         if proc.name() == process_name:
#             return proc.pid

# Reading the json file and getting the folders and files that are going to be
# monitored.
json_file = open('C:\\Users\\user\\Desktop\\FIAP\\LAB_501\\Testes\\securityFolders.json')
json_str = json_file.read()
json_data = json.loads(json_str)

ghostFiles = []
for folder in json_data:
    ghostFiles.append(folder['folderPath'] + '\\' + folder['fullFileName'])

# print(ghostFiles)
# exit()

class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*'],
                                                             ignore_directories=False, case_sensitive=False)

    # def on_created(self, event):
    #     print("Watchdog received created event - % s." % event.src_path)
    #     # Event is created, you can process it now
  
    def on_modified(self, event):
        # if event.src_path != r'C:\\Users\user\Desktop\FIAP\LAB_501\FinalCry\planilha.csv':
        # if event.src_path != r'C:\\Users\user\Desktop\FIAP\LAB_501\Testes\SecurityFolder_2\tysaedyqu.html':
        if event.src_path not in ghostFiles:
            return
            
        print("Watchdog received modified event - % s." % event.src_path)
        pid = os.getpid()

        # time.sleep(1)
        query_handle = win32evtlog.EvtQuery(
            'C:\Windows\System32\winevt\Logs\Security.evtx',
            win32evtlog.EvtQueryFilePath | win32evtlog.EvtQueryReverseDirection)

        read_count = 0
        
        detecting = True

        while read_count <= 500 and detecting:
            events = win32evtlog.EvtNext(query_handle, 100)
            
            read_count += len(events)
            if len(events) == 0: 
                print('No more events')
            
            for index, event in enumerate(events):
                xml_content = win32evtlog.EvtRender(event, win32evtlog.EvtRenderEventXml)
                # SubjectUserSid S-1-5-21-134867458-105844377-4090580669-1001
                # SubjectUserName user
                # SubjectDomainName DESKTOP-C7MCF3M
                # SubjectLogonId 0x29ce6
                # ObjectServer Security
                # ObjectType File
                # ObjectName C:\Users\user\Desktop\FIAP\LAB_501\FinalCry\a.py
                # HandleId 0x2f0
                # AccessList %%4423
                # AccessMask 0x80
                # ProcessId 0x4738
                # 18232
                # ProcessName C:\Python39\python.exe
                # ResourceAttributes S:AI

                # parse xml content
                xml = ET.fromstring(xml_content)

                ns_map = { 'e': 'http://schemas.microsoft.com/win/2004/08/events/event' }

                process_id_converted = None
                is_a_File_ObjectType = False
                is_a_GhostFile = False
                is_a_ransomware = False

                for data in xml.iterfind('.//e:EventData/e:Data', ns_map):
                    # if is_a_File_ObjectType == True:
                    #   print(data.attrib['Name'], data.text)
                    #   quit()

                    if data.attrib['Name'] == 'ObjectType' and data.text == 'File':
                        is_a_File_ObjectType = True
                    
                    # ghostFiles = [r"C:\Users\user\Desktop\FIAP\LAB_501\FinalCry\planilha.csv", r"C:\Users\user\Desktop\FIAP\LAB_501\reserva\a.txt"]

                    # É um tipo de alteração de arquivo
                    if is_a_File_ObjectType == True:
                        # if data.attrib['Name'] == 'ObjectName' and data.text == r"C:\Users\user\Desktop\FIAP\LAB_501\FinalCry\planilha.csv":
                        if data.attrib['Name'] == 'ObjectName' and data.text == r"C:\Users\user\Desktop\FIAP\LAB_501\Testes\SecurityFolder_2\tysaedyqu.html":
                            is_a_GhostFile = True
                            print(data.attrib['Name'], data.text)

                        # if data.attrib['Name'] == 'ObjectName' and data.text in ghostFiles:
                        #     is_a_GhostFile = True
                        #     print(data.attrib['Name'], data.text)

                        # É um arquivo ghost
                        if is_a_GhostFile == True:
                            if data.attrib['Name'] == 'ProcessId':
                                process_id_converted = int(data.text, 16)
                                # print(process_id_converted)

                            if data.attrib['Name'] == 'ProcessName' and 'Explorer' not in data.text and 'Microsoft VS Code' not in data.text:
                            # if data.attrib['Name'] == 'ProcessName' and data.text == 'C:\Python39\python.exe' and process_id_converted == 13892:
                                print("Process found - ", process_id_converted, data.text)
                                is_a_ransomware = True

                            # É um ransomware
                            if is_a_ransomware == True and process_id_converted != pid:
                                for proc in psutil.process_iter():
                                    if proc.pid == process_id_converted:
                                        print('Ransomware found - ', process_id_converted, data.text)
                                        print("Process Kill - ", process_id_converted)
                                        # get process info by PID
                                        p = psutil.Process(process_id_converted)
                                        print(p)
                                        os.kill(process_id_converted, 9)
                                        detecting = False
                                        quit()


    # def on_closed(self, event):
    #     print("Watchdog received closed event - % s." % event.src_path)
    #     # Event is modified, you can process it now

    # def on_deleted(self, event):
    #     print("Watchdog received deleted event - % s." % event.src_path)
    #     # Event is modified, you can process it now

    # def on_moved(self, event):
    #     print("Watchdog received moved event - % s." % event.src_path)
    #     # Event is modified, you can process it now
  
  
if __name__ == "__main__":
    src_path = r"C:\\"
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()