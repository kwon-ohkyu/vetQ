import numpy
import matplotlib.pyplot as plt

N=10000
roll=numpy.zeros(N)
expectation = numpy.zeros(N)
for i in range(N):
    roll[i]=numpy.random.randint(1,7)
for i in range(1,N):
    expectation[i]=numpy.mean(roll[0:i])
plt.plot(expectation)
