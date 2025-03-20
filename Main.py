import tkinter as tk, re
from tkinter import ttk, messagebox
from _DB import query_db, configure_db
from _Config import config_setting, get_config
from _Autosave import load_query_from_autosave

config_setting()
config = get_config()

def highlight_syntax():
    query_text.tag_remove("keyword", "1.0", tk.END)
    
    keywords = [
        "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "BETWEEN",
        "CREATE", "DROP", "ALTER", "JOIN", "INNER", "OUTER", "SET",
        "LEFT", "RIGHT", "ON", "AND", "OR", "NOT", "NULL", "DECLARE",  
        "LIKE", "IN", "AS", "ORDER", "BY", "GROUP", "HAVING", "LIMIT"
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

def limit_lines():
    content = query_text.get("1.0", "end-1c")
    lines = content.split("\n")
    if len(lines) > config['lines_limit']:
        truncated_content = "\n".join(lines[:config['lines_limit']])

        query_text.delete("1.0", tk.END)
        query_text.insert("1.0", truncated_content)

def on_key_release(event=None):
    limit = config['lines_limit']
    limit_lines(limit)
    highlight_syntax()

def execute_query():
    limit_lines = 100
    query = query_text.get("1.0", tk.END).strip()
    if not query:
        messagebox.showwarning("Input Error", "Please inform something.")
        return
    try:
        df = query_db(config, query, config['lines_limit'])
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
        Help me solve this error, remembering that it is a query in {config['driver']}.
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
    
    close_button = tk.Button(button_frame, text="Close", command=error_window.destroy)
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

load_query_from_autosave(config['autosave_path'], query_text)

execute_button = tk.Button(input_frame, text="Execute Query (F9)", command=execute_query)
execute_button.pack()

configure_button = tk.Button(input_frame, text="Configure", command=configure_db)
configure_button.pack(side="left",padx=1)

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
