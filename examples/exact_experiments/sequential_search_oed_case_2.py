import numpy as np
from time import time
from pyomo import dae as pod
from pyomo import environ as po
from scipy.optimize import minimize

from pydex.core.designer import Designer


def simulate(ti_controls, sampling_times, model_parameters):
    norm_spt = sampling_times / np.max(sampling_times)
    model = create_model(norm_spt)

    """ fixing the control variables """
    # time-invariant
    model.theta_0.fix(model_parameters[0])
    model.theta_1.fix(model_parameters[1])
    model.alpha_a.fix(model_parameters[2])
    model.alpha_b.fix(0)
    model.nu.fix(model_parameters[3])

    model.tau.fix(max(sampling_times))
    model.ca[0].fix(ti_controls[0])
    model.cb[0].fix(0)
    model.temp.fix(ti_controls[1])
    # no time-varying control for this example

    """ simulating """
    simulator = pod.Simulator(model, package="casadi")
    simulator.simulate(integrator='idas')
    simulator.initialize_model()

    """" extracting results and returning it in appropriate format """
    ca = np.array([model.ca[t].value for t in norm_spt])
    cb = np.array([model.cb[t].value for t in norm_spt])

    return np.array([ca, cb]).T

def create_model(spt):
    """ defining the model """
    model = po.ConcreteModel()
    model.t = pod.ContinuousSet(bounds=(0, 1), initialize=spt)
    model.tau = po.Var()

    model.temp = po.Var()

    model.ca = po.Var(model.t, bounds=(0, 50))
    model.cb = po.Var(model.t, bounds=(0, 50))
    model.dca_dt = pod.DerivativeVar(model.ca, wrt=model.t)
    model.dcb_dt = pod.DerivativeVar(model.cb, wrt=model.t)

    model.theta_0 = po.Var()  # model parameters
    model.theta_1 = po.Var()
    model.alpha_a = po.Var()
    model.alpha_b = po.Var()
    model.nu = po.Var()

    def _material_balance_a(m, t):
        k = po.exp(m.theta_0 + m.theta_1 * (m.temp - 273.15) / m.temp)
        return m.dca_dt[t] / m.tau == - k * (m.ca[t] ** model.alpha_a) * (
                model.cb[t] ** model.alpha_b)

    model.material_balance_a = po.Constraint(model.t, rule=_material_balance_a)

    def _material_balance_b(m, t):
        k = po.exp(m.theta_0 + m.theta_1 * (m.temp - 273.15) / m.temp)
        return m.dcb_dt[t] / m.tau == m.nu * k * (m.ca[t] ** model.alpha_a) * (
                model.cb[t] ** model.alpha_b)

    model.material_balance_b = po.Constraint(model.t, rule=_material_balance_b)

    return model

def info_matrix(tic, spt, mp):
    designer1 = Designer()
    designer1.simulate = simulate
    designer1.ti_controls_candidates = np.array([tic])
    designer1.sampling_times_candidates = np.array([spt])
    designer1.model_parameters = mp
    designer1.initialize(verbose=0)
    designer1._trim_fim = False
    efforts = np.array([[1] * spt.size])
    return designer1.eval_fim(efforts)

def simul_d_opt(x):
    mp = np.array([-4.5, -2.2, 1, 0.5])
    tic1 = x[:2]
    spt1 = x[2:7]
    tic2 = x[7:9]
    spt2 = x[9:14]
    tic3 = x[14:16]
    spt3 = x[16:21]
    fim1 = info_matrix(tic1, spt1, mp)
    fim2 = info_matrix(tic2, spt2, mp)
    fim3 = info_matrix(tic3, spt3, mp)
    fim = fim1 + fim2 + fim3
    sign, log_det = np.linalg.slogdet(fim)

    """ log_det """
    if sign == 1:
        d_opt = - log_det
    else:
        d_opt = np.inf
    return d_opt

start = time()
opt_res = minimize(
    fun=simul_d_opt,
    x0=[
        1,
        273.15,
        50,
        60,
        70,
        80,
        90,
        2,
        303.15,
        50,
        100,
        200,
        80,
        90,
        5,
        323.15,
        50,
        60,
        70,
        80,
        90,
    ],
    method="l-bfgs-b",
    # method="SLSQP",
    # method="TNC",
    bounds=[
        (1, 5),
        (273.15, 323.15),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
        (1, 5),
        (273.15, 323.15),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
        (1, 5),
        (273.15, 323.15),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
        (0, 200),
    ],
    options={
        "disp": True,
    },
)
print(opt_res)
print(f"Optimization took {time() - start} CPU seconds.")
