import tkinter as tk
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
ALLOWED = {"__builtins__": None,
           "sin": np.sin, "cos": np.cos, "tan": np.tan,
           "exp": np.exp, "log": np.log, "sqrt": np.sqrt,
           "pi": np.pi, "e": np.e, "abs": np.abs, "np": np}
def make_mult_explicit(text):
    """
    Turn common implicit multiplication into explicit form:
    2x  -> 2*x
    2(x) -> 2*(x)
    x2  -> x*2
    (x)(x) -> (x)*(x)
    Also converts ^ to ** for powers.
    """
    s = text.replace("^", "**")
    s = s.replace(")(", ")*(")
    s = re.sub(r'(\d)\s*\(', r'\1*(', s)            
    s = re.sub(r'(\d)\s*(x\b)', r'\1*\2', s, flags=re.I)  
    s = re.sub(r'(\bx)\s*(\d)', r'\1*\2', s, flags=re.I)  
    s = re.sub(r'(\bx)\s*(\()', r'\1*\2', s, flags=re.I)  
    s = re.sub(r'(\))\s*(x\b)', r'\1*\2', s, flags=re.I)  
    s = re.sub(r'\s+', '', s)  
    return s
def remove_spikes(values, jump_limit=50, clamp=1e3):
    """
    Replace very large / jumping values with NaN so matplotlib won't draw
    lines across vertical asymptotes (like for tan).
    """
    y = np.asarray(values, dtype=float)
    y[~np.isfinite(y)] = np.nan
    y[np.abs(y) > clamp] = np.nan
    diffs = np.abs(np.diff(y))
    big_jumps = np.where(diffs > jump_limit)[0]
    for i in big_jumps:
        y[i] = np.nan
        y[i+1] = np.nan
    return y
def draw_graph():
    expr_text = expr_input.get().strip()
    if not expr_text:
        status.set("Please type an expression first.")
        return

    expr = make_mult_explicit(expr_text)

    try:
        start = float(from_input.get()); end = float(to_input.get())
        samples = int(samples_input.get())
        xdeg = np.linspace(start, end, samples)
    except Exception as e:
        status.set("Range error: " + str(e))
        return

    if re.search(r'\b(sin|cos|tan)\b', expr, flags=re.I):
        x_for_eval = np.radians(xdeg)
        xlabel = "x (degrees)"
    else:
        x_for_eval = xdeg
        xlabel = "x"

    try:
        yvals = eval(expr, ALLOWED, {"x": x_for_eval, "np": np})
        yvals = np.asarray(yvals)
    except Exception as e:
        status.set("Evaluation error: " + str(e))
        return

    yvals = remove_spikes(yvals, jump_limit=50, clamp=1e3)

    ax.clear()
    ax.grid(True)
    ax.plot(xdeg, yvals, color="green", linewidth=1.6, label=expr_text)
    ax.set_xlabel(xlabel)

    finite = yvals[np.isfinite(yvals)]
    if finite.size:
        low, high = np.percentile(finite, [1, 99])
        if high - low > 0:
            margin = 0.2 * max(1.0, (high - low))
            ax.set_ylim(low - margin, high + margin)

    ax.legend()
    canvas.draw()
    status.set("Plotted")
root = tk.Tk()
root.title("Equation Visualiser")

panel = tk.Frame(root)
panel.pack(padx=8, pady=8)

tk.Label(panel, text="y =").grid(row=0, column=0)
expr_input = tk.Entry(panel, width=30)
expr_input.grid(row=0, column=1, columnspan=3)
expr_input.insert(0, "tan(x)")

tk.Label(panel, text="from").grid(row=1, column=0)
from_input = tk.Entry(panel, width=8); from_input.grid(row=1, column=1); from_input.insert(0, "0")
tk.Label(panel, text="to").grid(row=1, column=2)
to_input = tk.Entry(panel, width=8); to_input.grid(row=1, column=3); to_input.insert(0, "360")

tk.Label(panel, text="samples").grid(row=2, column=0)
samples_input = tk.Entry(panel, width=8); samples_input.grid(row=2, column=1); samples_input.insert(0, "800")

plot_btn = tk.Button(panel, text="Plot", command=draw_graph)
plot_btn.grid(row=2, column=2, columnspan=2, sticky="ew")

status = tk.StringVar(); status.set("Ready")
tk.Label(root, textvariable=status).pack()

fig, ax = plt.subplots(figsize=(6,4))
ax.grid(True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

root.mainloop()
