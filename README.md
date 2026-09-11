# Digital Business Unit Economics Model

A lightweight Python desktop application for modeling and visualizing the unit economics of a digital business.

Built for **USF · Digital Business Models · Group 12** as part of the Week 3 Unit Economics Model project.

---

## What This Project Does

The model answers a simple question:

> **Does the economics of acquiring and retaining a customer actually work?**

Seven raw business inputs are entered into the application. The model calculates eight unit-economics metrics and visualizes the relationship between customer acquisition cost, gross profit, CAC payback, customer lifetime, and lifetime value.

The application is designed as a **decision model**, not just a calculator. Changing an input automatically propagates through every dependent calculation and visualization.

---

## Model Inputs

The model uses seven monthly inputs:

| Input | Description |
|---|---|
| Sales & Marketing Spend | Monthly cost associated with acquiring customers |
| New Customers Acquired | Customers acquired during the period |
| Revenue | Monthly revenue |
| Paying Users | Revenue-generating users during the period |
| Customers at Beginning of Period | Customer population used to calculate churn |
| Customers Lost During Period | Customers lost during the month |
| Gross Margin | Percentage of revenue remaining after direct delivery costs |

All inputs are validated before calculations are performed.

---

## Model Outputs

The application calculates eight required unit-economics metrics:

| Metric | Calculation |
|---|---|
| **Customer Acquisition Cost (CAC)** | Sales & Marketing Spend ÷ New Customers |
| **Average Revenue Per User (ARPU)** | Revenue ÷ Paying Users |
| **Monthly Churn Rate** | Customers Lost ÷ Starting Customers |
| **Customer Lifetime** | 1 ÷ Monthly Churn |
| **Lifetime Value (LTV)** | ARPU × Customer Lifetime × Gross Margin |
| **LTV:CAC Ratio** | LTV ÷ CAC |
| **CAC Payback Period** | CAC ÷ Monthly Gross Profit |
| **Contribution Margin** | Monthly Gross Profit − Monthly CAC Allocation |

Customer lifetime is capped at **60 months** to prevent unrealistically large LTV values at very low churn rates.

---

## How the Model Works

The model was designed by working backward from the required outputs.

```text
RAW BUSINESS DATA
       │
       ▼
CORE UNIT METRICS
CAC · ARPU · Churn
       │
       ▼
DERIVED ECONOMICS
Lifetime · Gross Profit
       │
       ▼
DECISION METRICS
LTV · LTV:CAC · Payback · Contribution Margin
       │
       ▼
VISUAL INTERPRETATION
Customer Economics Timeline · LTV:CAC Health
```

Each financial metric is implemented as an independent Python function. A central model runner orchestrates those functions and returns a single result set used by both the GUI and visualizations.

This keeps the financial logic separate from the presentation layer and makes individual formulas easy to audit, test, or modify.

---

## Visualizations

### Customer Economics Timeline

The timeline shows the economic relationship between:

- Initial customer acquisition cost
- Monthly gross profit
- CAC payback point
- Customer lifetime
- Cumulative lifetime gross profit

This makes the distinction between **CAC payback period** and **customer lifetime** immediately visible.

### LTV:CAC Health

The model also interprets the LTV:CAC ratio using the course framework:

| LTV:CAC | Interpretation |
|---:|---|
| `< 1×` | Value Destructive |
| `1× – <3×` | Growing, Not Earning |
| `3× – 5×` | Healthy |
| `> 5×` | Potentially Underinvesting in Growth |

---

## Technology

The application intentionally uses a small technology stack:

- **Python** — model and application logic
- **Tkinter** — desktop user interface
- **Matplotlib** — embedded financial visualizations

There is no database, API, web server, or persistent storage.

The entire application lives in a single `model.py` file.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd unit-economics-model
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

The only third-party dependency is Matplotlib.

### 3. Run the model

```bash
python model.py
```

---

## Example Test Case

The following synthetic values can be used to verify the model:

| Input | Value |
|---|---:|
| Sales & Marketing Spend | $24,000 |
| New Customers Acquired | 100 |
| Revenue | $5,000 |
| Paying Users | 100 |
| Starting Customers | 100 |
| Customers Lost | 4.1667 |
| Gross Margin | 80% |

Expected results are approximately:

```text
CAC                  $240.00
ARPU                  $50.00
Monthly Churn           4.17%
Customer Lifetime      24.0 months
LTV                   $960.00
LTV:CAC                  4.00×
CAC Payback              6.0 months
Contribution Margin     $30.00 / customer / month
```

These values are **synthetic test data** and are not sourced company data.

---

## Model Assumptions

This is intentionally a simplified unit-economics model.

Current assumptions include:

- All calculations use monthly units.
- Customer lifetime is derived from monthly churn.
- Customer lifetime is capped at 60 months.
- Gross margin is applied to ARPU when calculating customer gross profit.
- The model does not currently include discount rates.
- Expansion revenue and net dollar retention are not modeled.
- Taxes, financing costs, and full financial-statement effects are outside the model's scope.

### Contribution Margin

The current implementation calculates contribution margin as:

```text
Monthly Gross Profit − (CAC ÷ Customer Lifetime)
```

This treats customer acquisition cost as amortized across the modeled customer lifetime.

The Week 3 project instructions currently describe CAC as being amortized across the **CAC payback period**. Because CAC payback is itself calculated from monthly gross profit, that interpretation mathematically produces a contribution margin of zero for any valid input.

Clarification has been requested from the course professor. The contribution-margin calculation is intentionally isolated in its own function so the model can be updated without affecting the rest of the architecture.

---

## Data Sourcing

The final project model is intended to use publicly available company data from sources such as:

- SEC 10-K filings
- SEC 10-Q filings
- S-1 filings
- Investor presentations
- Earnings materials
- Other documented public sources permitted by the course

Not every raw model input must be directly reported. Inputs may be **derived from reported data** when the calculation and source can be documented.

The objective is to minimize unsupported assumptions and maintain a traceable evidence path from public data to model input to calculated output.

---

## Development Approach

This project was developed using an **AI-assisted software engineering workflow**.

The process was:

1. Identify the required business outputs.
2. Trace those outputs backward to the necessary raw inputs.
3. Define the mathematical relationships and dependencies.
4. Design the calculation architecture.
5. Design the desktop interface and visualizations.
6. Use OpenAI Codex to implement the specification.
7. Independently calculate test cases.
8. Validate the application's results against expected values.
9. Review and refine the model assumptions.

AI assisted with implementation, but the model architecture, financial relationships, assumptions, testing, and interpretation remain the responsibility of the project team.

---

## Project Structure

```text
unit-economics-model/
│
├── model.py           # Complete model, GUI, and visualization logic
├── requirements.txt   # Python dependency
├── README.md          # Project documentation
└── .gitignore
```

---

## Course

**University of South Florida**  
Digital Business Models  
Week 3 — Unit Economics Model  
**Group 12**

---

### Built to make the economics visible.

Because a model should do more than calculate numbers — it should help explain what those numbers mean.