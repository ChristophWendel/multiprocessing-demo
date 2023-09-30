############################################################
###   How to Set up Child Processes of Child Processes   ###
############################################################

# There might be situations in which you have lots of available CPU-cores, but for reasons connected with the nature of your algorithm it is not possible (not advisable) to assign one task to each of the available workers. Then, you have remaining CPU-cores ready to take additional tasks. In such a case you can divide the original tasks into sub-tasks. Then, each worker (child process of the mother process) to whom a task has been assigned, can set up additional workers (child processes of the child process) to whom the sub-tasks will be assigned. Such a situation will be shown in the following.
# The Process class will be used to set up child process of the mother process and each child process will use the Pool class to set up its own child processes. Such a nesting is possible when starting with the Process class, but it is not possible when starting with the Pool class.


import random
import multiprocessing
import time
from queue import Empty
import numpy as np


### Specification of parameters

ListOfNumbersToAdd = np.linspace(1000000, 6500000, 12) # This is an array of numbers which will be the arguments of the tasks. So, the number of items in this array is the number of talks. (1000000, 6500000, 12) is a good choice for a simple test of this code. For a more trustworthy (and comparable) run,(10000000, 65000000, 12) might be advisable.
NumberOfSubtasksInOneTask = 8 # 8 is a good choice for a simple test of this code. For a more trustworthy (and comparable) run, 64 might be a recommendation. Of course, 64 is somewhat arbitrary. It is however motivated by the following: If a CPU has 64 cores, and NumberOfProcessWorkers is the smallest (namely 1) and NumberOfPoolWorkers is the biggest (namely 64), then each core has one sub-task to execute. If NumberOfProcessWorkers is 2, then each core has two tasks to execute and so on.

# Caution:
# Depending on the choice of ListOfNumbersToAdd and NumberOfSubtasksInOneTask, one run of this code can take several CPU-hours. Therefore, for environmental reasons, please only run this code during periods of sunshine, when there is abundance of green electric energy.

NumberOfProcessWorkers = 2 # Number of workers to create via the Process class. This equals the number of child processes of the mother process.
NumberOfPoolWorkers = 2 # Number of workers to create via the Pool class. This equals the number of child processes that are set up by one child process of the mother process.
# Changing NumberOfProcessWorkers and NumberOfPoolWorkers and running this code, one can compare the timings of each run and by this find the best settings for  NumberOfProcessWorkers and NumberOfPoolWorkers for the given CPU. It is especially instructive to check whether increasing NumberOfProcessWorkers and/or NumberOfPoolWorkers decreases the runtime similarly to the theoretical downscaling or less. For example, one can find the fastest setting or one can find the most efficient setting. 


### Definition of CPU-heavy functions, first for the sub-tasks, afterwards for the tasks

def SumRandomNumbers(WeightedNumbersToAdd, ProcessID, SubTaskNumber):
    '''In short, this is a function that sums up random numbers to mimic a CPU-heavy function. Precisely, first it prints the ID of the process in which it is running, it prints the name of the worker in the pool in which it is running and it prints the number of the sub-task it is performing. These prints are just to keep an overview. Second, it just determines the sum of WeightedNumbersToAdd random numbers. In the following, WeightedNumbersToAdd will be differing between calls of SumRandomNumbers from different tasks. Third, after the computation it again prints all the identifiers. And fourth, it returns the result. In the following, one call of this function is considered as a sub-task.'''
    PoolWorkerID = multiprocessing.current_process().name
    print('%-13s and %-25s: Beginning sub-task number %s.' % (ProcessID, PoolWorkerID, SubTaskNumber))
    Sum = 0.0
    for i in range(WeightedNumbersToAdd):
        Sum += random.random()
    print('%-13s and %-25s: Finished  sub-task number %s.' % (ProcessID, PoolWorkerID, SubTaskNumber))
    return Sum

def JobToPerformTasks(InputQueue, OutputQueue):
    """Draw input-value from the queue. Determine a weight of each computation. Sum up random numbers twice. A CPU-heavy operation! In the following, one call of this function is considered as a job and one workthrough of the try-block is considered as a task."""
    while True: # Do this as long as there are items in InputQueue.
        try:
            NumbersToAdd = InputQueue.get(block=False) # Get the parameter NumbersToAdd from the input queue. (The bigger NumbersToAdd, the more expensive is the computation.) 
            RandomWeight = random.randint(1,3) # This draws random numbers out of the arbitrarily chosen set {1, 2, 3}, which causes a random weight of each computation in the following. This is implemented for illustration purpose because in real-world-problems, different tasks will have different CPU-intensity. If you want to compare the timings of the computations quantitatively, then make sure to remove this random influence, e.g. by setting RandomWeight = random.randint(2,2).
            ProcessID = multiprocessing.current_process().name # The function JobToPerformTasks will be called by the workers created by the Process class. This determines the identifier of the current worker.
            WeightedNumbersToAdd = RandomWeight*int(NumbersToAdd)
            print('%-12s: Beginning computation with NumbersToAdd = %s' % (ProcessID, NumbersToAdd)) # This just says which worker performs which task.
            MyPool = multiprocessing.Pool(processes=NumberOfPoolWorkers) # Set up a pool of NumberOfPoolWorkers workers and start the computation...
            Result = [MyPool.apply_async(SumRandomNumbers,args=[WeightedNumbersToAdd,ProcessID,SubtaskNumber+1]) for SubtaskNumber in range(NumberOfSubtasksInOneTask)] # The summation of WeightedNumbersToAdd random numbers is performed NumberOfSubtasksInOneTask times by the pool of NumberOfPoolWorkers workers.
            ListOfSums = [r.get() for r in Result] # This is the list of sums of all the sub-tasks that just have been performed by the pool of workers.
            MyPool.close() # Finish ...
            MyPool.join() #         ... the computation.
            Sum = int(np.sum(ListOfSums)/(0.5*NumberOfSubtasksInOneTask*RandomWeight)) # Compute the arithmetic mean. The division is necessary, for the result to be the approximate original input NumbersToAdd.
            OutputQueue.put((NumbersToAdd, Sum)) # Feed the pair of NumbersToAdd (the input value of this task) and the resulting sum into the output queue.
            print('%-12s: Finished  computation with NumbersToAdd = %s, Mean sum = %s, Relative deviation = %s\n' % (ProcessID, NumbersToAdd, Sum, (NumbersToAdd-Sum)/NumbersToAdd)) # Just as an information about the accomplishment of this task.
        except Empty:
            break


if __name__ == "__main__":
    
    # Serial computation of all the tasks with all their sub-tasks:
    print('\n\nSerial:\n')
    StartingTime = time.time()
    QueueWithInputValues = multiprocessing.Queue() # Create a queue for the input values.
    for i in ListOfNumbersToAdd:
        QueueWithInputValues.put(i) # And fill the queue with the items from the array.
    NumberOfTasks = QueueWithInputValues.qsize() # The number of items in the queue is just the total number of tasks.
    QueueWithResults = multiprocessing.Queue()
    JobToPerformTasks(QueueWithInputValues, QueueWithResults) # Start one single job, which works through all the tasks (and sub-tasks)
    Results = [QueueWithResults.get() for t in range(NumberOfTasks)] # Retrieve the results from the output queue.
    print(Results)
    EndingTime = time.time()
    TimeIntervalSerial = (EndingTime-StartingTime)
        
    time.sleep(10)
    
    # Parallelised and nested computation of all the tasks with all their sub-tasks:
    print('\n\nMultiprocessing:\n')
    StartingTime = time.time()
    QueueWithInputValues = multiprocessing.Queue() # As above.
    for i in ListOfNumbersToAdd:
        QueueWithInputValues.put(i)
    NumberOfTasks = QueueWithInputValues.qsize() # As above.
    QueueWithResults = multiprocessing.Queue() # As above.
    ListOfProcesses = [multiprocessing.Process(target=JobToPerformTasks, args=(QueueWithInputValues,QueueWithResults)) for i in range(NumberOfProcessWorkers)] # Create the Processes for jobs. Use QueueWithInputValues as input and QueueWithResults as output. Each worker starts a job to contribute in working through all the tasks.
    for p in ListOfProcesses: # Start the processes
        p.start()
    Results = [QueueWithResults.get() for t in range(NumberOfTasks)] # Collect the output.
    print('Results (unordered):\n', Results) # As the different tasks have a randomly chosen CPU-heaviness, their accomplishment takes different timespans. Consequently, it can happen that the computation of one task started after the computation of another task but is finished even earlier. Therefore, the results in the queue are unordered in the first place. The next three lines create an ordered array of results.
    DataType = [('Input-number', float), ('Output-number', float)] # This is the assignment on how the following array will be structured.
    ResultArrayUnordered = np.array(Results, dtype=DataType) # Create a structured array.
    ResultArrayOrdered = np.sort(ResultArrayUnordered, order='Input-number') # Sort along the input value. This is necessary, because the unordered array is unordered because every task can last longer or shorter than the other tasks.
    print('Results (ordered):\n', ResultArrayOrdered)
    for p in ListOfProcesses: # Finish the processes.
        p.join()
    EndingTime = time.time()
    TimeIntervalMulti = (EndingTime-StartingTime)

    print("\nTime spent on the serial computation:", TimeIntervalSerial/60,"minutes\n")
    print("Time spent on the multiprocessing computation:", TimeIntervalMulti/60,"minutes\n")