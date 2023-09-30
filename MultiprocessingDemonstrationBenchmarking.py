############################################################################
###   Getting Benchmarks of Various Implementations of Multiprocessing   ###
############################################################################

# Purpose of this code is to determine the runtime of a given CPU-bound computation performed serially, parallely (with multiprocessing.Pool) and parallely (with multiprocessing.Process) and to compare the speed of the various approaches in dependence on the number of tasks and on the weight of the computation and in dependence on the number of used processes.


import numpy as np
import random
import multiprocessing
import platform
import time
import subprocess
import pylab as pl

if platform.python_version_tuple()[0]=='3':
    from queue import Empty
else:
    from Queue import Empty

if platform.system() == "Windows":
    ProcessorModel = str(subprocess.check_output("wmic cpu get name", shell=True)).split('\\n')[1].split('  ')[0]+' '+str(multiprocessing.cpu_count())+' threads'
elif platform.system() == "Linux":
    try:
		ProcessorModel = str(subprocess.check_output("cat /proc/cpuinfo", shell=True)).split('\t')[0].split('\\')[10].split(':')[1].strip()
	except:
		ProcessorModel = 'Unknown processor model'
else:
    ProcessorModel = 'Unknown processor model'


def SleepForxSeconds(x):
    s=0
    while s<(x-1):
        time.sleep(1.0)
        s+=1
        print('sleeping...')
    time.sleep(1.0)
    print("...awakening! It's now %s o'clock." % time.asctime().split()[3])
    print(' ')

def CPUHeavyFunction(NumbersToDraw, ID):
    """Compute pi with Monte-Carlo-method. This is a CPU-heavy operation."""
    NumbersInside = 0
    for i in range(NumbersToDraw):
        x = random.random()
        y = random.random()
        if y <= np.sqrt(1-x*x):
            NumbersInside +=1
    Pi = 4*NumbersInside/NumbersToDraw
    return (ID, Pi)

def UsingQueues(InputQueue, OutputQueue, FunctionToEvaluate):
    """This function taylors the function FunctionToEvaluate (which is intended to be CPUHeavyFunction) so that it can be used with queues instead of common arguments. InputQueue contains all the arguments (tuples of arguments) for which FunctionToEvaluate is meant to be evaluated. All the returned results will be stored in OutputQueue."""
    while True:
        try:
            TupleOfArguments = InputQueue.get(block=False) # Get the two arguments for one evaluation of FunctionToEvaluate from the queue.
            ReturnedTuple = FunctionToEvaluate(TupleOfArguments[0],TupleOfArguments[1])
            OutputQueue.put(ReturnedTuple)
        except Empty:
            break

# Serial
def Serial(NumberOfWorkers, NumberOfTasks, WeightOfComputation):
    '''This function calls the CPUHeavyFunction NumberOfTasks times. The WeightOfComputation determines the difficulty of each task, since it goes into the NumbersToDraw argument of CPUHeavyFunction. NumberOfWorkers has no purpose in this serial computation and is just used for syntactical reasons.'''
    print('Serial:')
    StartingTime = time.time()
    Output = [CPUHeavyFunction(WeightOfComputation, i) for i in range(NumberOfTasks)] # Here, the CPUHeavyFunction is called and the results are stored in Output. (Actually, we are not interested in the results of the computations of pi, but we have this assignment for completeness.)
    #print(Output[:3]+Output[-3:]) # Optionally, one can have a look at the results.
    EndingTime = time.time()
    print('Number of tasks: %s,    Weight of computation: %s,   Spent time: %.3f s' % (NumberOfTasks, WeightOfComputation, EndingTime-StartingTime))
    return (EndingTime-StartingTime) # Time spent on the computation

# Parallel with multiprocessing.Pool
def UsePool(NumberOfWorkers, NumberOfTasks, WeightOfComputation):
    '''This function distributes NumberOfTasks calls of the CPUHeavyFunction to NumberOfWorkers workers. The WeightOfComputation again determines the difficulty of each task.'''
    print('Using Pool:')
    StartingTime = time.time()
    MyPool = multiprocessing.Pool(processes=NumberOfWorkers)
    Results = [MyPool.apply_async(CPUHeavyFunction, args=[WeightOfComputation, i]) for i in range(NumberOfTasks)]
    Output = [r.get() for r in Results]
    MyPool.close()
    MyPool.join()
    #print(Output[:3]+Output[-3:]) # Optionally, one can have a look at the results.
    EndingTime = time.time()
    print('Number of tasks: %s,    Weight of computation: %s,   Spent time: %.3f s' % (NumberOfTasks, WeightOfComputation, EndingTime-StartingTime))
    return (EndingTime-StartingTime) # Time spent on the computation

# Parallel with multiprocessing.Process
def UseProcess(NumberOfWorkers, NumberOfTasks, WeightOfComputation):
    '''This function distributes NumberOfTasks calls of the CPUHeavyFunction to NumberOfWorkers workers. The WeightOfComputation again determines the difficulty of each task. The input values and the results are communicated via dedicated queues.'''
    print('Using Process:')
    StartingTime = time.time()
    InputQueue = multiprocessing.Queue()
    for i in range(NumberOfTasks):
        InputQueue.put((WeightOfComputation,i))
    OutputQueue = multiprocessing.Queue()
    MyProcesses = [multiprocessing.Process(target=UsingQueues, args=(InputQueue,OutputQueue,CPUHeavyFunction)) for i in range(NumberOfWorkers)]
    for p in MyProcesses:
        p.start()
    Output = [OutputQueue.get() for i in range(NumberOfTasks)]
    #print(Output[:3]+Output[-3:]) # Optionally, one can have a look at the results.
    for p in MyProcesses:
        p.join()
    EndingTime = time.time()
    print('Number of tasks: %s,    Weight of computation: %s,   Spent time: %.3f s' % (NumberOfTasks, WeightOfComputation, EndingTime-StartingTime))
    return (EndingTime-StartingTime) # Time spent on the computation


if __name__ == '__main__':
    NumberOfWorkers = 2
    # In this benchmarking test, the timings of the computations are measured in dependence on the number of tasks as well as in dependence on the weight of each task. Therefore, we specify the maxima of these independent variables.
    MaximalNumberOfTasks = 100 # 100 is a good choice for a simple test of this code. For a more trustworthy (and comparable) run, 1000 could be more appropriate.
    MaximalWeightOfComputation = 800000 # 800000 is a good choice for a simple test of this code. For a more trustworthy (and comparable) run, 8000000 might be a recommended value.
    
    # Caution:
    # Depending on the choice of MaximalNumberOfTasks and MaximalWeightOfComputation, one run of this code can take several CPU-hours. Therefore, for environmental reasons, please only run this code during periods of sunshine, when there is abundance of green electric energy.
    
    MinimalWeightOfComputation = 150
    LogMaximalNumberOfTasks = np.log10(MaximalNumberOfTasks)
    ListOfNumberOfTasks = np.logspace(1,LogMaximalNumberOfTasks,round(LogMaximalNumberOfTasks)+1)
    ColoursOfNumberOfTasks = np.linspace(0,1,num=len(ListOfNumberOfTasks),endpoint=True)
    LogMaximalWeightOfComputation = np.log10(MaximalWeightOfComputation)
    LogMinimalWeightOfComputation = np.log10(MinimalWeightOfComputation)
    ListOfWeightOfComputation = np.concatenate((np.logspace(LogMinimalWeightOfComputation,LogMinimalWeightOfComputation+1,3,endpoint=False),np.logspace(LogMinimalWeightOfComputation+1,LogMaximalWeightOfComputation,round(LogMaximalWeightOfComputation))))

    # Computation:
    # It will be looped through all combinations from ListOfNumberOfTasks and ListOfWeightOfComputation. For each of these combinations, the serial, the multiprocessing-with-Pool and the multiprocessing-with-Process approaches will be applied. For each computation, the timespan needed is saved in a data structure.
    SleepForxSeconds(10)
    Benchmarks = {} # The timings of all the computations are stored in a dictionary of dictionaries.
    for NumOfTasks in ListOfNumberOfTasks:
        NTasks = int(round(NumOfTasks))
        Benchmarks['Number of tasks: %s' % NTasks] = {}
        for WeightOfComp in ListOfWeightOfComputation:
            Weight = int(round(WeightOfComp))
            Benchmarks['Number of tasks: %s' % NTasks]['Weight of computation: %s' % Weight] = {}
            Benchmarks['Number of tasks: %s' % NTasks]['Weight of computation: %s' % Weight]['Serial'] = Serial(NumberOfWorkers,NTasks,Weight)
            SleepForxSeconds(10)
            Benchmarks['Number of tasks: %s' % NTasks]['Weight of computation: %s' % Weight]['Pool'] = UsePool(NumberOfWorkers,NTasks,Weight)
            SleepForxSeconds(10)
            Benchmarks['Number of tasks: %s' % NTasks]['Weight of computation: %s' % Weight]['Process'] = UseProcess(NumberOfWorkers,NTasks,Weight)
            SleepForxSeconds(10)

    # Plot:
    Title = 'Benchmarks for multiprocessing with %s processes\n running on %s' % (NumberOfWorkers,ProcessorModel)
    pl.figure(num=Title, figsize=(11,11))
    pl.title(Title[:52]+'\n'+Title[52:], fontsize=16, fontweight='bold')
    for NumOfTasks, Colour in zip(Benchmarks,ColoursOfNumberOfTasks):
        NTasks = NumOfTasks.split(': ')[1]
        X = []
        YSerial = []
        YPool = []
        YProcess = []
        for WeightOfComp in Benchmarks[NumOfTasks]:
            Weight = WeightOfComp.split(': ')[1]
            X.append(Weight)
            YSerial.append(Benchmarks[NumOfTasks][WeightOfComp]['Serial'])
            YPool.append(Benchmarks[NumOfTasks][WeightOfComp]['Pool'])
            YProcess.append(Benchmarks[NumOfTasks][WeightOfComp]['Process'])
        X = np.asarray(X, dtype=float)
        pl.loglog(X*0.94, YSerial, 'o', color=pl.get_cmap('rainbow')(Colour), label='Serial with %s tasks' % NTasks)
        pl.loglog(X, YPool, 'v', color=pl.get_cmap('rainbow')(Colour), label='Pool with %s tasks' % NTasks)
        pl.loglog(X*1.06, YProcess, 's', color=pl.get_cmap('rainbow')(Colour), label='Process with %s tasks' % NTasks)
    ax = pl.gca()
    ax.xaxis.set_tick_params(labelsize=16)
    ax.yaxis.set_tick_params(labelsize=16)
    pl.xlim(10**np.floor(LogMinimalWeightOfComputation),10**np.ceil(LogMaximalWeightOfComputation))
    if platform.python_version_tuple()[0]=='3':
        pl.legend(loc="best", fontsize=10)
    else:
        pl.legend(loc="best", prop={'size':10})
    pl.xlabel("Weight of computation", fontsize=16)
    pl.ylabel("Spent time in seconds", fontsize=16)
    pl.savefig(Title+' (temporary).svg')


# You can run this code with different NumberOfWorkers. I have tried it on two CPUs with the following findings:
# The following abbreviations are used below:
# t: Evaluation time
# N: Number of processes (called NumberOfWorkers in the code above)
# W: Weight of computation
# T: Number of tasks

# Findings for Intel Core i7-4720HQ @ 2.6 GHz, 4 cores, 8 threads:
# - For big enough W, t is direct proportional to W.
# - For big enough T, t is direct proportional to T.
# - For low T and low W (t < few s), Pool and Process are always the slowest approaches and serial is always the fastest one.
# - For high T and high W, Pool is always faster than serial.
# - Process sometimes seems to not parallelise the work at all, thus sometimes is comparable to the serial approach. (The reason for this is unknown for me, unfortunately.)
# - If Process parallelises, it is comparable to Pool.
# - For Pool and for N<5 and for high enough T and W, the decrease of t with increasing N is about in accordance with the theoretical downscaling expectation t~1/N. For N=5, the decrease of t with increasing N is negligible. For 5<N, t doesn't decrease any more.

# Findings for Intel Core i7-2600 @ 3.4 GHz, 4 cores, 8 threads:
# - For big enough W, t is direct proportional to W.
# - For big enough T, t is direct proportional to T.
# - For low T and low W (t < few 0.1 s), Pool is always the slowest one and Process is about comparable to serial.
# - For high T and high W, Pool is always faster than serial.
# - For low T and high W, Process sometimes seems to not parallelise the work at all, thus sometimes is comparable to the serial approach. (The reason for this is unknown for me, unfortunately.)
# - If Process parallelises, it is comparable to Pool.
# - For N<5 and for high enough T and W, the decrease of t with increasing N is about in accordance with the theoretical downscaling expectation. For N=5, the decrease of t with increasing N is negligible. For 5<N, t doesn't decrease any more.

# Findings for AMD Ryzen Threadripper 2990WX @ 3.0 GHz, 32 cores, 64 threads:
# - For big enough W, t is direct proportional to W.
# - For big enough T, t is direct proportional to T.
# - For low T and low W (t < 0.1 s), Pool is always the slowest one
# - For very low T and very low W (t < few 0.01 s), Process is slower than serial.
# - For high T and high W, Pool is always faster than serial.
# - For N=2, Process sometimes seems to not parallelise the work at all, thus sometimes is comparable to the serial approach. (The reason for this is unknown for me, unfortunately.)
# - If Process parallelises, it is comparable to Pool.
# - For N < about 32 and for high enough T and W, the decrease of t with increasing N is about in accordance with the theoretical downscaling expectation. The more N increases, the more it deviates from the downscaling expectation.
