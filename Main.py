import tkinter as tk, pandas as pd, pyodbc, re
from tkinter import ttk, messagebox

config = {}

def query_db(query,limit):
    db = pyodbc.connect(f"Driver={config['driver']};"
                                f"UID={config['uid']};"
                                f"PASSWORD={config['password']};"
                                f"DatabaseName={config['database']};"
                                f"ServerName={config['server']};"
                                f"Integrated={config['integrated']};"
                                f"Encryption={config['encryption']};"
                                f"Host={config['host']}")
    df = pd.read_sql_query(query, db)
    return df.head(limit)

def highlight_syntax():
    query_text.tag_remove("keyword", "1.0", tk.END)
    
    keywords = [
        "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE",
        "CREATE", "DROP", "ALTER", "JOIN", "INNER", "OUTER",
        "LEFT", "RIGHT", "ON", "AND", "OR", "NOT", "NULL",
        "LIKE", "IN", "AS", "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "DECLARE", "SET", "BETWEEN"
    ]
    
    for keyword in keywords:
        start_index = "1.0"

        while True:
            pos = query_text.search(r"\y" + re.escape(keyword) + r"\y", start_index,
                        stopindex=tk.END, nocase=True, regexp=True)
            if not pos: break

            end_index = f"{pos}+{len(keyword)}c"
            query_text.tag_add("keyword", pos, end_index)
            start_index = end_index

def limit_lines(limit):
    content = query_text.get("1.0", "end-1c")
    lines = content.split("\n")
    if len(lines) > 100:
        truncated_content = "\n".join(lines[:100])

        query_text.delete("1.0", tk.END)
        query_text.insert("1.0", truncated_content)

def on_key_release(event=None):
    limit = 100 # config['lines_limit']
    limit_lines(limit)
    highlight_syntax()

def execute_query():
    limit_lines = 100
    query = query_text.get("1.0", tk.END).strip()
    if not query:
        messagebox.showwarning("Input Error", "Please inform a valid SQL query.")
        return
    try:
        df = query_db(query, limit_lines)
        for item in tree.get_children(): 
            tree.delete(item)
        
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center", stretch=True)
        
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))
            
    except Exception as e: show_error_with_copy(e,query)

def load_query_from_config(file_path="autosave.txt"): # config['autosave_path']
    try:
        with open(file_path, "r") as f:
            config_query = f.read()
        query_text.insert("1.0", config_query)
    except Exception as e:
        messagebox.showerror("Error trying to read autosave", f"Erro:\n{e}")

def on_closing():
    try:
        config_content = query_text.get("1.0", "end-1c")
        with open("autosave.txt", "w") as f:
            f.write(config_content)
    except Exception as e:
        messagebox.showerror("Error", f"Error trying to save autosave:\n{e}")
    root.destroy()

def show_error_with_copy(error_text,query):
    error_window = tk.Toplevel(root)
    error_window.title("Query Error")
    error_window.geometry("400x200")
    
    error_label = tk.Label(error_window, text=error_text, padx=10, pady=10, justify=tk.LEFT, wraplength=380)
    error_label.pack(fill=tk.BOTH, expand=True)

    gpt_error_text = f"""
        The following query: {query}
        Gave me the following error: {error_text}
        Help me solve this error, remembering that it is a query in SQL Anywhere 17.
    """
    
    def copy_error():
        root.clipboard_clear()
        root.clipboard_append(error_text)

    def copy_gpt():
        root.clipboard_clear()
        root.clipboard_append(gpt_error_text)
    
    button_frame = tk.Frame(error_window)
    button_frame.pack(pady=10)
    
    copy_button = tk.Button(button_frame, text="Copy Error", command=copy_error)
    copy_button.pack(side=tk.LEFT, padx=(0, 10))

    gpt_copy_button = tk.Button(button_frame, text="Copy Error for AI Prompt", command=copy_gpt)
    gpt_copy_button.pack(side=tk.LEFT, padx=(0, 10))
    
    close_button = tk.Button(button_frame, text="Fechar", command=error_window.destroy)
    close_button.pack(side=tk.LEFT)

root = tk.Tk()
root.title("Simple SQL-SAP-Anywhere-Sybase Client")
root.geometry("800x600")

input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.pack(fill="both", expand=False)

query_label = tk.Label(input_frame, text="Query:")
query_label.pack(anchor="w")

query_text = tk.Text(input_frame, wrap="none", height=10)
query_text.pack(fill="both", expand=True, pady=(0, 10))

query_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=query_text.yview)
query_scrollbar.pack(side="right", fill="y")
query_text.configure(yscrollcommand=query_scrollbar.set)

query_text.bind("<KeyRelease>", on_key_release)

load_query_from_config("autosave.txt") # config['autosave_path']

execute_button = tk.Button(input_frame, text="Execute Query (F9)", command=execute_query)
execute_button.pack()

table_frame = tk.Frame(root, padx=10, pady=10)
table_frame.pack(fill="both", expand=True)

tree = ttk.Treeview(table_frame)
tree.pack(side="left", fill="both", expand=True)

vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
vsb.pack(side="right", fill="y")
tree.configure(yscrollcommand=vsb.set)

hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
hsb.pack(fill="x")
tree.configure(xscrollcommand=hsb.set)

query_text.tag_config("keyword", foreground="blue", font=("Courier New", 10, "bold"))

root.bind("<F9>", lambda event: execute_query())
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
