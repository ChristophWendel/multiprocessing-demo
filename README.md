# multiprocessing-demo
These files serve as a beginner's tutorial on the usage of the python multiprocessing module. The aim is to give an overview about how tasks can be parallelised to various CPU cores via the multiprocessing module and to point out possible caveats and to show how to bypass them. It is a practical demonstration for quickly setting up parallel workers.

The five scripts can be used independently of each other, but the recommended ordering of working through them is as follows:

1. MultiprocessingDemonstrationPool.py:
   Here, the Pool class is introduced. As it can be set up quite straightforwardly, it is the easiest implementation of parallelisation within multiprocessing. Its way of usage and its performance is compared to serial approaches, both non-vectorised and vectorised via numpy.

2. MultiprocessingDemonstrationProcess.py:
   The Process class is discussed. Its usage in connection with queues is presented. Again, its way of usage and its timing is compared to serial computations, for non-vectorised as well as for vectorised operations.

3. MultiprocessingDemonstrationBenchmarking.py:
   This script performs a comparison of the timings/performance of your CPU for a given set of standardised computations that are performed both serially, parallelised with the Pool class and parallelised with the Process class. You can assess simple benchmarks and see how the timing depends on the number of used cores as well as on the weight of the tasks.

4. MultiprocessingDemonstrationNestingProcessAndPool.py:
   Here, it is demonstrated how sub-processes can set of sub-processes on their own. This can be helpful if in your algorithm there is not only one point of vantage to parallelise the tasks into sub-tasks but when sub-tasks again pear potential to get divided.

5. MultiprocessingDemonstrationManagerDictOfDicts.py:
   It is exemplarily shown here how the various, concurrently running workers can communicate with each other by manipulating (i.e. storing and retrieving results in) a data structure. This common data structure is a dictionary of dictionaries, in this example.
