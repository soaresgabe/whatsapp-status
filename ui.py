import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter.filedialog import askopenfilename, asksaveasfilename
from driver import GetStatus
import pandas as pd
from PIL import Image, ImageTk
import threading
import time


class UI():
    
    def __init__(self):        
        # Create the main window
        self.root = tk.Tk()
        self.driver = GetStatus()
        
        # Set the window size and title
        self.root.geometry("550x550")
        self.root.resizable(False, False)
        self.root.title("WhatsApp Status")
        self.root.iconbitmap("Project\logo.ico")
        
        # Create a frame for the title and login button
        self.header_frame = tk.Frame(self.root, bg="#25D366")
        self.header_frame.pack(side=tk.TOP, fill=tk.X)

        # Create a frame for the UI elements
        self.frame = tk.Frame(self.root, bg="#25D366", padx=2)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a label for the title text
        self.title_label = tk.Label(self.header_frame, text="WhatsApp Status", font=("Helvetica", 16), fg="white", bg="#25D366")
        self.title_label.pack(side=tk.LEFT, expand=True)

        # Create a login button
        self.style = ttk.Style()
        self.style.configure("Login.TButton", padding=3, relief="solid", borderwidth=3, font=("Helvetica", 12), background="#25D366")
        self.login_button = ttk.Button(self.header_frame, text="Login", style="Login.TButton", command=lambda: self.login())
        self.login_button.pack(side=tk.RIGHT)


        # Create a frame for the message list
        self.message_frame = tk.Frame(self.frame, bg="white")
        self.message_frame.pack(fill=tk.BOTH, expand=True)

        # Create a scrollbar for the message list
        self.message_scrollbar = tk.Scrollbar(self.message_frame)
        self.message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a listbox for the messages
        self.message_list = tk.Listbox(self.message_frame, yscrollcommand=self.message_scrollbar.set)

        # Pack the message listbox and make it fill the frame
        self.message_list.pack(fill=tk.BOTH, expand=True)

        # Connect the scrollbar to the message listbox
        self.message_scrollbar.config(command=self.message_list.yview)

        # Create a frame for the input field
        self.input_frame = tk.Frame(self.frame, bg="#ece5dd")
        self.input_frame.pack(fill=tk.X, pady=10)

        # Create an entry widget for the input field
        self.input_entry = tk.Entry(self.input_frame, font=("Helvetica", 20))
        self.input_entry.pack(fill=tk.X, expand=True, padx=5, pady=3)

        # Bind the '<Return>' key to the input field
        self.input_entry.bind("<Return>", self.add_message)
       
        self.style = ttk.Style()
        self.style.configure("Round.TButton", padding=3, relief="solid", borderwidth=3, font=("Helvetica", 12), shape="circle")
        
        self.upload_button = ttk.Button(self.input_frame, text="Upload File", style="Round.TButton", command=self.upload_file)
        self.downloadall_button = ttk.Button(self.input_frame, text="Invalid Only", style="Round.TButton", command=self.download_invalid)
        self.downloadvalid_button = ttk.Button(self.input_frame, text="Valid Only", style="Round.TButton", command=self.download_valid)
        self.downloadinvalid_button = ttk.Button(self.input_frame, text="Download", style="Round.TButton", command=self.download_all)
        
        # Create a button to upload a CSV file
        self.upload_button.pack(side=tk.LEFT, pady=1, padx=1)

        # DOWNLOADS
        self.downloadall_button.pack(side=tk.RIGHT, pady=1, padx=1)
        self.downloadvalid_button.pack(side=tk.RIGHT, pady=1, padx=1)
        self.downloadinvalid_button.pack(side=tk.RIGHT, pady=1, padx=1)
        
    def upload_file(self):
        file_path = askopenfilename()
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            data = pd.read_excel(file_path)

        data_list = data[data.columns[0]].tolist()
        
        self.resultCSV = {}
        self.validsCSV = []
        self.invalidsCSV = []

        for n in data_list:

            status = self.check(n)
            self.resultCSV[n] = status

            if (status == "Valid Number."):
                self.validsCSV.append(n)
            elif (status == "Invalid Number."):
                self.invalidsCSV.append(n)
            
            self.root.update()
        self.driver.login()

        self.message_list.insert(tk.END, "")
        self.message_list.insert(tk.END, f"Your verification is done for {len(data_list)} numbers.")
        self.message_list.insert(tk.END, f"{len(self.validsCSV)} valids. {len(self.invalidsCSV)} invalids. {len(self.resultCSV) - (len(self.validsCSV) + len(self.invalidsCSV))} erros.")

    def download_all(self):
        df = pd.DataFrame.from_dict(self.resultCSV, orient='index')
        file_path = asksaveasfilename(defaultextension='.csv', initialfile='all_numbers.csv')
        df.to_csv(file_path, header=False)
        
    def download_valid(self):
        df = pd.DataFrame(self.validsCSV)
        file_path = asksaveasfilename(defaultextension='.csv', initialfile='valid_numbers.csv')
        df.to_csv(file_path, index=False, header=False)
    
    def download_invalid(self):
        df = pd.DataFrame(self.invalidsCSV)
        file_path = asksaveasfilename(defaultextension='.csv', initialfile='invalid_numbers.csv')
        df.to_csv(file_path, index=False, header=False)
        
    # LOGIN
    def checkOne(self): #switch_bindings
        # unbind the <Return> from the old entry
        self.input_entry.unbind("<Return>")

        # create the popup
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Single Check")
        self.popup.iconbitmap("Project\logo.ico")
        self.popup.geometry("200x100")
        self.popup.configure(bg='#25D366')
        self.popup.resizable(0, 0)

        # center the popup in the main window
        x = (self.root.winfo_screenwidth() - self.popup.winfo_reqwidth()) / 2
        y = (self.root.winfo_screenheight() - self.popup.winfo_reqheight()) / 2
        self.popup.geometry("+%d+%d" % (x, y))

        # make the main window unclickable and unmovable
        self.popup.grab_set()

        frame = tk.Frame(self.popup, bd=2, relief=tk.SUNKEN, bg='#25D366')
        frame.pack(fill=tk.BOTH, expand=True)

        # create a label for the title
        title_label = tk.Label(frame, text="Username:", bg='#25D366', fg='white', font=("TkDefaultFont", 14))
        title_label.pack(pady=(10, 0))

        # create a new entry in the popup
        self.popup_entry = tk.Entry(frame, font=("TkDefaultFont", 14), bg='#fff', fg='black')
        self.popup_entry.pack()

        # bind the <Return> to the new entry
        self.popup.bind("<Return>", lambda event, entry=self.popup_entry: self.popup_action(event))

    def popup_action(self, event):
        # get the text from the entry
        popup_text = self.popup_entry.get()
        self.message_list.insert(tk.END, popup_text)

        # destroy the popup
        self.popup.destroy()

        # bind the <Return> back to the main entry
        self.root.bind("<Return>", lambda event, entry=self.input_entry: self.add_message(event))

    # Function to add message to the message list
    def add_message(self, event):
        # Get the text from the input field
        text = self.input_entry.get()
        self.check(text)

    def check(self, id):
        # For Brazil here it's 11, you can remove it but helps find errors beforehand. (can also be added a country code and use it)
        id = str(id)
        if(len(id) < 11): 
            self.message_list.insert(tk.END, f"{id}: ERROR! Not enough digits, verify the number and try again.")
        elif(len(id) > 11):
            self.message_list.insert(tk.END, f"{id}: ERROR! Too many digits, verify the number and try again.")
        else:
            
            number = "55" + id

            self.message_list.insert(tk.END, f"Checking status for {number}...")
            
            self.root.update()
            status = self.driver.run(number)
            
            self.message_list.insert(tk.END, f"{number} : {status}")

        # Clear the input field
        self.input_entry.delete(0, tk.END)
        return status

    def login(self):

        self.driver.login()
        # time.sleep(10)

        # # create the popup
        # self.popup = tk.Toplevel(self.root)
        # self.popup.title("Login")
        # self.popup.iconbitmap("Project\logo.ico")
        # self.popup.geometry("300x300")
        # self.popup.configure(bg='#25D366')
        # self.popup.resizable(0, 0)

        # # center the popup in the main window
        # x = (self.root.winfo_screenwidth() - self.popup.winfo_reqwidth()) / 2
        # y = (self.root.winfo_screenheight() - self.popup.winfo_reqheight()) / 2
        # self.popup.geometry("+%d+%d" % (x, y))

        # # make the main window unclickable and unmovable
        # self.popup.grab_set()

        # frame = tk.Frame(self.popup, bd=2, relief=tk.SUNKEN, bg='#25D366')
        # frame.pack(fill=tk.BOTH, expand=True)

        # image = Image.open("qr_code.png")
        # image = image.resize((300, 300), Image.ANTIALIAS)
        # image = ImageTk.PhotoImage(image)
            
        # self.canvas = tk.Canvas(frame, width=270, height=270)
        # self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        # self.canvas.pack(fill=tk.BOTH, expand=True)
