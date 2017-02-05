import os
import numpy as np
import random
import math
import datetime
import timeit


#set working directory
os.chdir("/Volumes/Joe/Projects/PYSimAnneal")

#Random SubTour reversal, indexing from 1
def Sub_Tour_Rev(ListTour, StartVal, EndVal):
    if StartVal > len(ListTour) or EndVal > len(ListTour):
        return "Error: Tour start or end values too high"
    elif EndVal <= StartVal:
        return "Error: Endval before StartVal"
    else:
        TempTour = ListTour[StartVal-1:EndVal]
        TempTour.reverse()
        TempTour = ListTour[:StartVal-1] + TempTour + ListTour[EndVal:]
    return TempTour

#Dictionary of locations indices to text names
def GetDestNames(DestInFile):
    Dests = {}
    with open(DestInFile) as f:
        Dests = {int(k): v for line in f for (k, v) in (line.strip().split(",", 1),)}
    return Dests

#Initial test sequence, home at start and end
def InitialiseSeq(NumElem,Home):
    TempSeq = [i1 for i1 in range(1,Home)] + \
           [i1 for i1 in range(Home + 1, NumElem + 1)]
    random.shuffle(TempSeq)
    return [Home] + TempSeq + [Home]

#Distance of a route
def CostFunc(Route, Dists):
    TempCost = float(0)
    for i2 in range(1,len(Route)):
        TempCost = float(Dists[Route[i2]-1,Route[i2 - 1]-1]) + TempCost
    return TempCost

#Temperature schedule, reducing by a multiple after NumEach iters NumTemps times
def CreateIterSched(InitCostVal,InitMult,SubsMult,NumEach,NumTemps):
    TempSched = [0]*(NumEach*NumTemps)
    for idx, val in enumerate(TempSched):
        if idx < NumEach:
            TempSched[idx] = InitMult*InitCostVal
        else:
            TempSched[idx] = SubsMult*TempSched[idx - NumEach]
    return TempSched


#Initial Vars
DestDic = GetDestNames("DestList.csv")
DistVals = np.genfromtxt("DistTab.txt")

HomeLoc = 16
CurrSeq = InitialiseSeq(len(DestDic),HomeLoc)
BestSeq = CurrSeq
CurrCost = CostFunc(CurrSeq, DistVals)
BestCost = CurrCost
Iter = CreateIterSched(CurrCost, 0.8, 0.6, 25, 25)

#Algorith execution, repeated many times recording best
start_time = timeit.default_timer()
for times in range(1000):
    for num in range(len(Iter)):
        SubTour_Start = random.randrange(2,len(CurrSeq)-2)
        SubTour_End = random.randrange(SubTour_Start + 1,len(CurrSeq)-1)
        NewSeq = Sub_Tour_Rev(CurrSeq, SubTour_Start, SubTour_End)
        TestCost = CostFunc(NewSeq, DistVals)
        #print num, CurrCost, BestCost
        if TestCost < CurrCost:
            CurrSeq = NewSeq
            CurrCost = TestCost
            if TestCost < BestCost:
                BestCost = TestCost
                BestSeq = NewSeq
        else:
            TestVal = random.random()
            if math.exp((CurrCost - TestCost)/Iter[num-1])>TestVal:
                CurrSeq = NewSeq
                CurrCost = TestCost
        num = num + 1
Run_Time = timeit.default_timer() - start_time

#Output to stdout
print "Solution:"
for i in range(1, len(CurrSeq)):
    print "Step %d: %s to %s - %f miles" %(i, DestDic[BestSeq[i-1]], \
                                           DestDic[BestSeq[i]], \
                                           DistVals[BestSeq[i]-1,BestSeq[i - 1]-1])
print "Total Cost: %f miles" % BestCost

#File Output, timestamped
OutFileName = "SimAnnSol" + str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M")) +".txt"
print "File Output to %s" % OutFileName

with open(OutFileName, "w") as OutFile:
    OutFile.write("Iter \t Start \t End \t Dist \n")
    for k in range(1, len(CurrSeq)):
        OutFile.write(str(k) + "\t" + DestDic[BestSeq[k-1]] + "\t" + DestDic[BestSeq[k]] \
		  + "\t" + str(DistVals[BestSeq[k]-1,BestSeq[k - 1]-1]) + "\n")
    OutFile.write("Total: \t" + str(BestCost))
    OutFile.write(str(Run_Time) + "Seconds")

print "Execution Ended - Processing Time %f Seconds" % Run_Time
