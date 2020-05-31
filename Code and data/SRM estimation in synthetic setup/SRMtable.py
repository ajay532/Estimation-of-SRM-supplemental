# Code for table 1. results for SRM estimation SRM-Trapz and SRM-True for four different distributions

# importing files
import numpy
import math
from scipy.stats import norm
import matplotlib.pyplot as plt
import random
random.seed(1234)
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

    if distribution == "exponential":
        lamda = parameters[0]
        samples = numpy.random.exponential(1/lamda, no_of_samples)

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
    #if a == 1:
    #    print ("Error: CVaR can not be calculate at level 1, since 1/(1-a) become undefined")
    #    return -1
    srm = 0.0
    h = float(1/m)  # width of single subdivision.
    for k in range(1, m+1):
        srm = srm + phi((k - 1) * h) * empirical_var( (k - 1) * h, samples) + phi(k * h) * empirical_var(k * h, samples)
    srm = (srm * float(h)) / float(2)

    return srm

# This is the main entry point of this script.
if __name__ == "__main__":
    # random.seed(1234)
    no_of_samples = 0
    distribution = "exponential"
    print("distribution is %s" % (distribution))

    # for normal random variable X ~N(mu, sigma)
    if distribution == "normal":
        mu = 0
        sigma = 100
        parameters = [mu, sigma]

    # for uniform random variable X ~ U(p ,q)
    if distribution == "uniform":
        p = -1000
        q = 1000
        parameters = [p, q]

    if distribution == "exponential":
        lamda = 0.2
        parameters = [lamda]

    print("parameters are %s" % (parameters))
    samples_true = generate_samples(distribution, parameters, 100000)
    empirical_true = empirical_SRM(samples_true, 10000)
    true_srm = empirical_true
    # X = numpy.arange(1000, 1210, 100)  # for 100 gapper
    # X = numpy.arange(100, 300, 100)  # for 200 gapper
    X = [10000]
    subdivisions = [500, 1000]
    iterations = 1000
    # subdivisions = numpy.arange(100, 100000, 200)
    # subdivisions = subdivisions.tolist()
    empirical_srm = [0 for i in subdivisions]
    srms = []
    for i in range(0, len(X)):  # for different no of samples
        srms.append([])
        for j in range(0, iterations):  # generating same no of samples each time for averaging error bar
            srms[i].append([])
            no_of_samples = X[i]
            samples = generate_samples(distribution, parameters, no_of_samples)
            srms[i][j].append(true_srm)
            for k in range(0, len(subdivisions)):
                empirical = empirical_SRM(samples, subdivisions[k])
                empirical_srm[k] = abs(empirical - true_srm)
                srms[i][j].append(empirical)
            print("avg no = %i" % (j))
        print("done for sample size = %i" % (X[i]))
    srms = numpy.array(srms)
    srms_error = srms.std(1)
    srms = srms.mean(1)
    print("distribution is %s" % (distribution))
    print("parameters are %s" % (parameters))
    print("subdivision for SRM is %s" % (subdivisions))
    print("Samples_size are %s, placed vertically in the table" % (X))
    print("averaged on = %s iterations" % (iterations))
    print("true SRM \t subdivisions = %s" % (subdivisions))
    print(srms)
    print("SE_srms =")
    print(srms_error)
