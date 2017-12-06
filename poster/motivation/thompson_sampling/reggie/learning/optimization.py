"""
Perform type-II maximum likelihood to fit the hyperparameters of a GP model.
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import numpy as np
import scipy.optimize as so

__all__ = ['optimize']


def optimize(model, raw=False):
    """
    Perform type-II maximum likelihood to fit GP hyperparameters.
    """
    # use a copy of the model so we don't modify it while we're optimizing
    model = model.copy()

    if model.params.size == 0:
        # this is kind of a stupid object to optimize, but we want to make sure
        # that we don't crash if someone decides to do this.
        theta = np.array([])

    else:
        def objective(theta):
            """
            Return the negative log marginal likelihood of the model and the
            gradient of this quantity wrt the parameters.
            """
            # update the model using parameters in the transformed space
            model.params.set_value(theta, transform=True)

            # get prior and likelihood as well as their gradients in the
            # un-transformed space
            logp0, dlogp0 = model.params.get_logprior(grad=True)
            logp1, dlogp1 = model.get_loglike(grad=True)

            # form the posterior and transform the gradients
            logp = -(logp0 + logp1)
            dlogp = -(dlogp0 + dlogp1) * model.params.gradfactor

            return logp, dlogp

        # get rid of any infinite bounds.
        bounds = model.params.get_bounds(transform=True)
        isinf = np.isinf(bounds)
        bounds = np.array(bounds, dtype=object)
        bounds[isinf] = None
        bounds = map(tuple, bounds)

        # optimize the model
        theta = model.params.get_value(transform=True)
        theta, _, _ = so.fmin_l_bfgs_b(objective, theta, bounds=bounds)

    if raw:
        # return the parameters in the transformed space
        model = theta
    else:
        model.params.set_value(theta, transform=True)

    return model
