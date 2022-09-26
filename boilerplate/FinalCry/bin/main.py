import json
import os
import time
import psutil

import watchdog.events
import watchdog.observers

import win32evtlog
import xml.etree.ElementTree as ET
import win32api

from winotify import Notification, audio

# import win32api

# win32api.MessageBox(0, 'hello', 'title')
# exit()

# get pid from C:\Users\user\Desktop\FIAP\LAB_501\Testes\pid.txt
def get_pid_of_spectre():
    with open(r'"C:\Program Files (x86)\Final Cry\pid.txt"', 'r') as f:
        pid = f.read()
        return pid

def notify_ransomware():
    toast = Notification(app_id="Final Cry",
                     title="Um ransomware foi detectado",
                     msg="Não desligue o computador e entre em contato com o suporte técnico",
                     duration='long',
                     icon=r"C:\Users\user\Desktop\FIAP\LAB_501\Challenge\Spectre\Spectre.ico")

    toast.set_audio(audio.Mail, loop=False)
    toast.show()

    win32api.MessageBox(0, 'Um ransomware foi detectado.\nNão desligue seu dispositivo!\nPor favor entre em contato com o suporte para mais informações.', 'Final Cry', 0x00001000)

# Reading the json file and getting the folders and files that are going to be
# monitored.
json_file = open(r'C:\Program Files (x86)\Final Cry\securityFolders.json')
json_str = json_file.read()
json_data = json.loads(json_str)

ghostFiles = []
for folder in json_data:
    ghostFiles.append(folder['folderPath'] + '\\' + folder['fullFileName'])

# Getting the user that is modifying the file
def get_user():
    pid = os.getpid()

    query_handle = win32evtlog.EvtQuery(
        'C:\Windows\System32\winevt\Logs\Security.evtx',
        win32evtlog.EvtQueryFilePath | win32evtlog.EvtQueryReverseDirection)

    read_count = 0

    detecting = True

    while read_count <= 100 and detecting:
        events = win32evtlog.EvtNext(query_handle, 100)
        
        read_count += len(events)
        if len(events) == 0: 
            print('No more events')
        if events:
            for event in events:
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
                # print xml content
                # print(ET.tostring(xml, encoding='utf8').decode('utf8'))
                # exit()


                ns_map = { 'e': 'http://schemas.microsoft.com/win/2004/08/events/event' }

                subject_user_sid = None
                process_id_converted = None
                is_a_File_ObjectType = False
                is_a_GhostFile = False
                is_a_ransomware = False

                for data in xml.iterfind('.//e:EventData/e:Data', ns_map):
                    if data.attrib['Name'] == 'ProcessId':
                        process_id_converted = int(data.text, 16)
                        # print(process_id_converted)

                    if data.attrib['Name'] == 'ObjectType' and data.text == 'File':
                        is_a_File_ObjectType = True

                    if data.attrib['Name'] == 'SubjectUserName':
                        subject_user_sid = data.text
                    
                    # É um tipo de alteração de arquivo
                    if is_a_File_ObjectType == True:
                        # Checando se o arquivo modificado é um arquivo fantasma (em alguns casos, o event log não retorna o nome do arquivo)
                        # if data.attrib['Name'] == 'ObjectName' and data.text in ghostFiles:
                        #     is_a_GhostFile = True
                        #     print(data.attrib['Name'], data.text)
                        is_a_GhostFile = True


                        # É um arquivo ghost
                        if is_a_GhostFile == True:
                            if data.attrib['Name'] == 'ProcessId':
                                process_id_converted = int(data.text, 16)
                                # print(process_id_converted)

                            # dont_kill_this_process = [
                            #     'Microsoft VS Code',
                            #     'Kaspersky',
                            # ]

                            if data.attrib['Name'] == 'ProcessName' and 'Explorer' not in data.text and 'Microsoft VS Code' not in data.text and 'Kaspersky' not in data.text:
                            # if data.attrib['Name'] == 'ProcessName' and data.text == 'C:\Python39\python.exe' and process_id_converted == 13892:
                                print("Process found - ", process_id_converted, data.text)
                                is_a_ransomware = True

                            # É um ransomware
                            if is_a_ransomware == True and process_id_converted != pid and process_id_converted != get_pid_of_spectre():
                                for proc in psutil.process_iter():
                                    if proc.pid == process_id_converted:
                                        print('Ransomware found - ', process_id_converted, data.text)
                                        print("Process Kill - ", process_id_converted)
                                        # get process info by PID
                                        p = psutil.Process(process_id_converted)
                                        print(p)
                                        os.kill(process_id_converted, 9)
                                        notify_ransomware()
                                        detecting = False
                                        return([subject_user_sid,process_id_converted])
                                        # quit()
    return None

    # handle = win32evtlog.OpenEventLog(None, "Security")
    # flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    # total = win32evtlog.GetNumberOfEventLogRecords(handle)
    # events = win32evtlog.ReadEventLog(handle, flags, 0)

    # if event.EventID == 4656:
    #     xml = ET.fromstring(event.StringInserts[-1])
    #     if xml.find('Data[@Name="ProcessId"]').text == str(pid):
    #         return xml.find('Data[@Name="SubjectUserSid"]').text.split('-')[-1]

# Getting the file that is being modified
def get_file(event):
    if event.is_directory:
        return None
    else:
        return event.src_path

# Getting the time that the file is being modified
def get_time():
    return time.strftime("%d/%m/%Y %H:%M:%S")

# Getting the event that is happening
def get_event(event):
    if event.event_type == 'created':
        return 'Created'
    elif event.event_type == 'modified':
        return 'Modified'
    elif event.event_type == 'deleted':
        return 'Deleted'
    elif event.event_type == 'moved':
        return 'Moved'

# Writing the log file
def write_log(event):
    if event.src_path in ghostFiles:
        print("Watchdog received modified event - % s." % event.src_path)
        try:
            file = get_file(event)
            pid_and_user = get_user()
            time_now = get_time()
            event_type = get_event(event)
            if pid_and_user != None:
                with open(r'C:\Program Files (x86)\Final Cry\log.csv', 'a+') as file_object:
                    file_object.seek(0)
                    data = file_object.read(100)
                    if len(data) > 0 :
                        file_object.write("\n")
                    file_object.write(f'{file};{pid_and_user[0]};{pid_and_user[1]};{time_now};{event_type}')
        except:
            print("Error getting process info")

# Creating the event handler
class MyHandler(watchdog.events.PatternMatchingEventHandler):
    patterns = ["*"]

    def process(self, event):
        write_log(event)

    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)

    def on_moved(self, event):
        self.process(event)

# Creating the observer
if __name__ == '__main__':
    path = 'C:\\'
    event_handler = MyHandler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()