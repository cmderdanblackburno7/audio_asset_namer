"""Run directly with Python 3.10+; no third-party packages."""
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from core import VERSION, export_plan, filename, load_plan, validate_titles
from exporting import exists, prepare_export
from theme import COLORS, apply_theme
from windows_branding import apply_window_branding, asset_path, set_app_id

WEBSITE = "https://binaurawave.com/"
UTM_PARAMETERS = (
    ("utm_source", "asset-namer"),
    ("utm_medium", "desktop_app"),
    ("utm_campaign", "free_creator_tools"),
)


def website_link(url):
    """Add campaign attribution locally; opening remains an explicit UI action."""
    parts = urlsplit(url)
    keys = {key for key, _ in UTM_PARAMETERS}
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if key not in keys]
    return urlunsplit(parts._replace(query=urlencode(query + list(UTM_PARAMETERS))))


FOOTER_LINKS = (
    ("BinauraWave", website_link(WEBSITE)),
    ("Create Audio Sessions", website_link(WEBSITE + "binaurawave_app/")),
    ("Help & Support", website_link(WEBSITE + "feedback/")),
)
# Verified public repository; opened only on an explicit footer click.
GITHUB_URL = "https://github.com/cmderdanblackburno7/audio_asset_namer"
LOCAL_FILES_NOTE = ("Organise and name your audio clips locally. No account required. "
                    "Your audio files and scripts remain on your computer.")


class App:
    def __init__(self, root):
        self.root, self.plan, self.selected, self.busy = root, None, None, False
        self.events = queue.Queue()
        root.title(f"BinauraWave Audio Asset Namer {VERSION}")
        root.geometry("1100x820")
        root.minsize(800, 650)
        self.style = apply_theme(root)
        self.folder, self.script, self.title = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.add_footer()
        main = ttk.Frame(root, padding=12)
        main.pack(fill="both", expand=True)
        self.add_header(main)
        for label, variable, command in (("Audio folder", self.folder, self.choose_folder),
                                          ("UTF-8 script", self.script, self.choose_script)):
            row = ttk.Frame(main)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=label, width=16).pack(side="left")
            ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
            ttk.Button(row, text="Browse…", command=command).pack(side="left", padx=6)
        ttk.Button(main, text="Load / reload preview", command=self.load).pack(anchor="w", pady=8)
        self.status = ttk.Label(main, text="Select the exports and script, then load the preview.", wraplength=1000, style="Muted.TLabel")
        self.status.pack(fill="x")
        table = ttk.Frame(main)
        table.pack(fill="both", expand=True, pady=8)
        self.tree = ttk.Treeview(table, columns=("number", "original", "title", "output"), show="headings", height=9)
        for key, label, width in (("number", "Paragraph", 70), ("original", "Original filename", 230),
                                  ("title", "Editable title (select a row)", 270), ("output", "Resulting filename", 330)):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=60)
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select)
        ttk.Label(main, text="Title — edit here; the filename preview updates immediately (maximum 50 characters)").pack(anchor="w")
        self.editor = ttk.Entry(main, textvariable=self.title)
        self.editor.pack(fill="x", pady=4)
        self.title.trace_add("write", self.edit)
        self.original = self.text_area(main, "Full original paragraph (read only)", 4)
        self.spoken = self.text_area(main, "Cleaned spoken text — [pause] removed (read only)", 3)
        self.copy_button = ttk.Button(main, text="Confirm and copy…", command=self.copy, state="disabled", style="Primary.TButton")
        self.copy_button.pack(anchor="w", pady=8)
        self.log = self.text_area(main, "Per-file results", 4)
        root.bind("<Configure>", self.fit_workspace, add="+")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Map>", self.apply_native_branding, add="+")
        root.after(100, self.poll)

    def apply_native_branding(self, event=None):
        if event is not None:
            if event.widget == self.root:
                # The first native map can recreate Tk's wrapper HWND; waiting
                # until after mapping also handles restore/remap safely.
                self.root.after_idle(self.apply_native_branding)
            return
        self.native_branding = apply_window_branding(self.root)

    def add_header(self, parent):
        header = tk.Frame(parent, background=COLORS["background"], padx=10, pady=4)
        header.pack(fill="x", pady=(0, 8))
        self.logo = None
        try:
            original = tk.PhotoImage(file=str(asset_path("assets/logo.png")))
            factor = max(1, (original.width() + 139) // 140, (original.height() + 27) // 28)
            self.logo = original.subsample(factor, factor)
            tk.Label(header, image=self.logo, background=COLORS["background"]).pack(side="left", padx=(0, 14))
        except (OSError, tk.TclError):
            pass  # Keep the utility usable if a manually copied package omits the asset.
        tk.Label(header, text="BinauraWave Audio Asset Namer", font=("Segoe UI", 12, "bold"),
                 foreground=COLORS["text"], background=COLORS["background"]).pack(side="left")
        tk.Frame(parent, background=COLORS["gold"], height=1).pack(fill="x", pady=(0, 5))

    def add_footer(self):
        # Reserve space before packing the workspace so results cannot cover it.
        self.footer = tk.Frame(self.root, background=COLORS["background"], padx=8, pady=3)
        self.footer.pack(side="bottom", fill="x")
        self.link_buttons = {}
        for label, url in (*FOOTER_LINKS, ("GitHub", GITHUB_URL)):
            button = ttk.Button(self.footer, text=label, command=lambda url=url: self.open_link(url),
                                state="normal" if url else "disabled", style="Link.TButton",
                                cursor="hand2" if url else "arrow", width=0)
            button.pack(side="left")
            self.link_buttons[label] = button
        self.about_button = ttk.Button(self.footer, text="About", command=self.show_about)
        self.about_button.pack(side="right", padx=4)

    def open_link(self, url):
        if not url:
            return
        try:
            if webbrowser.open(url, new=2):
                return
        except (OSError, webbrowser.Error):
            pass
        messagebox.showinfo("Open in your browser", f"Open this address in your browser:\n{url}", parent=self.root)

    def show_about(self):
        messagebox.showinfo("About BinauraWave Audio Asset Namer",
                            f"BinauraWave Audio Asset Namer\nVersion {VERSION}\n\n"
                            "Free audio organisation utility\nDeveloped by BinauraWave\n"
                            f"Website: binaurawave.com\n\n{LOCAL_FILES_NOTE}", parent=self.root)

    def fit_workspace(self, event):
        if event.widget == self.root:
            # Keep the existing pane sizes at the default window height. On
            # shorter desktops, lower requested heights so every pane, the copy
            # button and the reserved footer remain visible; scrolling is retained.
            compact = event.height < 800
            self.tree.configure(height=4 if compact else 9)
            for widget, height in ((self.original, 4), (self.spoken, 3), (self.log, 4)):
                widget.configure(height=2 if compact else height)

    def text_area(self, parent, label, height):
        ttk.Label(parent, text=label).pack(anchor="w")
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=3)
        text = tk.Text(frame, height=height, wrap="word", state="disabled",
                       background=COLORS["field"], foreground=COLORS["text"],
                       insertbackground=COLORS["text"], selectbackground=COLORS["selection"],
                       selectforeground=COLORS["text"], inactiveselectbackground=COLORS["selection"],
                       relief="flat", borderwidth=0, highlightthickness=1,
                       highlightbackground=COLORS["border"], highlightcolor=COLORS["gold"])
        bar = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        return text

    @staticmethod
    def set_text(widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def choose_folder(self):
        if not self.busy:
            value = filedialog.askdirectory(parent=self.root)
            if value:
                self.folder.set(value)

    def choose_script(self):
        if not self.busy:
            value = filedialog.askopenfilename(parent=self.root, filetypes=[("Text scripts", "*.txt")])
            if value:
                self.script.set(value)

    def load(self):
        if self.busy:
            return
        self.plan, self.selected = None, None
        self.copy_button.configure(state="disabled")
        self.tree.delete(*self.tree.get_children())
        self.title.set("")
        for widget in (self.original, self.spoken, self.log):
            self.set_text(widget, "")
        try:
            if not self.folder.get() or not self.script.get():
                raise ValueError("Select both an audio folder and a script.")
            self.plan = load_plan(self.folder.get(), self.script.get())
        except (OSError, ValueError) as exc:
            self.status.configure(text=str(exc))
            messagebox.showerror("Cannot prepare preview", str(exc), parent=self.root)
            return
        for index, clip in enumerate(self.plan.clips):
            self.tree.insert("", "end", iid=str(index), values=(clip.number, clip.source.name, clip.title, filename(clip)))
        ignored = ", ".join(self.plan.ignored) or "none"
        self.status.configure(text=f"{len(self.plan.clips)} matched paragraphs. Ignored unnumbered MP3s: {ignored}. Review every title and mapping.")
        self.tree.selection_set("0")
        self.copy_button.configure(state="normal")

    def select(self, event=None):
        selection = self.tree.selection()
        if not selection or not self.plan:
            return
        self.selected = int(selection[0])
        clip = self.plan.clips[self.selected]
        self.title.set(clip.title)
        self.set_text(self.original, clip.original)
        self.set_text(self.spoken, clip.spoken)

    def edit(self, *args):
        if self.selected is not None and self.plan and not self.busy:
            clip = self.plan.clips[self.selected]
            clip.title = self.title.get()
            self.tree.item(str(self.selected), values=(clip.number, clip.source.name, clip.title, filename(clip)))

    def existing_output_choice(self, destination):
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose where to save")
        dialog.configure(background=COLORS["background"])
        dialog.transient(self.root)
        dialog.resizable(False, False)
        choice = [None]

        def finish(value=None):
            choice[0] = value
            dialog.destroy()

        content = ttk.Frame(dialog, padding=18)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="This output folder already exists.", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(content, text=str(destination), wraplength=650).pack(anchor="w", pady=(8, 10))
        ttk.Label(content, text="Choose another folder to keep everything as it is, or replace only the exports we can safely identify. Replacement needs another confirmation.", wraplength=650).pack(anchor="w")
        buttons = ttk.Frame(content)
        buttons.pack(fill="x", pady=(16, 0))
        choose = ttk.Button(buttons, text="Choose another folder", command=lambda: finish("choose"))
        choose.pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Replace existing exports", command=lambda: finish("replace")).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Cancel", command=finish).pack(side="left")
        dialog.protocol("WM_DELETE_WINDOW", finish)
        dialog.bind("<Escape>", lambda event: finish())
        for button in buttons.winfo_children():
            button.bind("<Return>", lambda event, target=button: (target.invoke(), "break")[1])
        dialog.bind("<Return>", lambda event: (choose.invoke(), "break")[1])
        dialog.update_idletasks()
        dialog.geometry(f"+{self.root.winfo_rootx() + 40}+{self.root.winfo_rooty() + 80}")
        dialog.grab_set()
        choose.focus_force()  # Safe default; Enter never selects replacement by default.
        dialog.after_idle(lambda: apply_window_branding(dialog))
        self.root.wait_window(dialog)
        return choice[0]

    def choose_export_request(self):
        destination, replace = None, False
        default = self.plan.folder / "Named"
        if exists(default):
            choice = self.existing_output_choice(default)
            if choice == "choose":
                destination = filedialog.askdirectory(parent=self.root, title="Choose an output folder", mustexist=True)
                if not destination:
                    return None
            elif choice == "replace":
                replace = True
            else:
                return None
        request = prepare_export(self.plan, destination, replace=replace)
        if request.replace:
            title = "Replace these exports?"
            message = (f"Save {len(self.plan.clips)} clips and their manifest here:\n{request.destination}\n\n"
                       "Only recognised exports from this session will be replaced. Unrelated files and original recordings will be kept. Previous exports will be saved in a backup folder.\n\nContinue with replacement?")
        else:
            title = "Confirm copy"
            message = (f"Copy {len(self.plan.clips)} files and a CSV to:\n{request.destination}\n\n"
                       "Original MP3s and script are retained. Existing files will not be overwritten.")
        if not messagebox.askokcancel(title, message, parent=self.root, default="cancel",
                                      icon="warning" if request.replace else "question"):
            return None
        return request

    def copy(self):
        if self.busy or not self.plan:
            return
        try:
            validate_titles(self.plan.clips)
        except ValueError as exc:
            messagebox.showerror("Edit titles before copying", str(exc), parent=self.root)
            return
        try:
            request = self.choose_export_request()
        except (OSError, ValueError) as exc:
            self.status.configure(text=str(exc))
            messagebox.showinfo("Choose an output destination", str(exc), parent=self.root)
            return
        if request is None:
            self.status.configure(text="Export cancelled. No files changed.")
            return
        self.output_request = request
        self.busy = True
        self.editor.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.set_text(self.log, "")
        self.status.configure(text=f"Copying to {self.output_request.destination}… Please keep this window open.")
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        try:
            results = export_plan(self.plan, lambda *result: self.events.put(("result", result)), request=self.output_request)
            self.events.put(("done", all(ok for _, ok, _ in results)))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "result":
                    name, ok, detail = value
                    self.log.configure(state="normal")
                    self.log.insert("end", f"{'OK' if ok else 'FAILED'}: {name} — {detail}\n")
                    self.log.see("end")
                    self.log.configure(state="disabled")
                else:
                    self.busy = False
                    self.editor.configure(state="normal")
                    self.copy_button.configure(state="normal")
                    if kind == "error":
                        self.status.configure(text="Copy failed: " + value)
                        messagebox.showerror("Copy failed", value, parent=self.root)
                    else:
                        self.status.configure(text=("Completed successfully. " if value else "Completed with failures; inspect the per-file results. ") + f"Output folder: {self.output_request.destination}")
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Copy in progress", "Wait for per-file results before closing.", parent=self.root)
        else:
            self.root.destroy()


if __name__ == "__main__":
    set_app_id()
    root = tk.Tk()
    App(root)
    root.mainloop()
