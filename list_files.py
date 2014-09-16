import os

def list_files(dir_path):
    file_dict={}
    file_list=os.listdir(path=dir_path)
    for file in file_list:
        dim=(os.path.getsize(dir_path+'/'+file))
        file_dict[file]=round(dim/1024,2)
    return file_dict

                         
    

