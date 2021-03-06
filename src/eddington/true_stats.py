import numpy as np
from scipy.optimize import least_squares
from scipy.linalg import inv


def chi2(params, *args):
    # function, x, y, x_variance, y_variance, func_derivative_by_x
    func, x, y, xvar, yvar, derr = args

    return (y - func(params, x))/np.sqrt(xvar*np.square(derr(params, x)) + yvar)


class ModifiedOutput():
    # a small output class to have all the needed attributes
    def __init__(self, params, cost, cov_mat):
        self.beta = params
        self.chi2 = cost
        self.sd_beta = np.sqrt(np.diag(cov_mat)) #std(x) = sqrt(cov(x, x))
        self.cov_beta = cov_mat


class ModifiedODR():
    def __init__(self, data, model, beta0=None):
        self.data = data
        self.model = model
        if beta0 is None: raise IOError("Initial guess is None!")
        self.beta0 = beta0

    def run(self):
        data  = self.data
        model = self.model
        if model.fjacd is None:
            # use a simple 2-point finnite difference scheme
            # TODO: add support for controllable FD stepsize, as in ODR
            xderr = lambda params, x:(model.fcn(params, x + 1e-8) - model.fcn(params, x - 1e-8))/(2e-8)
        else:
            xderr = model.fjacd
        
        #fit. FOR NOW, NUMERICALLY DERIVATES CHI2 (REQUIRES f_xa FOR ANALYTICAL)
        res = least_squares(chi2, self.beta0, '3-point', method='trf',
                            args=(model.fcn,
                                  data.x, data.y,
                                  np.square(data.sx), np.square(data.sy),
                                  xderr))

        # calculate approximate covariance matrix using Gauss-Newton approximation
        cov_mat = inv(res.jac.T@res.jac)

        # make "output" object
        output = ModifiedOutput(res.x, res.cost, cov_mat)
        return output
