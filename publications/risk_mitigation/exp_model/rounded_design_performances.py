from pydex.core.designer import Designer
from local_design import simulate
import numpy as np


designer = Designer()
designer.simulate = simulate
designer.ti_controls_candidates = designer.enumerate_candidates(
    bounds=[
        [0, 0.5],
    ],
    levels=[
        21,
    ],
)

np.random.seed(123)
n_scr = 200
param = np.random.uniform(
    low=[1, -10],
    high=[10, 0],
    size=(n_scr, 2),
)
designer.model_parameters = param

local_design_efforts = np.array([
    [5.00023299e-01],   # Candidate 1
    [6.98725680e-09],
    [5.17125933e-09],
    [6.26472222e-09],
    [8.97789517e-09],

    [1.20110169e-08],
    [9.66765432e-09],
    [2.87218601e-07],
    [4.99975697e-01],  # Candidate 8
    [5.46497287e-07],

    [4.00096324e-08],
    [2.18599626e-08],
    [1.50948534e-08],
    [1.07890913e-08],
    [7.92234066e-09],

    [5.97453669e-09],
    [4.61503062e-09],
    [3.63889749e-09],
    [2.91956126e-09],
    [2.37743191e-09],

    [1.96110213e-09],  # Candidate 21
])
max_mean_efforts = np.array([
    [0.4848],  # Candidate 1
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0.4283],  # Candidate 8
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0.0870],  # Candidate 21
])
max_cvar_efforts = np.array([
    [0.5000],  # Candidate 1
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0.5000],  # Candidate 7
    [0],  # Candidate 8
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0],  # Candidate 21
])
goldilocks_efforts = np.array([
    [0.4930],  # Candidate 1
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0.4700],  # Candidate 8
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0],
    [0],
    [0],
    [0],
    [0],

    [0.0370],  # Candidate 21
])
designer.initialize(verbose=2)

compute_actual_efficiency = False
n_exp = 3

print("[Local Design]".center(100, "="))
# compute the Type 1 D-optimal mean
designer.design_experiment(
    designer.d_opt_criterion,
    pseudo_bayesian_type=1,
    fix_effort=local_design_efforts,
)
designer.print_optimal_candidates()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

# compute the CVaR 0.75
designer.design_experiment(
    designer.cvar_d_opt_criterion,
    beta=0.75,
    fix_effort=local_design_efforts,
)
designer.print_optimal_candidates()
designer.plot_criterion_pdf()
designer.plot_criterion_cdf()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

print("[Maximal Mean Design]".center(100, "="))
# compute the Type 1 D-optimal mean
designer.design_experiment(
    designer.d_opt_criterion,
    pseudo_bayesian_type=1,
    fix_effort=max_mean_efforts,
)
designer.print_optimal_candidates()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

# compute the CVaR 0.75
designer.design_experiment(
    designer.cvar_d_opt_criterion,
    beta=0.75,
    fix_effort=max_mean_efforts,
)
designer.print_optimal_candidates()
designer.plot_criterion_pdf()
designer.plot_criterion_cdf()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

print("[Maximal CVaR Design]".center(100, "="))
# compute the Type 1 D-optimal mean
designer.design_experiment(
    designer.d_opt_criterion,
    pseudo_bayesian_type=1,
    fix_effort=max_cvar_efforts,
)
designer.print_optimal_candidates()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

# compute the CVaR 0.75
designer.design_experiment(
    designer.cvar_d_opt_criterion,
    beta=0.75,
    fix_effort=max_cvar_efforts,
)
designer.print_optimal_candidates()
designer.plot_criterion_pdf()
designer.plot_criterion_cdf()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

print("[Goldilocks Design]".center(100, "="))
# compute the Type 1 D-optimal mean
designer.design_experiment(
    designer.d_opt_criterion,
    pseudo_bayesian_type=1,
    fix_effort=goldilocks_efforts,
)
designer.print_optimal_candidates()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

# compute the CVaR 0.75
designer.design_experiment(
    designer.cvar_d_opt_criterion,
    beta=0.75,
    fix_effort=goldilocks_efforts,
)
designer.print_optimal_candidates()
designer.plot_criterion_pdf()
designer.plot_criterion_cdf()
designer.apportion(n_exp, compute_actual_efficiency=compute_actual_efficiency)

designer.show_plots()
