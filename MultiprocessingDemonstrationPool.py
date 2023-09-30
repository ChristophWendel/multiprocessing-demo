##########################################################
###   Demonstration of the Usage of Pool.apply_async   ###
##########################################################

# Purpose of these code snippets is to show the capabilities and the way of using of the Pool class of the multiprocessing package.


import multiprocessing
import time
import numpy as np
from scipy import integrate


### Definition of CPU-heavy functions

def ComputePi(N, ID):
    '''This determines pi as the N-th partial sum of the Madhava–Leibniz series, which actually is an inefficient determination of pi. For the present purpose this computation just represents a CPU-heavy computation. N is the number of summands to be added. ID is just an identifier that helps to name a certain call of ComputePi'''
    Sum = 0
    for n in range(0,N): # n goes over all N integers from 0 up to N-1.
        Sum += 4*(-1)**(n)/(2*n+1)
    return (ID, Sum) # Return the identifier of this function call and the approximation of pi.

def ComputePiVectorised(N, ID):
    '''This is a much more faster implementation of pi as the N-th partial sum of the Madhava–Leibniz series. It is vectorised via making use of numpy. For big N it is CPU-expensive, but due to the big numpy-array it is perhaps not strictly CPU-bound.'''
    RangeOfn = np.linspace(0,N-1,N) # This array contains all N integers from 0 up to N-1.
    Summands = (-1)**(RangeOfn)/(2*RangeOfn+1)
    Sum = 4*np.sum(Summands)
    return (ID, Sum)

def Integrand(x, m, t):
    """This function is a surrogate for a very complicated integrand. It is to be integrated. The function takes a number of arguments m and t."""
    return m*x+t

def AnalyticIntegral(LowerB, UpperB, m, t):
    """This is the analytical result of the definite integral of the above Integrand from the lower boundary LowerB to the upper border UpperB."""
    return m*(UpperB**2-LowerB**2)/2 + t*(UpperB-LowerB)


if __name__ == '__main__':


### Specification of parameters

    N=5000000 # Specify the number of summands to be added in determining the partial sum.
    NumberOfTasks = 16 # Specify the number of times pi is supposed to be determined.
    NumberOfProcesses = 6 # Specify the number of CPU cores (workers) that are supposed to help (parallely) in the various computations. This should be equal or smaller than NumberOfTasks because it is not reasonable to apply more workers than there are tasks.


### Four different computations, showing the benefits of vectorisation and parallelisation:

# 1. Case: Non-vectorised and serial computation
    print('Simple computation of pi, serial approach:') # First, determine pi NumberOfTasks times without multiprocessing.
    StartingTime = time.time() # Start the timer.
    ResultsSerial = [ComputePi(N, i) for i in range(1,NumberOfTasks+1)] # Determine the N-th partial sum NumberOfTasks times and collect the results in a list.
    print('pi =', ResultsSerial) # Show the results.
    EndingTime = time.time() # Stop the timer.
    TimeInterval = (EndingTime-StartingTime) # Determine the computation time...
    print("Time spent on the computation:", TimeInterval, "\n") # ... and print it.

# 2. Case: Non-vectorised and parallel computation
    print('Simple computation of pi, parallelised approach via Pool.apply_async:') # Second, determine pi NumberOfTasks times with multiprocessing.
    StartingTime = time.time() # Start the timer.
    MyPool = multiprocessing.Pool(processes=NumberOfProcesses) # Create a pool of NumberOfProcesses workers.
    ResultsParallel = [MyPool.apply_async(ComputePi,args=(N, i)) for i in range(1,NumberOfTasks+1)] # This starts NumberOfTasks calls of ComputePi with arguments being N and i. All these calls (tasks) are spread to the various workers in the pool, which work contemporaneously now through the entire bunch of tasks.
    Output = [r.get() for r in ResultsParallel] # After .apply_async, one has to use .get() to collect the results and arrange them in a list. Also, it ensues that the subsequent code is not performed before the tasks have been accomplished.
    MyPool.close() # This has to be called before .join. It exits the processes after they have accomplished their tasks and retrieves the used RAM.
    MyPool.join() # This closes the pool. This ensures that the subsequent code is executed not before all tasks have been finished.
    print('pi =', Output) # Show the results.
    EndingTime = time.time() # Stop the timer.
    TimeInterval = (EndingTime-StartingTime) # Determine the computation time...
    print("Time spent on the computation:", TimeInterval, "\n") # ... and print it.
# It seems that case 2 is faster than case 1 (by about the factor 1/NumberOfProcesses). Thus, for this non-vectorised task, parallelisation brings a huge increase in speed of evaluation.

# 3. Case: Vectorised and serial computation
    print('Vectorised computation of pi, serial approach:') # Third, determine pi NumberOfTasks times with the vectorised version but without multiprocessing.
    StartingTime = time.time()
    ResultsSerialVectorised = [ComputePiVectorised(N, i) for i in range(1,NumberOfTasks+1)]
    print('pi =', ResultsSerialVectorised)
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print("Time spent on the computation:", TimeInterval, "\n")
# It seems the vectorised case is much faster than both case 1 and 2.

# 4. Case: Vectorised and parallel computation
    print('Vectorised computation of pi, parallelised approach via Pool.apply_async:') # Fourth, determine pi NumberOfTasks times with the vectorised version and with multiprocessing.
    StartingTime = time.time()
    MyPool = multiprocessing.Pool(processes=NumberOfProcesses)
    ResultsParallelVectorised = [MyPool.apply_async(ComputePiVectorised,args=(N, i)) for i in range(1,NumberOfTasks+1)]
    Output = [r.get() for r in ResultsParallelVectorised]
    MyPool.close()
    MyPool.join()
    print('pi =', Output)
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print("Time spent on the computation:", TimeInterval, "\n")
# It seems that for the vectorised case and for big N, parallelisation only brings a small gain in evaluation speed. For smaller N, the parallelised version is even slower than the serial approach.
# The good thing using the Pool class is first that it is easy to implement and second that the results can easily be returned and third that the workers in the pool grab new jobs from the list of tasks and execute them until the whole list of tasks is worked through.


### New problem: Suppose a case where pairs of arguments have to be given to the function to be evaluated:

    ListOfTaskIDs = np.linspace(1,NumberOfTasks,NumberOfTasks) # Arrange the IDs in an array.
    ListOfN = ListOfTaskIDs*1000000 # Compile an array containing the numbers of summands to be added in determining the partial sum in the respective task. The i-th item in this array corresponds to the i-th item in the array ListOfTaskIDs.

    print('Vectorised computation of pi, parallelised approach via Pool.apply_async with zip:') # Determine pi NumberOfTasks times with the vectorised version and with multiprocessing.
    StartingTime = time.time()
    MyPool = multiprocessing.Pool(processes=NumberOfProcesses)
    ResultsParallelVectorisedZip = [MyPool.apply_async(ComputePiVectorised,args=(int(j), i)) for i, j in zip(ListOfTaskIDs,ListOfN)] # Loop over both arguments simultaneously via zip.
    Output = [r.get() for r in ResultsParallelVectorisedZip]
    MyPool.close()
    MyPool.join()
    print('pi =', Output)
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print("Time spent on the computation:", TimeInterval, "\n")


### Another problem: Integrate a function. An integral can be cut into smaller constituents:

    m=2 # Choose this parameter arbitrarily.
    t=5 # Same here.
    TrueResult=AnalyticIntegral(0, 100, m, t) # Determine the value of the integral from 0 up to 100.
    print('True Result:', TrueResult)

    ListOfIntegrationBorders = np.linspace(0, 100, NumberOfProcesses+1) # Cut the integration range into smaller part ranges and determine the corresponding part integrals by separate workers.
    MyPool = multiprocessing.Pool(processes=NumberOfProcesses)
    ResultsOfPartIntegrals = [MyPool.apply_async(integrate.quad,args=[Integrand, i, j, (m, t)]) for i, j in zip(ListOfIntegrationBorders[:-1], ListOfIntegrationBorders[1:])] # Loop over both arguments simultaneously via zip. The arguments m and t of the Integrand can also be specified in the list of arguments of .apply_async.
    Output = [r.get() for r in ResultsOfPartIntegrals]
    Sum=sum([i[0] for i in Output]) # As we are not interested in the error estimate of the numerical integration here, we only grab the results of the part integrals by using i[0].
    MyPool.close()
    MyPool.join()
    print('Numerically and parallelly determined result:', Sum)
# A time gain via parallelisation is not present here in this simple integral, but this is supposed to demonstrate how a numerical integration can be parallelised.
