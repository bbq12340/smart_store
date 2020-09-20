import tkinter as tk
from tkinter import messagebox,filedialog

from data import Reader

root = tk.Tk()
root.title('스토어 리뷰 크롤러')
root.geometry('250x150')

#var
limit = tk.IntVar()
no_limit = tk.IntVar()
delay_item = tk.IntVar()
delay_time = tk.IntVar()
FILENAME = []

#command
def add_file():
    filename = filedialog.askopenfilename(initialdir='/', title='파일 탐색', filetypes=[("text files", "*.txt")])
    filename_label = tk.Label(root, text=f"{filename.split('/')[-1]}")
    filename_label.grid(row=0, column=1)
    FILENAME.append(filename)

def start_process():
    if no_limit.get() == 0:
        print('제한 있음')
        Reader(FILENAME[0], limit=limit.get(), items=delay_item.get(), delay=delay_time.get())
        messagebox.showinfo('info', '크롤링 완료!')
    else:
        print('제한 없음')
        Reader(FILENAME[0], items=delay_item.get(), delay=delay_time.get())
        messagebox.showinfo('info', '크롤링 완료!')

#label
request_label = tk.Label(root, text='요청 파일명:')
request_label.grid(row=0, column=0)

limit_label = tk.Label(root, text='최소 수량')
limit_label.grid(row=1, column=0)

delay_item_label = tk.Label(root, text="딜레이 리뷰수")
delay_item_label.grid(row=2, column=0)

delay_time_label = tk.Label(root, text="딜레이 (초)")
delay_time_label.grid(row=3, column=0)

#checkbutton
limit_check = tk.Checkbutton(root, text='전체', variable=no_limit)
limit_check.grid(row=1, column=2)

#entry
limit_entry = tk.Entry(root, width=7, textvariable=limit)
limit_entry.grid(row=1, column=1)

delay_item_entry = tk.Entry(root, width=7, textvariable=delay_item)
delay_item_entry.grid(row=2, column=1)

delay_time_entry = tk.Entry(root, width=7, textvariable=delay_time)
delay_time_entry.grid(row=3, column=1)

#button
search_btn = tk.Button(root, text='파일 탐색', command=add_file)
search_btn.grid(row=0, column=2)
start_btn = tk.Button(root, text='시작', command=start_process)
start_btn.grid(row=3, column=2)

root.mainloop()