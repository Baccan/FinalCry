import json
import os
import PySimpleGUI as sg

def write_json(data, filename='folders.json'):
    with open(filename,'w') as foldersFile:
        json.dump(data, foldersFile, indent=4)

def main():
    backupFolder = ""
    
    sg.theme('DarkPurple1')
    
    layout = [  
        [sg.Text('Some text on Row 1')],
        [sg.Text('Enter something on Row 2'), sg.InputText()],
        [sg.Text('Select folder to monitor'), sg.In(size=(25,1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()],
        [sg.Button('Ok'), sg.Button('Cancel')],
        # [sg.Listbox(values=[], enable_events=True, size=(40,20), key="-FILE LIST-")],
    ]

    window = sg.Window('Spectre', layout)
    window.set_icon('./assets/Spectre.ico')

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            backupFolder = folder
            
            try:
                file_list = os.listdir(folder)
            except:
                file_list = []
            fnames = [
                f
                for f in file_list
                # if os.path.isfile(os.path.join(folder, f))
                # and f.lower().endswith((".png", ".gif"))
            ]
            window["-FILE LIST-"].update(fnames)
            
        print('You entered ', values[0])

    window.close()

# if backupFolder != "":
    

if __name__ == '__main__':
    main()





# with open('folders.json') as json_file:
#     data = json.load(json_file)

#     backupFolder = r"C:\Users\user\Desktop\FIAP\LAB_501\Testes\BKPs"
#     data['backupFolder'] = backupFolder

#     temp = data['securityFolders']
#     newSecurityFolder = {"folder": r"C:\Users\user\Desktop\FIAP\LAB_501\FinalCry", "file": "planilha.csv"}
#     temp.append(newSecurityFolder)

# write_json(data)