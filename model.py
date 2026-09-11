"""Monthly unit economics model. Run with: python model.py."""

import math
import tkinter as tk
from tkinter import messagebox, ttk


# Calculation layer ---------------------------------------------------------

LIFETIME_CAP = 60.0
INPUT_FIELDS = (
    ("marketing_spend", "Total Sales & Marketing Spend", "$ / month"),
    ("new_customers", "New Customers Acquired", "customers / month"),
    ("revenue", "Revenue", "$ / month"),
    ("paying_users", "Paying Users", "users this month"),
    ("starting_customers", "Customers at Beginning of Period", "customers"),
    ("lost_customers", "Customers Lost During Period", "customers / month"),
    ("gross_margin_percent", "Gross Margin", "% (e.g., 80)"),
)


def calculate_cac(marketing_spend: float, new_customers: float) -> float:
    """Return acquisition cost per new customer."""
    return marketing_spend / new_customers


def calculate_arpu(revenue: float, paying_users: float) -> float:
    """Return monthly revenue per paying user."""
    return revenue / paying_users


def calculate_churn(lost_customers: float, starting_customers: float) -> float:
    """Return monthly churn as a fraction."""
    return lost_customers / starting_customers


def calculate_customer_lifetime(churn: float) -> float:
    """Return expected customer lifetime in months, capped at 60."""
    return min(1.0 / churn, LIFETIME_CAP)


def calculate_ltv(arpu: float, lifetime: float, gross_margin: float) -> float:
    """Return lifetime gross profit per customer using modeled lifetime."""
    return arpu * lifetime * gross_margin


def calculate_ltv_cac_ratio(ltv: float, cac: float) -> float:
    """Return lifetime value divided by acquisition cost."""
    return ltv / cac


def calculate_payback_period(cac: float, arpu: float, gross_margin: float) -> float:
    """Return months needed for gross profit to recover acquisition cost."""
    return cac / (arpu * gross_margin)


def calculate_contribution_margin(
    arpu: float, gross_margin: float, cac: float, lifetime: float
) -> float:
    """Return monthly gross profit less acquisition cost amortization."""
    # Current model assumption, pending clarification from the professor:
    # amortize CAC across customer lifetime, not the payback period.
    return (arpu * gross_margin) - (cac / lifetime)


def validate_inputs(raw_inputs: dict) -> dict:
    """Parse finite numeric inputs and reject invalid model denominators."""
    values = {}
    for key, label, _unit in INPUT_FIELDS:
        try:
            value = float(raw_inputs[key])
        except (ValueError, TypeError, KeyError):
            raise ValueError(f"{label} must be numeric.") from None
        if not math.isfinite(value):
            raise ValueError(f"{label} must be a finite number.")
        if value < 0:
            raise ValueError(f"{label} cannot be negative.")
        values[key] = value

    positive_fields = (
        ("new_customers", "New Customers Acquired must be greater than zero."),
        ("paying_users", "Paying Users must be greater than zero."),
        ("starting_customers", "Starting Customers must be greater than zero."),
        ("lost_customers", "Customers Lost must be greater than zero; zero churn "
         "makes the lifetime calculation undefined."),
        ("marketing_spend", "Sales & Marketing Spend must be greater than zero; "
         "zero CAC makes LTV:CAC undefined."),
        ("revenue", "Revenue must be greater than zero; zero ARPU makes "
         "CAC payback undefined."),
    )
    for key, explanation in positive_fields:
        if values[key] == 0:
            raise ValueError(explanation)
    if not 0 < values["gross_margin_percent"] <= 100:
        raise ValueError("Gross Margin must be greater than 0 and at most 100%.")
    if values["lost_customers"] > values["starting_customers"]:
        raise ValueError("Customers Lost cannot exceed Starting Customers.")
    return values


def run_model(
    marketing_spend: float,
    new_customers: float,
    revenue: float,
    paying_users: float,
    starting_customers: float,
    lost_customers: float,
    gross_margin_percent: float,
) -> dict:
    """Calculate all outputs from validated monthly inputs in one place."""
    gross_margin = gross_margin_percent / 100.0
    cac = calculate_cac(marketing_spend, new_customers)
    arpu = calculate_arpu(revenue, paying_users)
    churn = calculate_churn(lost_customers, starting_customers)
    lifetime = calculate_customer_lifetime(churn)
    ltv = calculate_ltv(arpu, lifetime, gross_margin)
    results = {
        "cac": cac,
        "arpu": arpu,
        "churn": churn,
        "lifetime": lifetime,
        "ltv": ltv,
        "ratio": calculate_ltv_cac_ratio(ltv, cac),
        "payback": calculate_payback_period(cac, arpu, gross_margin),
        "contribution": calculate_contribution_margin(
            arpu, gross_margin, cac, lifetime
        ),
    }
    if not all(math.isfinite(value) for value in results.values()):
        raise ValueError("Inputs are too large or small for reliable calculations.")
    results["lifetime_capped"] = churn < 1.0 / LIFETIME_CAP
    # Chart data belongs to the model layer, so charts only render results.
    results["monthly_gross_profit"] = arpu * gross_margin
    results["timeline_months"] = [0.0, lifetime]
    results["cumulative_gross_profit"] = [0.0, ltv]
    results["payback_within_lifetime"] = (
        results["payback"] <= lifetime
        or math.isclose(results["payback"], lifetime, rel_tol=1e-12)
    )
    ratio = results["ratio"]
    # Ignore floating-point roundoff at the course's category boundaries.
    if ratio < 1 and not math.isclose(ratio, 1, rel_tol=1e-12):
        results["health"] = "Value Destructive"
    elif ratio < 3 and not math.isclose(ratio, 3, rel_tol=1e-12):
        results["health"] = "Growing, Not Earning"
    elif ratio <= 5 or math.isclose(ratio, 5, rel_tol=1e-12):
        results["health"] = "Healthy"
    else:
        results["health"] = "Potentially Underinvesting in Growth"
    return results


# Visualization layer -------------------------------------------------------

def draw_timeline(ax, results: dict | None) -> None:
    """Render model-provided gross profit, investment, and time markers."""
    ax.clear()
    ax.set_title("Customer Economics Timeline", loc="left", weight="bold")
    if results is None:
        ax.text(0.5, 0.5, "Calculate the model to view the timeline",
                ha="center", va="center", transform=ax.transAxes, color="#64748b")
        ax.set_axis_off()
        return
    ax.set_axis_on()
    lifetime = results["lifetime"]
    cac = results["cac"]
    ax.plot(results["timeline_months"], results["cumulative_gross_profit"],
            color="#007a63", linewidth=2.5, label="Cumulative gross profit")
    ax.axhline(cac, color="#b7791f", linestyle="--", label="CAC investment")
    ax.scatter([0], [cac], color="#b7791f", zorder=4)
    ax.annotate("Acquisition · Month 0", (0, cac), xytext=(8, 8),
                textcoords="offset points", fontsize=8)
    ax.axvline(lifetime, color="#334155", linestyle=":")
    ax.annotate(f"Customer Lifetime\n{lifetime:.1f} months"
                + (" (capped)" if results["lifetime_capped"] else ""),
                xy=(lifetime, 0.98), xycoords=("data", "axes fraction"),
                ha="right", va="top", fontsize=8,
                bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"})
    if results["payback_within_lifetime"]:
        payback = results["payback"]
        ax.vlines(payback, 0, cac, color="#2563eb", linestyle="--")
        ax.scatter([payback], [cac], color="#2563eb", zorder=5)
        ax.annotate(f"CAC Payback Point\n{payback:.1f} months", (payback, cac),
                    xytext=(0, 16), textcoords="offset points", ha="center",
                    fontsize=8, color="#1d4ed8",
                    bbox={"facecolor": "white", "alpha": 0.85,
                          "edgecolor": "none"})
    else:
        ax.text(0.03, 0.65,
                f"CAC Payback Point: {results['payback']:.1f} months\n"
                "Beyond modeled customer lifetime; CAC is not recovered.",
                transform=ax.transAxes, fontsize=8, color="#9f1239",
                bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "none"})
    ax.set_xlim(-lifetime * 0.03, lifetime * 1.08)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Months since acquisition", fontsize=9)
    ax.set_ylabel("Gross profit / customer ($)", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(axis="y", alpha=0.15)
    ax.legend(loc="upper left", fontsize=7, frameon=False)
    ax.text(0, -0.37,
            f"Monthly gross profit: ${results['monthly_gross_profit']:,.2f}"
            " / customer (ARPU × gross margin)",
            transform=ax.transAxes, fontsize=8, color="#475569")


def draw_health(ax, results: dict | None) -> None:
    """Render a fixed course health scale with an explicit overflow marker."""
    ax.clear()
    ax.set_title("LTV:CAC Health", loc="left", weight="bold", pad=24)
    for start, width, color in (
        (0, 1, "#fca5a5"), (1, 2, "#fde68a"),
        (3, 2, "#6ee7b7"), (5, 1, "#93c5fd"),
    ):
        ax.barh(0, width, left=start, height=0.35, color=color)
    ax.set_xlim(0, 6)
    ax.set_ylim(-0.4, 0.65)
    ax.set_yticks([])
    ax.set_xticks([0, 1, 3, 5, 6], ["0×", "1×", "3×", "5×", ">5×"])
    ax.tick_params(axis="x", length=0, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    if results is not None:
        position = min(results["ratio"], 5.85)
        ax.plot(position, 0.3, marker="v", color="#0f172a", markersize=9)
        ax.text(0, 1.02, f"{results['ratio']:.2f}× · {results['health']}",
                transform=ax.transAxes, fontsize=10, weight="bold")
    else:
        ax.text(0, 1.02, "Calculate the model to mark its current ratio",
                transform=ax.transAxes, fontsize=9, color="#64748b")
    ax.text(0, -0.65,
            "<1×  Value Destructive     |     1–<3×  Growing, Not Earning\n"
            "3–5×  Healthy     |     >5×  Potentially Underinvesting in Growth",
            transform=ax.transAxes, fontsize=8, linespacing=1.6)


# GUI / controller layer ----------------------------------------------------

class UnitEconomicsApp:
    """Manage input widgets, calculated KPI text, and embedded figures."""

    def __init__(self, root, figure_class, canvas_class):
        self.root = root
        self.results = None
        self.entries = {}
        self.output_vars = {}
        root.title("Digital Business Unit Economics Model")
        root.geometry("1240x920")
        root.minsize(1060, 900)
        root.configure(background="#f1f5f9")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f1f5f9")
        style.configure("TLabel", background="#f1f5f9", foreground="#0f172a",
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"),
                        foreground="#007a63")
        style.configure("Card.TFrame", background="white")
        style.configure("Card.TLabel", background="white", font=("Segoe UI", 9))
        style.configure("Value.TLabel", background="white",
                        font=("Segoe UI", 12, "bold"), foreground="#005c4b")
        style.configure("TButton", padding=9, font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=6)

        container = ttk.Frame(root, padding=20)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text="Digital Business Unit Economics Model",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(container, text="USF · Digital Business Models · Group 12"
                  "    |    Monthly model").pack(anchor="w", pady=(4, 18))
        body = ttk.Frame(container)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        left = ttk.Frame(body, width=320)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 24))
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        ttk.Label(left, text="MODEL INPUTS", style="Section.TLabel").pack(anchor="w")
        for key, label, unit in INPUT_FIELDS:
            ttk.Label(left, text=label).pack(anchor="w", pady=(12, 2))
            row = ttk.Frame(left)
            row.pack(fill="x")
            entry = ttk.Entry(row, width=18)
            entry.pack(side="left")
            ttk.Label(row, text=unit, font=("Segoe UI", 9)).pack(side="left", padx=8)
            self.entries[key] = entry
        buttons = ttk.Frame(left)
        buttons.pack(fill="x", pady=18)
        ttk.Button(buttons, text="CALCULATE MODEL", command=self.calculate).pack(
            side="left", padx=(0, 8))
        ttk.Button(buttons, text="CLEAR", command=self.clear).pack(side="left")
        ttk.Label(left, text="MODEL ASSUMPTIONS", style="Section.TLabel").pack(
            anchor="w", pady=(8, 6))
        ttk.Label(left, text=(
            "• Model uses monthly units throughout.\n\n"
            "• Lifetime is calculated from churn and capped at 60 months.\n\n"
            "• Contribution margin currently amortizes CAC across customer "
            "lifetime.\n\n"
            "• Simplified model: excludes discount rates, expansion revenue, "
            "taxes, financing costs, and other full financial-statement effects."
        ), wraplength=310, font=("Segoe UI", 9), justify="left").pack(anchor="w")

        ttk.Label(right, text="MODEL OUTPUTS", style="Section.TLabel").pack(anchor="w")
        groups = (
            ("Customer Economics", (("cac", "Customer Acquisition Cost"),
             ("arpu", "Average Revenue Per User"), ("churn", "Monthly Churn Rate"),
             ("lifetime", "Customer Lifetime"))),
            ("Customer Value", (("ltv", "Lifetime Value"), ("ratio", "LTV:CAC Ratio"))),
            ("Recovery & Contribution", (("payback", "CAC Payback Period"),
             ("contribution", "Contribution Margin"))),
        )
        for title, fields in groups:
            ttk.Label(right, text=title, font=("Segoe UI", 10, "bold")).pack(
                anchor="w", pady=(8, 3))
            group = ttk.Frame(right)
            group.pack(fill="x")
            group.columnconfigure((0, 1), weight=1, uniform="kpi")
            for index, (key, label) in enumerate(fields):
                card = ttk.Frame(group, style="Card.TFrame", padding=(10, 5))
                card.grid(row=index // 2, column=index % 2,
                          sticky="nsew", padx=2, pady=2)
                ttk.Label(card, text=label, style="Card.TLabel").pack(anchor="w")
                variable = tk.StringVar(master=root, value="—")
                ttk.Label(card, textvariable=variable,
                          style="Value.TLabel").pack(anchor="w")
                self.output_vars[key] = variable

        self.figure = figure_class(figsize=(7.6, 4.3), dpi=100, facecolor="white")
        self.timeline_ax = self.figure.add_axes((0.11, 0.53, 0.86, 0.38))
        self.health_ax = self.figure.add_axes((0.11, 0.13, 0.86, 0.14))
        self.chart_canvas = canvas_class(self.figure, master=right)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, pady=(12, 0))
        self.redraw(None)
        root.bind("<Return>", lambda _event: self.calculate())
        self.entries["marketing_spend"].focus_set()

    def redraw(self, results: dict | None) -> None:
        """Redraw both charts using the same model result dictionary."""
        draw_timeline(self.timeline_ax, results)
        draw_health(self.health_ax, results)
        self.chart_canvas.draw()

    def calculate(self) -> None:
        """Validate and calculate before committing any displayed changes."""
        try:
            inputs = validate_inputs({
                key: entry.get() for key, entry in self.entries.items()
            })
            results = run_model(**inputs)
            displays = {
                "cac": f"${results['cac']:,.2f} / customer",
                "arpu": f"${results['arpu']:,.2f} / month",
                "churn": f"{results['churn']:.2%} / month",
                "lifetime": f"{results['lifetime']:.1f} months"
                + (" (capped)" if results["lifetime_capped"] else ""),
                "ltv": f"${results['ltv']:,.2f} / customer",
                "ratio": f"{results['ratio']:.2f}×",
                "payback": f"{results['payback']:.1f} months",
                "contribution": f"${results['contribution']:,.2f} / customer / month",
            }
        except ValueError as error:
            messagebox.showerror("Invalid model inputs", str(error), parent=self.root)
            return
        except Exception:
            messagebox.showerror(
                "Calculation error", "The model could not calculate these inputs. "
                "Check that the values are within a reasonable numeric range.",
                parent=self.root,
            )
            return
        try:
            self.redraw(results)
        except Exception:
            self.redraw(self.results)
            messagebox.showerror("Chart error", "The charts could not be updated. "
                                 "Previous results were retained.", parent=self.root)
            return
        for key, text in displays.items():
            self.output_vars[key].set(text)
        self.results = results

    def clear(self) -> None:
        """Reset inputs, KPIs, and visualizations without closing the app."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        for variable in self.output_vars.values():
            variable.set("—")
        self.results = None
        self.redraw(None)
        self.entries["marketing_spend"].focus_set()


def main() -> None:
    """Check the optional installation before starting the desktop GUI."""
    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
    except ImportError:
        explanation = ("Matplotlib is required to run this application.\n\n"
                       "Install it using: pip install matplotlib")
        print(explanation)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Missing dependency", explanation, parent=root)
            root.destroy()
        except tk.TclError:
            pass  # The console message remains available without a display.
        return
    root = tk.Tk()
    UnitEconomicsApp(root, Figure, FigureCanvasTkAgg)
    root.mainloop()


if __name__ == "__main__":
    main()
