import tkinter as tk
from tkinter import messagebox
import sys

from data import Reader

root = tk.Tk()
root.title('스토어 리뷰 크롤러')
root.geometry('150x100')

#var
limit = tk.IntVar()

#command
def kill_process():
    sys.exit()

def start_process():
    Reader(limit.get())
    messagebox.showinfo('info', '크롤링 완료!')

#label
limit_label = tk.Label(root, text='최소수량')
limit_label.grid(row=0, column=0)

#entry
limit_entry = tk.Entry(root, width=10, textvariable=limit)
limit_entry.grid(row=0, column=1)

#button
cancel_btn = tk.Button(root, text='중지', command=kill_process)
cancel_btn.grid(row=0, column=2, padx=5)
start_btn = tk.Button(root, text='시작', command=start_process)
start_btn.grid(row=1, column=2)

root.mainloop()