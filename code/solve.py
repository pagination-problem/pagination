#!/usr/bin/env python
# encoding: utf-8

import json
import random
import collections
import os
import re
import time

import solver_tools

import solve_ff
import solve_best_fusion
import solve_genetic
import solve_genetic_group
import solve_overload_and_remove
import solve_overload_and_remove_presort

class Benchmark:
    
    def __init__(self):
        self.globalResults = []
        self.globalHeader = None
    
    def newInstance(self,testSet,name,testSetCount):
        print "Solving %s (%s)" % (name,testSetCount)
        self.filename = name
        if "solvers" not in testSet:
            testSet["solvers"] = {}
        if testSet["pageCount"]:
            algoName = re.sub(" \[.+", "", testSet.get("approximation","given"))
            self.instancePaginations = [solver_tools.Pagination(testSet["capacity"],algoName)]
            print "%(pageCount)s pages (current best)" % testSet
            for page in testSet["paginations"]:
                self.instancePaginations[-1].newPage([testSet["tiles"][tileIndex] for tileIndex in page])
            testSet["solvers"][algoName] = testSet["pageCount"]
        else:
            self.instancePaginations = []
        self.testSet = testSet
    
    def add(self, solver, testSet, **kargs):
        # if solver.name in testSet["times"] and testSet["times"][solver.name] < 500:
        #     print "aborted", solver.name
        #     return
        self.dirty = True
        random.seed(42)
        time_1 = time.time()
        pagination = solver.run(testSet, **kargs)
        time_2 = time.time()
        elapsed_time = round(time_2 - time_1, 2)
        rawPageCount = len(pagination)
        pagination.decantPages()
        pagination.decantConnectedComponents()
        pagination.decantTiles()
        print "%s -> %s pages" % (rawPageCount,len(pagination)),
        print ("" if pagination.isValid() else "*** invalid ***")
        self.instancePaginations.append(pagination)
        if pagination.isValid():
            currentPageCount = self.testSet["solvers"].get(pagination.algoName, self.testSet["tileCount"])
            if len(pagination) < currentPageCount:
                self.testSet["solvers"][pagination.algoName] = len(pagination)
                self.dirty = True
        if pagination.algoName not in self.testSet["times"] or elapsed_time < self.testSet["times"][pagination.algoName]:
            self.testSet["times"][pagination.algoName] = elapsed_time
            self.dirty = True
    
    def printInstanceConclusion(self):
        if self.globalHeader is None:
            self.globalHeader = [pagination.algoName for pagination in self.instancePaginations]
        (minPageCount,bestPagination) = min([(len(pagination),pagination) for pagination in self.instancePaginations if pagination.isValid()])
        bestAlgos = set(pagination.algoName for pagination in self.instancePaginations if pagination.isValid() and len(pagination)==minPageCount)
        print "Best algorithms (%s pages): %s" % (minPageCount,", ".join(bestAlgos))
        self.globalResults.append({
            "bestPagination": bestPagination,
            "minPageCount": minPageCount,
            "pageCounts": [(len(pagination) if pagination.isValid() else None) for pagination in self.instancePaginations],
            "bestAlgos": bestAlgos,
        })
        print
    
    def mayUpdateTestSetsWithNewPaginations(self,testSets,filename):
        improvementCount = 0
        for (testSet,result) in zip(testSets,self.globalResults[-len(testSets):]):
            if testSet["pageCount"] == 0 or testSet["pageCount"] > result["minPageCount"]:
                best = result["bestPagination"]
                d = best.getInfo(testSet["tiles"])
                d["approximation"] = "%s [%s]" % (best.algoName,time.strftime('%Y-%m-%d %H:%M:%S'))
                testSet.update(d)
                improvementCount += 1
        text = solver_tools.testSetsToText(testSets)
        if self.dirty:
            open(filename,"w").write(text)
            if improvementCount:
                print "Dumped %s with %s improvement(s)" % (filename,improvementCount)
            else:
                print "Dumped %s" % filename
            print
    
    def printGeneralConclusion(self):
        print "%s\nBest algorithms for these %s instances:\n%s" % ("*"*40,len(self.globalResults),"*"*40)
        bestInstanceCounts = [0] * len(self.globalHeader)
        for (i,name) in enumerate(self.globalHeader):
            for globalResult in self.globalResults:
                if name in globalResult["bestAlgos"]:
                    bestInstanceCounts[i] += 1
            print "%s: %3.2f%%" % (name,100.0*bestInstanceCounts[i]/len(self.globalResults))
    

def files_between(directory_path, min_prefix, max_prefix):
    for name in os.listdir(directory_path):
        if name.endswith(".json") and min_prefix <= name <= max_prefix:
            yield os.path.join(directory_path, name)

def main():
    directory_path = "../gauss"
    min_prefix = "C0"
    max_prefix = "C1"
    b = Benchmark()
    filenames = list(files_between(directory_path, min_prefix, max_prefix))
    random.shuffle(filenames)
    for filename in filenames:
        testSets = json.loads(open(filename).read())
        b.dirty = False
        for (testSetCount,testSet) in enumerate(testSets, 1):
            if "times" not in testSet:
                testSet["times"] = {}
            b.newInstance(testSet,filename,"%s/%s" % (testSetCount,len(testSets)))
            b.add(solve_ff, testSet)
            b.add(solve_genetic, testSet, verbose=False, size=80, maxgenerations=50)
            b.add(solve_best_fusion, testSet)
            b.add(solve_overload_and_remove, testSet)
            # b.add(solve_overload_and_remove_presort, testSet)
            b.add(solve_genetic_group, testSet, size=80, maxgenerations=50, verbose=False)
            b.printInstanceConclusion()
        # b.mayUpdateTestSetsWithNewPaginations(testSets,filename)
    b.printGeneralConclusion()
    

if __name__=="__main__":
    main()
