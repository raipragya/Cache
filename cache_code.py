import matplotlib.pyplot as plt #for plotting graphs
import numpy as np #for math operations
from tabulate import tabulate as tbl #to format tables

#BlockLine represents each block in a line(set)

class BlockLine:
    def __init__(self):
        self.t_recent_access = 0 #tracks when block was last accessed , its basically used to implement the LRU policy
        self.bitvalid = False #if block has valid data
        self.tag = None #store tag

#EachSet signifies a set in the cache
class EachSet:
    def __init__(self,ways):
        #a list of BlockLine objects
        self.blocks = []
        for _ in range(ways):
            self.blocks.append(BlockLine())
        self.flag_cnt = 0 #counter to keep track of access order for implementing the LRU policy

#implement LRU policy
#compares the t_recent_access , find index of block with least recent access time
    def get_lru_index(self):
        i_lru = 0
        t_min_access = self.blocks[0].t_recent_access


        i = 1
        while i < len(self.blocks):
            if (self.blocks[i].t_recent_access < t_min_access):
                i_lru = i
                t_min_access = self.blocks[i].t_recent_access
            i = i + 1

        return i_lru

#update access time for the block at index ind and increment flag_cnt
    def each_block_access(self,ind):
        self.blocks[ind].t_recent_access = self.flag_cnt
        self.flag_cnt +=1


#represents the full cache
class Cache:
    def __init__(self,number_of_sets,number_of_ways,blockSize):
        self.Sets = [] #list of EachSet objects
        for _ in range(number_of_sets):
            self.Sets.append(EachSet(number_of_ways))
        self.number_of_ways = number_of_ways
        self.blockSize = blockSize

#accessing a memory address
    def mem_access(self,addr):
        blockSize = self.blockSize #block size
        number_of_offsetBits = int(np.log2(blockSize)) #byte offset bits

        number_of_sets = len(self.Sets) #number of sets or lines 
        number_of_indexBits = int(np.log2(number_of_sets)) #index bits


        addressBits = 32 #given
        #calculate number of tag bits
        tagBits = addressBits - number_of_offsetBits - number_of_indexBits

        #extract only the tag from the full address
        shiftedAddressForTag = addr >> (number_of_offsetBits + number_of_indexBits)

        tm = (1 << tagBits) - 1
        tag = shiftedAddressForTag & tm

        #extract only the index bits from the full address
        shiftedAddressForIndex = addr >> number_of_offsetBits

        im = (1 << number_of_indexBits) - 1
        index = shiftedAddressForIndex & im


        #access the particular set using the index
        cs = self.Sets[index]

#check if the block is valid and if the tag matches the address tag
#its a hit
        for i in range(len(cs.blocks)):
            l = cs.blocks[i]
            if l.bitvalid == True and l.tag == tag:
                cs.each_block_access(i) #update the access time(for LRU policy)
                return True

#for a miss in the cache
#if bitvalid is False then update tag into the block and set bitvalid field to be True
        for i in range(len(cs.blocks)):
            l = cs.blocks[i]
            if l.bitvalid == False:
                l.tag = tag
                l.bitvalid = True
                cs.each_block_access(i)
                return False


#implement the LRU policy and if no empty block is found then replace the block according to the LRU policy
        lruWay = cs.get_lru_index()
        cs.blocks[lruWay].tag=tag
        cs.each_block_access(lruWay)
        return False
    


#the function Run will process all the addresses from trace file , keeps count of the number of hits and misses in the cache and finally returns the number of hits and misses   
    def Run(self,trace):
        no_of_hits = 0 #initialise number of hits to zero
        no_of_misses = 0 #initialise number of misses to zero
        for a in trace:
            #if access returns True then it is a hit
            if self.mem_access(a) == True:
                no_of_hits += 1
            #otherwise its a miss
            else:
                no_of_misses += 1
        return no_of_hits,no_of_misses


#Read trace files which store memory addresses
#after reading through the entire file, the function loadTrace will return a list which contains all the addresses in hexadecimal
def loadTrace(filePath):
    addrs = [] #list to store addresses after processing

    with open(filePath, 'r') as f:
        for l in f: #iterate through
            #strip the line of any inital or ending whitespaces
            l = l.strip()

            #split the line into parts , separate by whitespaces
            parts = l.split()

#if the line contains more than one part
            if (len(parts) > 1):
                addr_str = parts[1]

                #convert the address into an integer, treating it as a hexadecimal number (thats why the second argument is 16)
                addr = int(addr_str,16)
                addrs.append(addr)

    return addrs #return the list of addresses



#creates a graph 
#takes in x coordinate (abscissa), y coordinate(ordinate), x asis label, y axis label, title of the graph and legend
def plotGraph(abscissa, ordinate, xAxis, yAxis, title, legend):
    for y,label in zip(ordinate,legend):
        plt.plot(abscissa,y,label=label)
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)
        plt.title(title)
        plt.legend()
        plt.show()


#list of the input trace files
traceFiles = ["gcc.trace","gzip.trace","swim.trace","twolf.trace","mcf.trace"]

#loads traces from trace files given and stores them in traces list
traces = []
for _ in traceFiles:
    traces.append(loadTrace(_))


#prompt the user to enter the part of the program whose execution and results they want to see
user_ip = input("Read the instructions below:\nFor the hit and miss rates of each trace file, enter: a\nFor results on varying cache size, enter: b\nFor results on varying block size, enter: c\nFor results on varying associativity, enter: d\nuser_ip= ")


#initialise a results dictionary to store results of each part a, b, c and d
results={"a":[],"b":[],"c":[],"d":[]}


#32 bit address is given


#4 way set associative cache (1024 kB size, block size 4 bytes )
if user_ip=="a":
    cacheSize = 1024
    blockSize = 4
    ways = 4

#calculate cache size in bytes   
    cacheSizeBytes = cacheSize * 1024

#number of sets = cache size in bytes/(block size * ways)
    sets = cacheSizeBytes // (blockSize * ways)
    cache = Cache(sets,ways,blockSize)

#initialise trace index to 0 to track which trace file is being processed
    traceIndex = 0

#iterate through all traces in list
    for trace in traces:
    #call the Run function
        no_of_hits, no_of_misses = cache.Run(trace)

        hitRate = 100 * no_of_hits / len(trace)
        missRate = 100 * no_of_misses / len(trace)

#store reults in the results dictionary under key "a"
        results["a"].append([f"{ traceFiles[traceIndex] }", "Fixed Config", f"{ hitRate}", f"{ missRate}"])

        traceIndex += 1



#vary cache size from 128kB to 4096kB
#block size is 4 bytes and ways is 4
elif user_ip=="b":
    blockSize = 4
    ways = 4

#list with varying cache sizes from 126kB to 4096kB in powers of 2
    cacheSize = [128,256,512,1024,2048,4096]
    missRates = [] #initialise missRates list to store miss rates  

#iterate through all traces
    for traceIndex in range(len(traces)):
        trace = traces[traceIndex]
#initialise empty list missRatesTrace
        missRatesTrace = []



#iterate through each cache size
#cacheIndex keeps track of current cache size which is being processed
        for cacheIndex in range(len(cacheSize)):
            size = cacheSize[cacheIndex] #size

        #size in bytes
            sizeBytes = size * 1024

        #number of sets
            sets = sizeBytes // (blockSize * ways)

        #creating a cache object with the parameters calculated 
            Cache1 = Cache(sets, ways, blockSize)


            #call the Run function
            no_of_hits, no_of_misses = Cache1.Run(trace)
            hitRate = 100 * no_of_hits / len(trace)
            missRate = 100 * no_of_misses / len(trace)

#appends the miss rate for the particular current acache size to the missRatesTrace
            missRatesTrace.append(missRate)

            #store results in results dictionary under key "b"
            results["b"].append([f"{traceFiles[traces.index(trace)]}",f"Cache Size: {size} KB", f"{hitRate:.5f}", f"{missRate:.5f}"])

#appends missRatesTrace to the missRates list
        missRates.append(missRatesTrace)

#plot graph
#cache size is on the x axis, miss rates of each trace on y axis

    plotGraph(cacheSize, missRates, "Cache Size (KB)", "Miss Rate (%)", "Miss Rate vs Cache Size", ["gcc.trace","gzip.trace","swim.trace","twolf.trace","mcf.trace"])

#vary block size from 1 byte to 128 bytes
#cache size = 1024 bytes, ways = 4
elif user_ip=="c":
    cacheSize = 1024
    cacheSizeBytes = cacheSize * 1024
    ways = 4

#list of block sizes
    blockSizes = [1,2,4,8,16,32,64,128]
    missRates = [] #initialise missRates list to store miss rates

#iterate through all traces
    for trace in traces:
        missRatesTrace = [] #store miss rates for each trace 
        for blockSize in blockSizes: #blockSize represents the current block size being processed

            #number of sets
            sets = cacheSizeBytes//(blockSize * ways)

            #initialise a new cache object with calculated parameters
            Cache2 = Cache(sets, ways, blockSize)

            #call the Run function
            no_of_hits,no_of_misses = Cache2.Run(trace)
            hitRate = 100 * no_of_hits / len(trace)
            missRate = 100 * no_of_misses / len(trace)

            #append miss rate for the current block size to missRatesTrace
            missRatesTrace.append(missRate)

            #store results under key "c"
            results["c"].append([f"{traceFiles[traces.index(trace)]}",f"Block Size: {blockSize} Bytes" , f"{hitRate:.5f}", f"{missRate:.5f}"])
#store miss rates for all trace files and all block sizes
        missRates.append(missRatesTrace)

#plot graph of block size on x axis and miss rates on y axis
    plotGraph(blockSizes, missRates, "Block Size (Bytes)", "Miss Rate (%)", "Miss Rate vs Block Size", ["gcc.trace","gzip.trace","swim.trace","twolf.trace","mcf.trace"])

#vary associativity from 1 to 64
#cache size = 1024 kB
#block size = 4 bytes
elif user_ip=="d":
    cacheSize = 1024
    cacheSizeBytes = cacheSize * 1024
    blockSize = 4
    associativities = [1,2,4,8,16,32,64]
    hitRates = [] #initialise list
    for trace in traces:
        hitRatesTrace = []
        for a in associativities:
            #number of sets
            sets = cacheSizeBytes // (blockSize * a)

            #new cache object
            Cache3 = Cache(sets, a, blockSize)

            #call the Run function
            no_of_hits, no_of_misses = Cache3.Run(trace)
            hitRate = 100 * no_of_hits / len(trace)
            missRate = 100 * no_of_misses / len(trace)

            #append hit rate for current associativity
            hitRatesTrace.append(hitRate)

            #store results under key "d"
            results["d"].append([f"{traceFiles[traces.index(trace)]}",f"Associativity: {a}", f"{hitRate:.5f}", f"{missRate:.5f}"])

#sores hit rates for all trace files and all associatives 
        hitRates.append(hitRatesTrace)
    plotGraph(associativities, hitRates, "Associativity", "Hit Rate (%)", "Miss Rate vs Associativity", ["gcc.trace","gzip.trace","swim.trace","twolf.trace","mcf.trace"])

#invalid input
else:
    print("Invalid input. Input must be a, b, c or d")

#plot results in a formatted table
if user_ip in results and results[user_ip]:
    print(f"\nResults for Part {user_ip.upper()}:")
    print(tbl(results[user_ip], headers=["Trace", "Config", "Hit Rate", "Miss Rate"], tablefmt="grid"))