from pyomo import environ as po
from pyomo import dae as pod
from matplotlib import pyplot as plt
import numpy as np
import logging

logging.getLogger("pyomo.core").setLevel(logging.ERROR)

def create_model(spt):
    norm_spt = spt / np.max(spt)

    m = po.ConcreteModel()

    """ Sets """
    m.i = po.Set(initialize=["A", "B", "C"])
    m.j = po.Set(initialize=[1, 2])

    """ Time Components """
    m.t = pod.ContinuousSet(bounds=(0, 1), initialize=norm_spt)
    m.tau = po.Var(bounds=(0, None))

    """ Concentrations """
    m.c = po.Var(m.t, m.i, bounds=(0, None))
    m.dcdt = pod.DerivativeVar(m.c, wrt=m.t)

    """ Experimental Variables """
    m.f_in = po.Var(bounds=(0, 10))

    """ Reaction Parameters """
    s = {
        ("A", 1): -1,
        ("A", 2):  0,
        ("B", 1):  1,
        ("B", 2): -1,
        ("C", 1):  0,
        ("C", 2):  1,
    }
    m.s = po.Param(m.i, m.j, initialize=s)
    c_in = {
        "A": 1,
        "B": 0,
        "C": 0,
    }
    m.c_in = po.Param(m.i, initialize=c_in)

    """ Model Parameters """
    m.k = po.Var(m.j, bounds=(0, None))

    """ Reaction Rates """
    m.r = po.Var(m.t, m.j)

    """ Model Equations """
    def _bal(m, t, i):
        return m.dcdt[t, i] / m.tau == m.f_in * m.c_in[i] + sum(m.s[i, j] * m.r[t, j] for j in m.j)
    m.bal = po.Constraint(m.t, m.i, rule=_bal)

    def _r_def(m, t, j):
        if j == 1:
            return m.r[t, j] == m.k[j] * m.c[t, "A"]
        elif j == 2:
            return m.r[t, j] == m.k[j] * m.c[t, "B"]
        else:
            raise SyntaxError("Unrecognized reaction index, please check the model.")
    m.r_def = po.Constraint(m.t, m.j, rule=_r_def)

    return m

def simulate(ti_controls, sampling_times, model_parameters):
    norm_spt = sampling_times / np.max(sampling_times)
    m = create_model(sampling_times)
    m.tau.fix(max(sampling_times))

    m.f_in.fix(ti_controls[0])
    m.k[1].fix(model_parameters[0])
    m.k[2].fix(model_parameters[1])

    m.c[0, "A"].fix(1)
    m.c[0, "B"].fix(0)
    m.c[0, "C"].fix(0)

    simulator = pod.Simulator(m, package="casadi")
    t, profile = simulator.simulate(integrator="idas")

    simulator.initialize_model()
    c = np.array([[m.c[t, i].value for t in norm_spt] for i in m.i])

    if False:
        plt.plot(t, profile)

    return c.T

if __name__ == '__main__':
    """ Run Simulation """
    tic = [0]
    spt = np.linspace(0, 10, 101)
    mp = [1, 1]
    c = simulate(
        ti_controls=tic,
        sampling_times=spt,
        model_parameters=mp,
    )

    """ Plot Results """
    fig = plt.figure()
    axes = fig.add_subplot(111)
    axes.plot(
        spt,
        c[:, 0],
        label=r"$c_A$",
    )
    axes.plot(
        spt,
        c[:, 1],
        label=r"$c_B$",
    )
    axes.plot(
        spt,
        c[:, 2],
        label=r"$c_C$",
    )
    axes.legend()
    axes.set_xlabel("Time (hour)")
    axes.set_ylabel("Concentration (mol/L)")
    fig.tight_layout()

    plt.show()
