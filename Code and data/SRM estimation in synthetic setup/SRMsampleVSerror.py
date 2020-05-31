# Code for figure 1. Sample Vs error for normal distribution.

# importing files
import numpy
import math
from scipy.stats import norm
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 14})
import random
import pickle

# iid samples
def generate_samples(distribution, parameters, no_of_samples):
    if distribution == "normal":
        mu = parameters[0]
        sigma = parameters[1]
        samples = numpy.random.normal(mu, sigma, no_of_samples)

    if distribution == "uniform":
        p = parameters[0]
        q = parameters[1]
        samples = numpy.random.uniform(p, q, no_of_samples)

    return samples

# empirical var definition
def empirical_var(a, samples):
    samples.sort()
    if a == 0:
        return samples[0]
    return samples[int(math.ceil(len(samples)*a)) - 1]

# user risk aversion function
def phi(p):
	K = 5.0 # constant for user
	# phi =  K e^(-K(1-b))/(1-e^(-K))
	value = K * numpy.exp(-K*(1-p))/float(1 - numpy.exp(-K))
	return value

# empirical SRM definition
def empirical_SRM(samples, subdivisions):
    m = subdivisions  # subdivision number for trapezoidal rule.
    srm = 0.0
    h = float(1/m)  # width of single subdivision.
    for k in range(1, m+1):
        srm = srm + phi((k - 1) * h) * empirical_var( (k - 1) * h, samples) + phi(k * h) * empirical_var(k * h, samples)
    srm = (srm * float(h)) / float(2)

    return srm


# This is the main entry point of this script.
if __name__ == "__main__":
    #random.seed(1234)
    #a = 0.95
    no_of_samples = 0
    distribution = "normal"
    print("distribution is %s" % (distribution))

    # for normal random variable X ~N(mu, sigma)
    if distribution == "normal":
        mu = 0.5
        sigma = 5
        parameters = [mu, sigma]

    # for uniform random variable X ~ U(p ,q)
    if distribution == "uniform":
        p = -10
        q = 10
        parameters = [p, q]

    samples_true = generate_samples(distribution, parameters, 100000)
    empirical_true = empirical_SRM(samples_true, 10000)
    true_srm = empirical_true
    print(true_srm)
    # sample sizes
    # X = numpy.arange(1000, 1210, 100)  # for 100 gapper
    X = numpy.arange(500, 10000, 400)  # for 200 gapper
    # X = [100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200, 102400]

    # taking subdivisions
    # subdivisions = numpy.arange(100, 100000, 200)
    # subdivisions = subdivisions.tolist()
    subdivisions = [150, 500]
    empirical_srm = [0 for i in subdivisions]
    srms = []
    for i in range(0, len(X)):  # for different no of samples
        srms.append([])
        for j in range(0, 2):  # generating same no of samples each time for averaging error bar
            srms[i].append([])
            no_of_samples = X[i]
            samples = generate_samples(distribution, parameters, no_of_samples)
            for k in range(0, len(subdivisions)):
                empirical = empirical_SRM(samples, subdivisions[k])
                empirical_srm[k] = abs(empirical - true_srm)
                srms[i][j].append(empirical_srm[k])
        print("done for sample size = %i" % (X[i]))
    srms = numpy.array(srms)
    srms_error = srms.std(1)
    srms = srms.mean(1)
    srms = srms.tolist()
    srms_error = srms_error.tolist()

    # Plot shape and coloring
    # fmt = ['s', 'P', '^']
    # color = [ 'darkorange', 'black', 'royalblue']
    # fmt = ['s', 'P', 'o', '^']
    # color = ['darkorange', 'black', 'limegreen', 'royalblue']
    if len(subdivisions) == 1:
        fmt = ['s']
        # color = ['darkgray', 'dimgray', 'black']
        color = ['darkorange']
        # color = ['darkorange', 'black', 'royalblue']
    if len(subdivisions) == 2:
        fmt = ['P', 's']
        # color = ['darkgray', 'dimgray', 'black']
        color = ['black', 'royalblue']
        # color = ['darkorange', 'black', 'royalblue']
    if len(subdivisions) == 3:
        fmt = ['s', 'P', '^']
        # color = ['darkgray', 'dimgray', 'black']
        color = ['darkorange', 'royalblue', 'black']
        # color = ['darkorange', 'black', 'royalblue']
    if len(subdivisions) == 4:
        fmt = ['s', 'x', 'o', '^']
        color = ['darkgray', 'grey', 'dimgray', 'black']
    for k in range(0, len(subdivisions)):
        Y = []
        Y_SE = []
        for i in srms:
            # Y.append(math.pow(100, i[k]))
            Y.append(i[k])
        for i in srms_error:
            Y_SE.append(i[k])
        print("Y =")
        print(Y)
        print("Y_SE =")
        print(Y_SE)

        ax = plt.errorbar(X, Y, yerr=Y_SE, fmt=fmt[k], color=color[k], markersize=5, capsize=4, label="SRM-Trapz %i" % (subdivisions[k]))
    plt.xlabel('Sample size')
    plt.ylabel('|True SRM - Empirical SRM|')
    plt.legend()
    plt.savefig('sampleVSerror.eps', bbox_inches='tight', Transparent='True')
    plt.show()
