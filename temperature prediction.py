import sys
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox


def newton_divided_diff(x, y):
    n = len(x)
    coef = np.array(y, dtype=float).copy()
    for j in range(1, n):
        coef[j:n] = (coef[j:n] - coef[j - 1]) / (x[j:n] - x[j - 1])
    return coef

def newton_eval(coef, x_nodes, t):
    p = coef[-1]
    for k in range(len(coef) - 2, -1, -1):
        p = p * (t - x_nodes[k]) + coef[k]
    return float(p)

def bisection(f, a, b, tol=1e-4, maxit=100):
    fa, fb = f(a), f(b)
    if np.sign(fa) == np.sign(fb):
        return None
    for _ in range(maxit):
        c = 0.5 * (a + b)
        fc = f(c)
        if abs(fc) < tol or (b - a) * 0.5 < tol:
            return c
        if np.sign(fa) != np.sign(fc):
            b, fb = c, fc
        else:
            a, fa = c, fc
    return 0.5 * (a + b)

def loocv_mae(x, y):
    n = len(x)
    errs = []
    for k in range(n):
        mask = np.ones(n, dtype=bool)
        mask[k] = False
        coef = newton_divided_diff(x[mask], y[mask])
        pred_k = newton_eval(coef, x[mask], float(x[k]))
        errs.append(abs(pred_k - float(y[k])))
    return float(np.mean(errs))


def get_default_series():
    hours = np.array([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0, 24.0], dtype=float)
    temps = np.array([20.0, 19.5, 22.0, 26.0, 32.0, 36.0, 34.0, 28.0, 22.0], dtype=float)
    return hours, temps


def plot_prediction(hours, temps, predict_fn, t_query, y_query,
                    threshold, crossing_time):
    plt.style.use("seaborn-v0_8-whitegrid")

    t_min, t_max = hours.min(), hours.max()
    T = np.linspace(t_min, t_max, 600)
    Y = [predict_fn(t) for t in T]

    plt.figure(figsize=(9, 5))
    plt.scatter(hours, temps, s=60, c="red", label="Measured Data")
    plt.plot(T, Y, lw=2.5, c="blue", label="Newton Interpolation")

    plt.scatter([t_query], [y_query], c="orange", s=100, edgecolors="black", label="Your Query")
    plt.axhline(threshold, color="green", linestyle="--", label=f"{threshold}°C Threshold")

    if crossing_time is not None:
        plt.scatter([crossing_time], [predict_fn(crossing_time)],
                    c="green", s=90, edgecolors="black", label="Threshold Crossing")

    plt.xlabel("Time (hours)")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Prediction - 24 Hours (Cairo Approx.)")
    plt.legend()
    plt.grid()
    plt.show() 


def run_program():
    try:
        t_query = float(entry_time.get())
        if not (0 <= t_query <= 24):
            messagebox.showerror("Error", "Please enter a time between 0 and 24 hours.")
            return
    except:
        messagebox.showerror("Error", "Please enter a valid number (e.g., 13.5)")
        return

    hours, temps = get_default_series()
    coef = newton_divided_diff(hours, temps)
    predict_fn = lambda t: newton_eval(coef, hours, t)

    y_query = predict_fn(t_query)
    mae = loocv_mae(hours, temps)

    threshold = 35.0 
    f = lambda t: predict_fn(t) - threshold
    crossing_time = bisection(f, hours.min(), hours.max())

    result = (
        f"Query time: {t_query:.2f} h\n"
        f"Predicted temperature: {y_query:.2f} °C\n"
        f"LOOCV MAE: {mae:.3f}\n"
    )

    if crossing_time or y_query > threshold:
        if crossing_time:
            result += f"Crosses {threshold}°C at: {crossing_time:.2f} h"
        else:
            result += f"Your query ({t_query:.2f} h) exceeds {threshold}°C directly."
    else:
        result += "No crossing detected."

    text_output.config(state="normal")
    text_output.delete(1.0, "end")
    text_output.insert("end", result)
    text_output.config(state="disabled")

    plot_prediction(hours, temps, predict_fn, t_query, y_query,
                    threshold, crossing_time)


root = tk.Tk()
root.title("Temperature Predictor 24-h (Cairo Approx.)")
root.geometry("460x380")
root.resizable(False, False)

label = tk.Label(root, text="Enter time (0–24), e.g., 13.5:", font=("Arial", 12))
label.pack(pady=10)
entry_time = tk.Entry(root, font=("Arial", 14), width=10, justify="center")
entry_time.pack(pady=5)

btn = tk.Button(root, text="Predict", font=("Arial", 14), command=run_program)
btn.pack(pady=10)

text_output = tk.Text(root, height=8, width=45, font=("Arial", 11), state="disabled")
text_output.pack(pady=10)

root.mainloop()