#################################################
###   Demonstration of the Usage of Process   ###
#################################################

# Purpose of these code snippets is to show the capabilities and the way of using of the Process class of the multiprocessing package.


import multiprocessing
import random
import numpy as np
import time
from queue import Empty


### Specification of parameters

N = 60000000   # Number of random numbers to add
NumberOfProcesses = 4   # Number of processes to use as workers. This should not be higher than the number of available CPU-cores.


### Definition of CPU-heavy functions

def SumRandomNumbers(NumberOfValuesToAdd, ID, OutputQueue):
    """Sum up NumberOfValuesToAdd random numbers. This is a CPU-heavy operation. ID is just a name to identify each call of this function."""
    Sum = 0
    for i in range(int(NumberOfValuesToAdd)):
        Sum += random.random()
    OutputQueue.put((ID, Sum)) # When using the Process class, one cannot use return to propagate the results of the function calls. Instead, we have to put the ID and the Sum into an output queue which in the end will store all the results.

def JobToSumRandomNumbersRepeatedly(InputQueue, JobID, OutputQueue):
    """This is a repeated calling of the above SumRandomNumbers function. Once this function is called it runs and does the following: It fetches an input value from the InputQueue. This input value is used to determine NumberOfValuesToAdd for an addition of random numbers. Then this addition is computed. Then, it puts the resulting sum into the OutputQueue. If at some point an exception arises saying that the InputQueue is empty, it leaves the while loop and stops working. This function is also CPU-heavy because it is based on SumRandomNumbers."""
    while True:
        try:
            InputValue = InputQueue.get(block=False) # Get the next input value from the InputQueue. It is necessary to set block=False. This prevents the InputQueue to be blocked. If you set block=True, the queue gets blocked and in this case other workers which run simultaneously could not fetch values from this queue.
            NumberOfValuesToAdd = InputValue*N/25 # The right-hand side is chosen quite arbitrarily to get an appropriate NumberOfValuesToAdd, which however differs for each call of SumRandomNumbers.
            SumRandomNumbers(NumberOfValuesToAdd, (JobID, int(InputValue)), OutputQueue) # Call the usual function to sum up random numbers and to store the result in the OutputQueue
        except Empty:
            break


if __name__ == "__main__":


### Some different computations, showing the benefits of parallelisation:

# 1. Case: Serial computation
    print('Addition of random numbers, serial approach:') # First, go ahead without multiprocessing.
    StartingTime = time.time()
    QueueOfResults = multiprocessing.Queue() # Define an output queue. This queue will fetch all the results of the function calls.
    [SumRandomNumbers(N, i, QueueOfResults) for i in range(1,NumberOfProcesses+1)] # Assemble all the tasks (function calls) that we want to run and execute them. The results of the tasks will be stored in the QueueOfResults. (In this introductory example, we use NumberOfProcesses also as the number of tasks to be performed. However, in real life the number of tasks will be different from the number of available processes, see case 3 below....)
    Results = [QueueOfResults.get() for p in range(1,NumberOfProcesses+1)] # Get the results from the output queue.
    print(Results)
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print('Time spent on the computation:', TimeInterval, '\n')

# 2. Case: Parallel computation
    print('Addition of random numbers, parallel approach:') # Second, make use of multiprocessing.
    StartingTime = time.time()
    QueueOfResults = multiprocessing.Queue() # Define an output queue, again. The functions called by the several processes put their output into this queue.
    Jobs = [multiprocessing.Process(target=SumRandomNumbers, args=(N, i, QueueOfResults)) for i in range(1,NumberOfProcesses+1)] # Setup a list of tasks that we want to run. (Each task is executed by a separate worker and in this example each worker executes exactly one task.)
    for j in Jobs:
        j.start() # Run the tasks in the workers.
    Results = sorted([QueueOfResults.get() for j in Jobs]) # Get the results from the output queue. Using sorted(...) sorts the results along the job ID.
    print(Results)
    for j in Jobs:
        j.join() # Exit the completed processes. Make sure to .get() before to .join() to prevent a deadlock.
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print('Time spent on the computation:', TimeInterval, '\n')
# In comparison with case 1, it might be obvious that the parallel approach brings a speed-up of the entire evaluation.
# In this example, NumberOfProcesses workers are created and each one gets exactly one task. In real life there will however be the situation that you have many more tasks to be performed than workers (CPU-cores) available. Therefore you have to construct workers that not only exist for the execution of one single task, but instead exist and work until a whole list (queue) of tasks is worked through.

# 3. Case: Serial computation of lots of tasks using an input queue
    print('Addition of random numbers, lots of tasks with input queue, serial approach:') # Third, do a serial approach but use an input queue.
    StartingTime = time.time()
    QueueOfInputValues = multiprocessing.Queue() # This queue will be filled with all the input values for the various tasks to be performed.
    for i in np.linspace(1, 25, 25):
        QueueOfInputValues.put(i) # Put 25 numbers from 1 till 25 into the queue.
    NumberOfTasks = QueueOfInputValues.qsize() # Determine the number of input values in the queue, which just is the number of tasks to be performed.
    QueueOfResults = multiprocessing.Queue() # Define an output queue, again.
    JobToSumRandomNumbersRepeatedly(QueueOfInputValues, 1, QueueOfResults) # One call of this function starts a job. This job fetches the input values from the QueueOfInputValues, performs all the tasks and gives the results into the QueueOfResults.
    Results = [QueueOfResults.get() for p in range(1,NumberOfTasks+1)] # Get the results from the output queue. (This assumes that the number of items in the output queue is equal to the number of items in the originally filled input queue.)
    print(Results)
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print('Time spent on the computation:', TimeInterval, '\n')

# 4. Case: Parallel computation of lots of tasks using an input queue
    print('Addition of random numbers, lots of tasks with input queue, parallel approach:') # Fourth, make use of multiprocessing again.
    StartingTime = time.time()
    QueueOfInputValues = multiprocessing.Queue() # This queue will be filled with all the input values for the various tasks to be performed.
    for i in np.linspace(1, 25, 25):
        QueueOfInputValues.put(i) # Put 25 numbers from 1 till 25 into the queue.
    NumberOfTasks = QueueOfInputValues.qsize() # Determine the number of input values in the queue, which just is the number of tasks to be performed by all the workers together.
    QueueOfResults = multiprocessing.Queue() # Define an output queue, again. The functions called by the several workers, put their output into this queue.
    Jobs = [multiprocessing.Process(target=JobToSumRandomNumbersRepeatedly, args=(QueueOfInputValues, i, QueueOfResults)) for i in range(1,NumberOfProcesses+1)] # Setup a list of jobs that we want to run. (Each job is executed by a separate worker and each worker executes exactly one job. By this each worker executes lots of tasks. As soon as one worker has finished a task, it immediately starts with the next task (provided that there are still items remaining in the input queue).)
    for j in Jobs:
        j.start() # Run the jobs.
    Results = sorted([QueueOfResults.get() for p in range(1,NumberOfTasks+1)]) # Get the results from the output queue. Using sorted(...) sorts the results along the job ID.
    print(Results) # The list of results contains items which are comprised out of the following format ((ID of the job/worker, Input value / ID of the task), Resulting sum of the random numbers).
    for j in Jobs:
        j.join() # Exit the completed processes. Make sure to .get() before to .join() to prevent a deadlock.
    EndingTime = time.time()
    TimeInterval = (EndingTime-StartingTime)
    print('Time spent on the computation:', TimeInterval, '\n')
# Again, one realises the benefits of multiprocessing.
# In comparison to the Pool class, the Process class has the disadvantage that the functions to be applied (SumRandomNumbers in the present case) have to be embedded into another function (JobToSumRandomNumbersRepeatedly in the present case) so that the communication can take place via the queues. In the Pool class, the inter-process communication is easier to accomplish.