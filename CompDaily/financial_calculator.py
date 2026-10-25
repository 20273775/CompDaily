"""
Compound interest / savings growth calculator.

Computes the future value of savings given a starting principal,
an annual interest rate, a compounding frequency, and (optionally)
regular periodic contributions. Includes plotting and table views for
a single scenario, and side-by-side comparison of two scenarios.

SETUP
-----
A virtual environment with the required packages lives in `.venv/`
alongside this script. To use it:

    source .venv/bin/activate
    python3 financial_calculator.py

Or run it directly without activating:

    .venv/bin/python financial_calculator.py

If `.venv/` doesn't exist yet (e.g. on a fresh checkout), recreate it:

    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt

matplotlib is only needed for the plotting functions, not for
future_value() or print_schedule_table() alone.

RUNNING AS A SCRIPT
--------------------
    python3 financial_calculator.py

You'll be prompted to choose:
    1) Single scenario  - enter principal, rate, years, compounding
       frequency, and contribution; prints a summary.
    2) Compare two scenarios - enter inputs for two named scenarios;
       prints a side-by-side table and optionally saves a comparison
       chart (PNG) to a path you provide.

USING AS A LIBRARY
-------------------
Import the functions you need instead of running interactively:

    from financial_calculator import (
        future_value,
        plot_savings_growth,
        print_schedule_table,
        plot_scenario_comparison,
        print_scenario_comparison_table,
    )

    result = future_value(
        principal=5000,
        annual_rate=0.06,       # 6%, as a decimal
        years=10,
        compounds_per_year=12,  # 12 = monthly, 1 = annual, 4 = quarterly
        contribution=200,       # added each compounding period
    )

    print(f"Future value: ${result.future_value:,.2f}")

    print_schedule_table(result, compounds_per_year=12, every_n_periods=12)

    fig = plot_savings_growth(result, compounds_per_year=12)
    fig.savefig("savings_growth.png")  # or `fig` alone to display inline

    # Comparing two scenarios:
    scenario_a = future_value(principal=5000, annual_rate=0.06, years=10,
                               compounds_per_year=12, contribution=200)
    scenario_b = future_value(principal=5000, annual_rate=0.08, years=10,
                               compounds_per_year=12, contribution=150)
    scenarios = {"6% / $200mo": scenario_a, "8% / $150mo": scenario_b}

    print_scenario_comparison_table(scenarios)
    fig = plot_scenario_comparison(scenarios)

NOTES / LIMITATIONS
--------------------
- `annual_rate` is a nominal rate as a decimal (5% -> 0.05), applied
  per compounding period as annual_rate / compounds_per_year.
- Contribution timing: by default contributions are added at the end
  of each period, after that period's interest; pass
  contribution_timing="start" to add them before interest is applied.
- plot_scenario_comparison() and print_schedule_table() assume a
  single shared compounds_per_year across scenarios/periods being
  charted together; mixing frequencies in one comparison will mislabel
  the x-axis/year column.
"""

from dataclasses import dataclass


@dataclass
class SavingsProjection:
    """Result of a compound-interest projection."""

    future_value: float
    total_contributions: float
    total_interest_earned: float
    schedule: list[dict]


def _validate_future_value_inputs(
    principal: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int,
    contribution: float,
    contribution_timing: str,
) -> None:
    """
    Validate future_value() inputs, collecting all problems found and
    raising a single ValueError with a friendly, user-facing message
    listing each one. Raises nothing if inputs are valid.
    """
    errors = []

    if principal < 0:
        errors.append("Starting principal can't be negative.")
    if years <= 0:
        errors.append("Number of years must be greater than 0.")
    if compounds_per_year <= 0:
        errors.append("Compounding periods per year must be greater than 0.")
    if contribution < 0:
        errors.append("Contribution per period can't be negative.")
    if annual_rate < -1:
        errors.append("Annual interest rate can't be less than -100%.")
    if contribution_timing not in ("end", "start"):
        errors.append("contribution_timing must be 'end' or 'start'.")

    if errors:
        raise ValueError(" ".join(errors))


def future_value(
    principal: float,
    annual_rate: float,
    years: float,
    compounds_per_year: int = 12,
    contribution: float = 0.0,
    contribution_timing: str = "end",
) -> SavingsProjection:
    """
    Project the future value of savings under compound interest.

    Parameters
    ----------
    principal : float
        Starting balance.
    annual_rate : float
        Annual nominal interest rate as a decimal (e.g. 0.05 for 5%).
    years : float
        Number of years to project.
    compounds_per_year : int, default 12
        Number of compounding periods per year (12 = monthly, 1 = annual,
        4 = quarterly, 365 = daily).
    contribution : float, default 0.0
        Amount contributed each compounding period.
    contribution_timing : {"end", "start"}, default "end"
        Whether each period's contribution is added before ("start") or
        after ("end") that period's interest is applied.

    Returns
    -------
    SavingsProjection
        Dataclass with the final future value, total contributions made,
        total interest earned, and a period-by-period schedule.
    """
    _validate_future_value_inputs(
        principal=principal,
        annual_rate=annual_rate,
        years=years,
        compounds_per_year=compounds_per_year,
        contribution=contribution,
        contribution_timing=contribution_timing,
    )

    n_periods = round(years * compounds_per_year)
    period_rate = annual_rate / compounds_per_year

    balance = principal
    total_contributions = 0.0
    schedule = []

    for period in range(1, n_periods + 1):
        interest_earned = 0.0

        if contribution_timing == "start":
            balance += contribution
            total_contributions += contribution

        interest_earned = balance * period_rate
        balance += interest_earned

        if contribution_timing == "end":
            balance += contribution
            total_contributions += contribution

        schedule.append(
            {
                "period": period,
                "contribution": contribution,
                "interest_earned": interest_earned,
                "balance": balance,
            }
        )

    total_interest_earned = balance - principal - total_contributions

    return SavingsProjection(
        future_value=balance,
        total_contributions=total_contributions,
        total_interest_earned=total_interest_earned,
        schedule=schedule,
    )


def plot_savings_growth(projection: SavingsProjection, compounds_per_year: int = 12):
    """
    Plot balance over time from a SavingsProjection's schedule.

    Parameters
    ----------
    projection : SavingsProjection
        Result returned by `future_value`.
    compounds_per_year : int, default 12
        Must match the value used to generate `projection`, so periods
        can be converted to years for the x-axis.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    periods = [row["period"] for row in projection.schedule]
    balances = [row["balance"] for row in projection.schedule]
    years_x = [p / compounds_per_year for p in periods]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(years_x, balances, linewidth=2)
    ax.set_xlabel("Years")
    ax.set_ylabel("Balance ($)")
    ax.set_title("Savings Balance Over Time")
    ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def print_schedule_table(
    projection: SavingsProjection,
    compounds_per_year: int = 12,
    every_n_periods: int = 1,
) -> None:
    """
    Print a formatted period-by-period amortization/growth table.

    Parameters
    ----------
    projection : SavingsProjection
        Result returned by `future_value`.
    compounds_per_year : int, default 12
        Must match the value used to generate `projection`, so periods
        can be converted to years in the "Year" column.
    every_n_periods : int, default 1
        Print only every Nth period (e.g. 12 to show one row per year
        for a monthly schedule) to keep long schedules readable.
    """
    header = f"{'Period':>6} {'Year':>6} {'Contribution':>14} {'Interest':>12} {'Balance':>14}"
    print(header)
    print("-" * len(header))

    for row in projection.schedule:
        if row["period"] % every_n_periods != 0 and row["period"] != len(
            projection.schedule
        ):
            continue
        year = row["period"] / compounds_per_year
        print(
            f"{row['period']:>6} "
            f"{year:>6.2f} "
            f"{row['contribution']:>14,.2f} "
            f"{row['interest_earned']:>12,.2f} "
            f"{row['balance']:>14,.2f}"
        )

    print("-" * len(header))
    print(
        f"{'Totals':>6} {'':>6} "
        f"{projection.total_contributions:>14,.2f} "
        f"{projection.total_interest_earned:>12,.2f} "
        f"{projection.future_value:>14,.2f}"
    )


def plot_scenario_comparison(
    scenarios: dict[str, SavingsProjection],
    compounds_per_year: int = 12,
):
    """
    Plot balance-over-time for multiple scenarios on one chart.

    Parameters
    ----------
    scenarios : dict[str, SavingsProjection]
        Mapping of scenario label -> projection (e.g. results from
        separate `future_value` calls).
    compounds_per_year : int, default 12
        Must match the value used to generate the projections, so
        periods can be converted to years for the x-axis.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))

    for label, projection in scenarios.items():
        periods = [row["period"] for row in projection.schedule]
        balances = [row["balance"] for row in projection.schedule]
        years_x = [p / compounds_per_year for p in periods]
        ax.plot(years_x, balances, linewidth=2, label=label)

    ax.set_xlabel("Years")
    ax.set_ylabel("Balance ($)")
    ax.set_title("Savings Balance Over Time by Scenario")
    ax.yaxis.set_major_formatter(lambda x, _: f"${x:,.0f}")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def print_scenario_comparison_table(scenarios: dict[str, SavingsProjection]) -> None:
    """
    Print a side-by-side summary table comparing multiple scenarios.

    Parameters
    ----------
    scenarios : dict[str, SavingsProjection]
        Mapping of scenario label -> projection (e.g. results from
        separate `future_value` calls).
    """
    labels = list(scenarios.keys())
    label_width = max(12, max(len(label) for label in labels) + 2)

    header = f"{'Metric':<22}" + "".join(f"{label:>{label_width}}" for label in labels)
    print(header)
    print("-" * len(header))

    rows = [
        ("Total contributions", "total_contributions"),
        ("Total interest earned", "total_interest_earned"),
        ("Future value", "future_value"),
    ]
    for row_label, attr in rows:
        values = [getattr(scenarios[label], attr) for label in labels]
        print(
            f"{row_label:<22}"
            + "".join(f"{value:>{label_width},.2f}" for value in values)
        )


def _prompt_float(message: str) -> float:
    return float(input(message).strip())


def run_cli() -> None:
    """Interactive command-line prompt for a single scenario."""
    print("Compound interest / savings growth calculator\n")

    principal = _prompt_float("Starting principal ($): ")
    annual_rate_pct = _prompt_float("Annual interest rate (%, e.g. 5 for 5%): ")
    years = _prompt_float("Number of years: ")
    compounds_per_year = int(
        _prompt_float("Compounding periods per year (12=monthly, 1=annual): ")
    )
    contribution = _prompt_float("Contribution per period ($, 0 if none): ")

    result = future_value(
        principal=principal,
        annual_rate=annual_rate_pct / 100,
        years=years,
        compounds_per_year=compounds_per_year,
        contribution=contribution,
    )

    print(f"\nFuture value:          ${result.future_value:,.2f}")
    print(f"Total contributions:    ${result.total_contributions:,.2f}")
    print(f"Total interest earned:  ${result.total_interest_earned:,.2f}")


def _prompt_scenario(label: str) -> tuple[str, SavingsProjection]:
    """Prompt for one scenario's inputs and return (name, projection)."""
    print(f"\n--- {label} ---")
    name = input("Scenario name (e.g. 'Conservative'): ").strip() or label
    principal = _prompt_float("Starting principal ($): ")
    annual_rate_pct = _prompt_float("Annual interest rate (%, e.g. 5 for 5%): ")
    years = _prompt_float("Number of years: ")
    compounds_per_year = int(
        _prompt_float("Compounding periods per year (12=monthly, 1=annual): ")
    )
    contribution = _prompt_float("Contribution per period ($, 0 if none): ")

    projection = future_value(
        principal=principal,
        annual_rate=annual_rate_pct / 100,
        years=years,
        compounds_per_year=compounds_per_year,
        contribution=contribution,
    )
    return name, projection


def run_comparison_cli() -> None:
    """Interactive command-line prompt comparing two user-specified scenarios."""
    print("Savings scenario comparison\n")
    print(
        "Note: both scenarios use the compounding frequency entered for "
        "Scenario 1 when converting periods to years in the chart/table.\n"
    )

    name_a, projection_a = _prompt_scenario("Scenario 1")
    name_b, projection_b = _prompt_scenario("Scenario 2")
    scenarios = {name_a: projection_a, name_b: projection_b}

    print()
    print_scenario_comparison_table(scenarios)

    save_path = input(
        "\nSave comparison chart to file (path, or blank to skip): "
    ).strip()
    if save_path:
        import matplotlib.pyplot as plt

        fig = plot_scenario_comparison(scenarios)
        fig.savefig(save_path, dpi=150)
        plt.close(fig)
        print(f"Chart saved to {save_path}")


if __name__ == "__main__":
    print("1) Single scenario")
    print("2) Compare two scenarios")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "2":
        run_comparison_cli()
    else:
        run_cli()
