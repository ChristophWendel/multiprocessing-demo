################################################################
###   Manipulating Shared Data via multiprocessing.manager   ###
################################################################

# There might be problems of the following manner: You have set up several processes running on various CPU-cores. The processes perform a long algorithm. This algorithm continuously produces results which are to be stored in a data structure. Additionally, the algorithm collects and uses results from other processes that are stored in the data structure. As soon as the algorithm in one of the processes has computed a new result, it is to be communicated to the other processes so that the algorithms running in these processes can utilise this new result. An example for such a problem is an iterative-like computation, where the computation of new values builds upon previous results. The more previous results the iterative algorithm can utilise, the more accurate the next value will be.
# Such structures that can share data between concurrently running processes are provided by the Manager class of multiprocessing. In this code snippet shows how multiprocessing.manager can be used to store data in a dictionary of dictionaries and how to resolve one possible caveat.
# The caveat is the following: When using a nested manager's dictionary (a dictionary of dictionaries), it is not possible to directly mutate the interior dictionary. As a workaround, one has to assign the interior dictionaries to a new, temporary variable, then to modify this variable and then to re-assign the modified variable to the interior dictionary again. (It seems however, that this works only for a once-nested dictionary (dictionary of dictionaries), but not for multiply nested dictionaries.)


import multiprocessing
import pprint
import random


def ComputeNextElementOfLucasSequence(Sequence,P,Q):
    '''This is a placeholder for a CPU-intensive function, which is to be called lots of times. Given the Sequence of numbers (initialised with 0 and 1) as well as integer numbers P and Q, this determines the next element of this Lucas sequence of the first kind.'''
    return P*Sequence[-1] - Q*Sequence[-2]

def Worker(Dict, Key):
    '''This stands for a function which accesses the dictionary Dict (precisely the interior dictionary Dict[Key]) and uses its data to perform a computation. During this computation, Dict (precisely the interior dictionary Dict[Key]) is modified (i.e. the results of the computation are stored).'''
    P=random.randint(1,Key) # This is for the computation of a Lucas sequence. (The right-hand side is arbitrarily chosen.)
    Q=random.randint(-Key,-1) # This, too. (The right-hand side is arbitrarily chosen.)
    while Dict[Key]['CompFinished']==False: # Perform the computation while this is satisfied. See the if-clause below...
        # Now a Lucas sequence is to be computed. The sequence object is stored in Dict[Key]['Sequence']. However, it is not possible to directly access and manipulate Dict[Key]['Sequence'] (because the dictionary is a manager's dictionary). Therefore, instead one has to create a temporary copy of the interior dictionary Dict[Key]. This copy can then be manipulated. After manipulation, one can re-assign the manipulated copy to the original Dict[Key].
        TemporaryDict = Dict[Key] # Create a temporary copy. This is necessary for a proper modification of the interior dictionary Dict[Key].
        TemporaryDict['Sequence'] = TemporaryDict['Sequence'] + [ComputeNextElementOfLucasSequence(TemporaryDict['Sequence'],P,Q)] # Take the current sequence (from the copied dictionary), use its elements to compute the next element of the sequence, append this new element to the sequence and replace the old sequence by the appended sequence.
        Dict[Key] = TemporaryDict # Re-assign the modified temporary dictionary to the original dictionary.
        if Dict[Key]['Sequence'][-1]>=1000: # Here, we specify a (quite arbitrarily chosen) criterion. When this criterion is satisfied, the computation of this sequence is marked as finished.
            TemporaryDict = Dict[Key] # Again, the following three lines are necessary for a proper modification of the interior dictionary.
            TemporaryDict['CompFinished'] = True # Tag the finishing of the computation of the corresponding sequence.
            TemporaryDict['P'] = P # For completeness and reproducibility ...
            TemporaryDict['Q'] = Q # ... also save the parameters P and Q.
            Dict[Key] = TemporaryDict # Reassign the modified dictionary.
            break # Stop the worker that has computed this sequence.

if __name__ == '__main__':
    ListOfKeys = list(range(1,21)) # Assemble the list of values of the independent variable. These values (input values) will be the keys of a dictionary MyDict, which serves as a data structure to contain all the data and results of the parallel computation.
    # Initialise the dictionary MyDict:
    MyDict = {}
    for k in ListOfKeys:
        MyDict[k] = {} # The value of MyDict, corresponding to each key, is supposed to be again a dictionary. This interior dictionary will contain all the data corresponding to one certain key.
        # Initialise the interior dictionaries MyDict[key]. They will have two keys, one called 'Sequence' and the other one called 'CompFinished':
        MyDict[k]['Sequence'] = [0, 1] # Every value corresponding to MyDict[key]['Sequence'] is actually a list containing the starting elements of a mathematical sequence (Lucas sequence of the first kind), with initially two items, 0 and 1.
        MyDict[k]['CompFinished'] = False # Every value corresponding to MyDict[key]['CompFinished'] is a boolean which states, whether the computation of the sequence has already been finished or not. If this boolean gets the value True, the user or the algorithm can easily find out that the computation of the sequence was finished.
    print('MyDict after initialisation:')
    pprint.pprint(MyDict)
    print()
    
    MyManager=multiprocessing.Manager() # Create a manager instance. With this object it is possible to share information between concurrent processes.
    MyManagersDict = MyManager.dict(MyDict) # Initialise a dictionary in the manager based on the original dictionary MyDict. This manager's dictionary in the beginning contains all the information of MyDict. But during the program flow, it can be accessed and manipulated by parallel processes. A process can store data in this dictionary and it can fetch data from this dictionary that other processes have written into the dictionary while the process was already running.
    MyPool = multiprocessing.Pool(processes=int(multiprocessing.cpu_count()/2)) # Initialise a pool of processes. For this purpose, let python get the number of CPU-cores of your system via multiprocessing.cpu_count()/2.
    [MyPool.apply_async(Worker, args=[MyManagersDict, k]) for k in ListOfKeys] # Distribute the tasks to the processes of the pool. The tasks are started automatically and will modify MyManagersDict. (Notice that the function Worker does not return anything, it just modifies the manager's dictionary. Therefore (in contrast to the other demonstration of the Pool class) it is not necessary here to assign this list comprehension to a new object.)
    MyPool.close() # Clear the pool to exit the processes and to...
    MyPool.join() # ...retrieve the used RAM.
    
    MyDict = dict(MyManagersDict) # Map the manager's dictionary back to a common dictionary.
    print('MyDict after computation:') # Look ...
    pprint.pprint(MyDict, width=200) #        ... at it.
