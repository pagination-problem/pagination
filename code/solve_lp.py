#!arch -i386 python2.7
# encoding: utf-8

import cplex
import os
import sys
import re,itertools,collections,json

class Logger(object):
	def __init__(self,filename,mode="w"):
		self.out = sys.stdout
		self.log = open(filename, mode)

	def write(self, message):
		self.out.write(str(message))
		self.log.write(str(message))
	
	def flush(self):
		self.out.flush()
		self.log.flush()
	
	def close(self):
		self.log.close()
	

def disableCplexOptimizations(problem):
	problem.parameters.mip.cuts.cliques.set(-1)
	problem.parameters.mip.cuts.covers.set(-1)
	problem.parameters.mip.cuts.disjunctive.set(-1)
	problem.parameters.mip.cuts.flowcovers.set(-1)
	problem.parameters.mip.cuts.gomory.set(-1)
	problem.parameters.mip.cuts.gubcovers.set(-1)
	problem.parameters.mip.cuts.implied.set(-1)
	problem.parameters.mip.cuts.mcfcut.set(-1)
	problem.parameters.mip.cuts.mircut.set(-1)
	problem.parameters.mip.cuts.pathcut.set(-1)
	problem.parameters.mip.cuts.zerohalfcut.set(-1)
	problem.parameters.mip.strategy.search.set(1) # disable dynamic search
	# problem.parameters.randomseed.set(42)

def checkSolution(problem,lpPath):
	rex = re.compile(r"(\d+)_(\d+)")
	paginations = collections.defaultdict(list)
	logger = Logger("cplex2.log","a")
	for (name,value) in itertools.izip(problem.variables.get_names(),problem.solution.get_values()):
		if name.startswith("y") and value==1:
			(tileIndex,pageIndex) = rex.search(name).groups()
			paginations[int(pageIndex)-1].append(int(tileIndex)-1)
	text = open(lpPath).read()
	text = text[text.index("<testSet>")+len("<testSet>"):text.index("</testSet>")].replace("\\ ","")
	testSet = json.loads(text)
	for (pageIndex,pagination) in paginations.iteritems():
		logger.write("Page %s contains %s tiles " % (pageIndex+1,len(pagination)))
		symbols = set()
		for tileIndex in pagination:
			symbols = symbols.union(testSet["tiles"][tileIndex])
		logger.write( "covering %s distinct symbols:\n" % len(symbols))
		logger.write(str([testSet["tiles"][tileIndex] for tileIndex in pagination])+"\n")
	logger.write( "Optimal page count = %s\n" % testSet.get("pageCount","unknown"))
	logger.write( "Solution page count = %s\n" % len(paginations))
	if testSet.get("pageCount") is not None and testSet.get("pageCount")!=len(paginations):
		if testSet.get("pageCount")>len(paginations):
			logger.write("%s\n%s\n%s\n" % ("*"*60, "Better solution!", "*"*60))
			logger.close()
		else:
			logger.write("%s\n%s\n%s\n" % ("*"*60, "Wrong solution!", "*"*60))
			logger.close()
			raise ValueError

def remainingFiles():
	lpSet = set()
	logSet = set()
	for (dirpath, _, filenames) in os.walk("results"):
		for filename in filenames:
			if filename.endswith(".lp"):
				lpSet.add((dirpath,filename[:-3]))
			if filename.endswith(".log"):
				logSet.add((dirpath,filename[:-4]))
	return sorted(list(lpSet.difference(logSet)))
	
def main():
	for (dirpath,filename) in remainingFiles():
		problem = cplex.Cplex()
		logger = Logger("cplex2.log")
		problem.set_results_stream(logger)
		problem.parameters.read.datacheck.set(0)
		disableCplexOptimizations(problem)
		problem.read(os.path.join(dirpath,filename+".lp"))
		logger.write('Solving "%s/%s.lp"\n' % (dirpath,filename))
		problem.solve()
		checkSolution(problem,os.path.join(dirpath,filename+".lp"))
		os.rename("cplex2.log",os.path.join(dirpath,filename+".log"))
	print "All result files generated."

if __name__ == "__main__":
	main()