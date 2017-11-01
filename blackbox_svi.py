import autograd.numpy as np
import autograd.numpy.random as npr
from autograd import grad
rs = npr.RandomState(0)


def kl_inference(log_gp_prior, N_weights, N_samples):
    def unpack_params(params):
        mean, log_std = params[:N_weights], params[N_weights:]
        return mean, log_std

    def kl_objective(params, t):
        """
        Provides a stochastic estimate of the kl divergence
        between p_BNN(f|phi) and p_GP(f|theta)
        mean, log_std                                           dim = [N_weights]
        samples                                                 dim = [N_samples, N_weights]
        kl                                                      dim = [1]

        """

        prior_mean, prior_log_std = unpack_params(params)
        samples = rs.randn(N_samples, N_weights) * np.exp(prior_log_std) + prior_mean
        kl = -np.mean(log_gp_prior(samples, t))
        return kl

    grad_kl = grad(kl_objective)

    return kl_objective, grad_kl, unpack_params


def elbo_inference(logprob, N_weights, N_samples):
    def unpack_params(params):
        mean, log_std = params[:N_weights], params[N_weights:]
        return mean, log_std

    def gaussian_entropy(log_std):
        return 0.5 * N_weights * (1.0 + np.log(2*np.pi)) + np.sum(log_std)

    def elbo_objective(params, t):
        """
        Provides a stochastic estimate of the evidence lower bound
        ELBO = H[q(w)] + E_q(w)[p(N_weights|w)]

        params                                                  dim = [2*N_weights]
        mean, log_std                                           dim = [N_weights]
        samples                                                 dim = [N_samples, N_weights]
        elbo                                                    dim = [1]
        """
        mean, log_std = unpack_params(params)
        samples = rs.randn(N_samples, N_weights) * np.exp(log_std) + mean
        lower_bound = gaussian_entropy(log_std) + np.mean(logprob(samples, t))
        return -lower_bound

    grad_elbo = grad(elbo_objective)

    return elbo_objective, grad_elbo, unpack_params