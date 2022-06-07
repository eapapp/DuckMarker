import re

import xml.etree.ElementTree as ET
from xml.dom import minidom

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import tkinter.ttk as ttk

import uuid
from datetime import datetime

mainpane = None
optvar = None

SPdict = {"ebrain01": "ebrain01",
          "SP1": "bp00sp01",
          "SP2": "bp00sp02",
          "SP3": "bp00sp03",
          "SP4": "bp00sp04",
          "SP5": "bp00sp05",
          "SP6": "bp00sp06",
          "SP8": "bp00sp08",
          "covid19": "covid19",
          "External": "bp00ext",       
          "EBRAINS": "ebrain01"}

xmldict = {"Protocol": "swift",
            "Provider": "openstack-keystone3",
            "Nickname": "",
            "UUID": "",
            "Hostname": "ksproxy.cscs.ch",
            "Port": "13000",
            "Username": "",
            "Path": "",
            "Access Timestamp": ""}

doctype = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'

def quitDm():
    root.destroy()


def getContainer():

    cont = mainpane.nametowidget('txtContainer')
    cname = cont.get()

    if len(cname) > 0 and not cname[0] == '/':
        cname = '/' + cname

    return cname


def checkSpaces(user, container):

    error = False

    if len(user) == 0:
        messagebox.showwarning('Error - Invalid user name', 'Please fill in your CSCS user name.')
        error = True

    elif ' ' in user:
        messagebox.showwarning('Error - Invalid user name', 'You have a space in your user name. Please check again.')
        error = True


    if len(container) == 0:
        messagebox.showwarning('Error - Invalid container name', 'Please fill in the CSCS container name.')
        error = True

    elif ' ' in container:
        messagebox.showwarning('Error - Invalid container name', 'You have a space in the container name. Please check again.')
        error = True

    if error:
        return True
    
    return False


def valid(prj, usr, cont):

    if prj == '...':
        messagebox.showwarning('Error - Invalid subproject', 'Please select a subproject.')
        return False

    # if len(usr) == 0 or len(cont) == 0:
    #     return False

    if checkSpaces(usr,cont):
        return False

    return True

def exportDm(root):

    global xmldict

    opt = optvar.get()
    usrobj = mainpane.nametowidget('txtUser')
    usr = usrobj.get().strip()
    cont = getContainer().strip()

    if not valid(opt, usr, cont):
        return

    prj = SPdict[opt]

    xmldict["UUID"] = str(uuid.uuid4())
    xmldict["Username"] = prj + ":cscs:" + usr
    xmldict["Path"] = cont
    xmldict["Nickname"] = xmldict["Path"][1:]
    xmldict["Access Timestamp"] = str(int(datetime.timestamp(datetime.now())*1000))

    file_path = filedialog.asksaveasfilename(title = "Export Cyberduck Bookmark", filetypes = (("Cyberduck Bookmark", "*.duck"),("All files","*.*")))

    if file_path != "":     

        if file_path[-5:] != '.duck':
            fname = file_path.split('.')[0]
            file_path = fname + '.duck'

        duckroot = ET.Element("plist")
        duckroot.attrib["version"] = "1.0"
        dicttag = ET.SubElement(duckroot,"dict")

        for tag in xmldict:
            keytag = ET.SubElement(dicttag, "key")
            keytag.text = tag
            valuetag = ET.SubElement(dicttag, "string")
            valuetag.text = xmldict[tag]

        ugly = doctype + ET.tostring(duckroot, encoding = "unicode")
        ugly = re.sub(r"\n|\t+","",ugly)
        reparsed = minidom.parseString(ugly)
        pretty_xml = reparsed.toprettyxml(encoding = "UTF-8").decode("utf-8")

        m = re.search("(<!.*dtd'>)", pretty_xml, re.DOTALL)
        ugly_doctype = m.group() 
        fixed_xml = pretty_xml.replace(ugly_doctype, doctype).encode("utf-8")

        f = open(file_path,"w+b")
        f.write(fixed_xml)
        f.close()


def loadGUI():
    
    global mainpane
    global optvar

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", quitDm)
    root.title("DuckMarker")
    root.minsize(392,135)
    root.resizable(width=False, height=False)

    mainpane = tk.Frame(root, padx="10", pady="10")
    mainpane.grid(row=0, column=0, sticky="NEWS")

    lblSP = tk.Label(mainpane, text="Select HBP subproject (SP):")
    lblSP.grid(row=0, column=0, sticky="NW")

    lblUser = tk.Label(mainpane, text="CSCS user name:")
    lblUser.grid(row=1, column=0, sticky="NW")

    lblContainer = tk.Label(mainpane, text="CSCS container name:")
    lblContainer.grid(row=2, column=0, sticky="NW")

    s = ttk.Style()
    s.configure("TMenubutton", background="white")   

    optvar = tk.StringVar(root)
    optvar.set("")

    optSP = ttk.OptionMenu(mainpane, optvar, "...", *tuple(SPdict.keys()))
    optSP.config(width=30)
    optSP.grid(row=0, column=1, sticky="EW")
        
    txtUser = tk.Entry(mainpane, name="txtUser", width=36)
    txtUser.grid(row=1, column=1, sticky="NW")

    txtContainer = tk.Entry(mainpane, name="txtContainer", width=36)
    txtContainer.grid(row=2, column=1, sticky="NW")    

    btnpane = tk.Frame(root, padx="10", pady="10")
    btnpane.grid(row=1, column=0, sticky="EW")

    btnExport = tk.Button(btnpane, text="Export bookmark", command=lambda: exportDm(root), width=18)
    btnExport.grid(row=0, column=0, sticky="EW", padx="5")

    btnQuit = tk.Button(btnpane, text="Quit", command=quitDm, width=16)
    btnQuit.grid(row=0, column=1, sticky="EW", padx="5")

    root.grid_rowconfigure(0, weight=0)
    root.grid_columnconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(1, weight=0)
    
    return(root)


if __name__ == "__main__":

    root = loadGUI()
    root.mainloop()    
