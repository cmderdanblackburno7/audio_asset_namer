"""Local, standard Tk/ttk presentation only; no application behavior."""
from tkinter import ttk

COLORS = {
    "background": "#0c1420",
    "surface": "#142131",
    "field": "#101c2a",
    "border": "#34465b",
    "text": "#e5ebf2",
    "muted": "#acb9c9",
    "gold": "#d6a95f",
    "gold_hover": "#e8bf7d",
    "hover": "#25384d",
    "pressed": "#1b2b3d",
    "selection": "#36516d",
    "disabled": "#8d9bad",
}


def apply_theme(root):
    c = COLORS
    root.configure(background=c["background"])
    style = ttk.Style(root)
    # Windows' native ttk themes ignore many colour options. Clam is included
    # with Tk and lets all workspace controls share the same portable palette.
    style.theme_use("clam")
    style.configure(".", background=c["background"], foreground=c["text"],
                    font=("Segoe UI", 9), bordercolor=c["border"],
                    lightcolor=c["border"], darkcolor=c["border"],
                    troughcolor=c["field"], selectbackground=c["selection"],
                    selectforeground=c["text"], focuscolor=c["gold"])
    style.configure("TFrame", background=c["background"])
    style.configure("TLabel", background=c["background"], foreground=c["text"])
    style.configure("Muted.TLabel", foreground=c["muted"])
    style.configure("TButton", background=c["surface"], foreground=c["text"],
                    padding=(8, 2), borderwidth=1, relief="flat", focusthickness=1,
                    focuscolor=c["gold"], lightcolor=c["surface"], darkcolor=c["surface"])
    style.map("TButton",
              background=[("disabled", c["surface"]), ("pressed", c["pressed"]), ("active", c["hover"])],
              foreground=[("disabled", c["disabled"])],
              bordercolor=[("focus", c["gold"]), ("active", c["muted"])],
              lightcolor=[("active", c["hover"])], darkcolor=[("active", c["hover"])])
    style.configure("Primary.TButton", background=c["gold"], foreground=c["background"],
                    lightcolor=c["gold"], darkcolor=c["gold"], bordercolor=c["gold"],
                    focuscolor=c["background"])
    style.map("Primary.TButton",
              background=[("disabled", c["surface"]), ("pressed", c["gold"]), ("active", c["gold_hover"])],
              foreground=[("disabled", c["disabled"]), ("!disabled", c["background"])],
              bordercolor=[("focus", c["text"]), ("disabled", c["border"]), ("!disabled", c["gold"])],
              lightcolor=[("disabled", c["surface"]), ("active", c["gold_hover"])],
              darkcolor=[("disabled", c["surface"]), ("active", c["gold_hover"])])
    style.configure("Link.TButton", background=c["background"], foreground=c["gold"],
                    padding=(6, 2), bordercolor=c["background"],
                    lightcolor=c["background"], darkcolor=c["background"])
    style.map("Link.TButton",
              background=[("disabled", c["background"]), ("pressed", c["pressed"]), ("active", c["surface"])],
              foreground=[("disabled", c["disabled"]), ("active", c["gold_hover"])],
              bordercolor=[("focus", c["gold"]), ("!focus", c["background"])],
              lightcolor=[("active", c["surface"])], darkcolor=[("active", c["surface"])])
    style.configure("TEntry", fieldbackground=c["field"], foreground=c["text"],
                    insertcolor=c["text"], padding=(5, 2), borderwidth=1,
                    lightcolor=c["field"], darkcolor=c["field"])
    style.map("TEntry", fieldbackground=[("disabled", c["surface"]), ("readonly", c["field"])],
              foreground=[("disabled", c["muted"])], bordercolor=[("focus", c["gold"])],
              lightcolor=[("focus", c["gold"])], darkcolor=[("focus", c["gold"])])
    style.configure("Treeview", background=c["field"], fieldbackground=c["field"],
                    foreground=c["text"], rowheight=20, borderwidth=1,
                    lightcolor=c["border"], darkcolor=c["border"])
    style.map("Treeview", background=[("selected", c["selection"])],
              foreground=[("selected", c["text"])], bordercolor=[("focus", c["gold"])])
    style.configure("Treeview.Heading", background=c["surface"], foreground=c["muted"],
                    padding=(5, 3), relief="flat", borderwidth=1,
                    lightcolor=c["surface"], darkcolor=c["surface"])
    style.map("Treeview.Heading", background=[("active", c["hover"])], foreground=[("active", c["text"])])
    for name in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
        style.configure(name, background=c["border"], troughcolor=c["field"],
                        arrowcolor=c["muted"], bordercolor=c["field"],
                        lightcolor=c["border"], darkcolor=c["border"], relief="flat", borderwidth=0)
        style.map(name, background=[("active", c["hover"]), ("pressed", c["selection"])])
    return style
