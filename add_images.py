import pathlib

path = pathlib.WindowsPath("C:\\Users\\adria\OneDrive - Queensland University of Technology\\IFN557 - Web Dev\\Assignment 2\\cycle\\static\\images")
folder_list = []
for i in path.rglob("*"):
    if i.is_dir():
        folder_list.append(pathlib.WindowsPath(i))

image_list = []
for j in folder_list:
    for img in j.rglob("*"):
        image_list.append(img.name)

print(image_list)

