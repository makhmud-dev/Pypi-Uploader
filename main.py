import sys
import os
import shutil
from time import sleep
try:
	import PySimpleGUI as sg
except:
	os.system("pip install pysimplegui")
	import PySimpleGUI as sg

try:
	import setuptools
except:
	os.system("pip install setuptools")

try:
	import twine
except:
	os.system("pip install twine")

try:
	import wheel
except:
	os.system("pip install wheel")

sg.theme('DarkAmber')
window_title = "Pypi uploader"

main = [[sg.T("Select project folder: ", font='16'), sg.FolderBrowse("Browse", target='folder', font='12')],
		[sg.Input("", size=(40,1), key="folder")],
		[sg.T("Important!\nThis folder should contain the __init__.py file!\n", text_color="red", font='Courier 12')],
		[sg.T("Load to:", font='16')],
		[sg.Radio("Pypi", 0, default=False, key="pypi", font='Segoe 12'), sg.Radio("Test Pypi", 0, default=True, key="test_pypi", font='Segoe 12')],[sg.T("")],
		[sg.T("Package name: ", font='12'), sg.Input("", size=(26,1), key="package_name")],
		[sg.T("Version:            ", font='12'), sg.Input("", size=(15,1), key="version")],
		[sg.T("Description:       ", font='12'), sg.Input("", size=(26,1), key="description")],[sg.T("")],
		[sg.T("Select README.md file: ", font='12')],
		[sg.Input("", size=(37,1), key="readme"), sg.FileBrowse("Browse", file_types=(("Markdown File", "*.md"),), target='readme', font='12'), sg.T("(Optional)", text_color="yellow", font='Arial 12')],[sg.T("")],
		[sg.T("Your username:   ", font='12'), sg.Input("", size=(26,1), key="username")],
		[sg.T("Your password:   ", font='12'), sg.Input("", size=(26,1), key="password", password_char='*'),sg.I("", size=(26,1),visible=False, key="pass_show"), sg.B("Show", key="Show")],
		[sg.T("Your email:          ", font='12'), sg.Input("", size=(26,1), key="email")],
		[sg.T("Github repository: ", font='12'), sg.Input("", size=(26,1), key="github"), sg.T("(Optional)", text_color="yellow", font='Arial 12')],[sg.T("")],
		[sg.T("Delete all created files, folders and archives after upload?", font='Segoe 14')],
		[sg.Radio("Yes", 2, default=False, key="delete_yes", font='Segoe 12'), sg.Radio("No", 2, default=True, key="delete_no", font='Segoe 12')],
		[sg.T("")],[sg.T("						"), sg.OK("Upload", font='12')]]


layout = [[sg.Column(main, size=(500,600), scrollable=True, vertical_scroll_only=True)]]

window = sg.Window(window_title, layout)
showing = False
while True:
	event, values = window.read()

	if event == sg.WIN_CLOSED:
		sys.exit()

	if event == "Show":
		showing = not showing
		if showing == True:
			window['pass_show'].update(values["password"], visible=True)
			window['password'].update(visible=False)
			window["Show"].update("Hide")
		else:
			window['pass_show'].update(visible=False)
			window['password'].update(values["pass_show"], visible=True)
			window["Show"].update("Show")

	if event == "Upload":
		break

upload_to_pypi = values["pypi"]
upload_to_test_pypi = values["test_pypi"]
username = values["username"]
if showing == True:
	password = values["pass_show"]
else:
	password = values["password"]

delete_temp_files = False
if values["delete_yes"] == True:
	delete_temp_files = True
package_name = values["package_name"]
path = values["folder"].split("/")
folder = ""
for i in range (len(path)-1):
	folder += path[i]
	
	if i == len(path)-1:
		break
	folder += "/"


required = []
if os.path.exists('requirements.txt'):
	with open('requirements.txt', 'r') as file:
		required = file.readlines()

comand = "import setuptools\n"
if values["readme"] != "":
	comand += "with open(r'" + str(values["readme"].replace("/", "\\")) + "', 'r', encoding='utf-8') as fh:\n"
	comand += "	long_description = fh.read()\n"
comand += "\n"
comand += "setuptools.setup(\n"
comand += "	name='" + str(values["package_name"]) + "',\n"
comand += "	version='" + str(values["version"]) + "',\n"
comand += "	author='" + str(values["username"]) + "',\n"
comand += "	author_email='" + str(values["email"]) + "',\n"
comand += "	description='" + str(values["description"]) + "',\n"

if values["readme"] != "":
	comand += "	long_description=long_description,\n"
	comand += "	long_description_content_type='text/markdown',\n"

if values["github"] != "":
	comand += "	url='" + str(values["github"]) + "',\n"

comand += "	packages=['" + str(path[len(path)-1]) + "'],\n"
comand += '	classifiers=[\n		"Programming Language :: Python :: 3",\n		"License :: OSI Approved :: MIT License",\n		"Operating System :: OS Independent",\n	],\n'
if required:
	comand += f"	install_requires={required},\n"
comand += "	python_requires='>=3.6',\n)"


window.close()

layout = [[sg.T("Generating setup files...", key="text")],[sg.T("")]]
window = sg.Window(window_title, layout)    
event, values = window.read(timeout = 10)
sleep(1)


with open(str(folder) + "setup.py", 'w', encoding='utf-8') as file:
	file.write(comand)

with open(str(folder) + "setup.cfg", 'w') as file:
	file.write("[egg_info]\ntag_build = \ntag_date = 0")

with open(str(folder) + "MANIFEST.in", 'w') as file:
	file.write(f"include {path[len(path)-1]}/*")


window['text'].update("Generating distribution archives...")
window.Refresh()

os.system("python setup.py sdist bdist_wheel")
sleep(1)

window['text'].update("Uploading files...")
window.Refresh()


if upload_to_pypi:
	os.system("python -m twine upload dist/* -u " + str(username) + " -p " + str(password))
else:
	os.system("python -m twine upload --repository testpypi dist/* -u " + str(username) + " -p " + str(password))


if delete_temp_files:
	window['text'].update("Removing temporary files...")
	window.Refresh()

	shutil.rmtree('build')
	shutil.rmtree("dist")
	print(str(package_name) + ".egg-info")
	shutil.rmtree(str(package_name) + ".egg-info")
	os.remove(str(folder) + "setup.cfg")
	os.remove(str(folder) + "setup.py")

window['text'].update("Uploaded successfully!")
window.Refresh()

print("\nUploaded successfully!")
while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED:
		sys.exit()
