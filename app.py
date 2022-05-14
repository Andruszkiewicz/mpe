from dataclasses import fields
from typing import List

from config import get_mpe_config, MPEConfig, update_mpe_config
import tkinter as tk

from simulation import run_simulation


def on_click_run_simulation(entries: List[tk.Entry]):
    mpe_config = get_mpe_config()
    mpe_config = update_mpe_config(entries, mpe_config)
    run_simulation(mpe_config)


ROOT = tk.Tk()
ROOT.title("Multiagent simultation")

label = tk.Label(ROOT, text="Insert configuration: ")
label.grid(row=0, column=1)

entries = [tk.Entry(ROOT, textvariable=field.name) for field in fields(MPEConfig)]
labels = [tk.Label(ROOT, text=field.name) for field in fields(MPEConfig)]

row_count = 1

for entry, label in zip(entries, labels):
    label.grid(row=row_count, column=0)
    entry.grid(row=row_count, column=1)
    row_count += 1


button = tk.Button(
    ROOT, text="Run simulation", command=lambda: on_click_run_simulation(entries)
)
button.grid(row=row_count, column=1)

ROOT.mainloop()



