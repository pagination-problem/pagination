#!/usr/bin/env python
# encoding: utf-8

import genetic
import random
import solver_tools

name = "GeneticGroup"

def firstFit(pages,tiles):
    for tile in tiles:
        for page in pages:
            if tile.canFitIn(page):
                page.add(tile)
                break
        else:
            pages.newPage(tile)



def run(testSet,**kargs):
    
    def mate(p1,left1,right1,p2,left2,right2):
        pages = solver_tools.Pagination(capacity)
        medianTiles = set(tile for i in xrange(left2,right2) for tile in p2.chromosome[i])
        for i in xrange(0,left1):
            tilesToPlace = p1.chromosome[i].tileSet.difference(medianTiles)
            if tilesToPlace:
                pages.newPage(tilesToPlace)
        for i in xrange(left2,right2):
            pages.newPage(p2.chromosome[i])
        for i in xrange(right1,p1.length):
            tilesToPlace = p1.chromosome[i].tileSet.difference(medianTiles)
            if tilesToPlace:
                pages.newPage(tilesToPlace)
        pool = list(refTiles.difference(tile for page in pages for tile in page))
        pool.sort(key=lambda tile:tile.size,reverse=True)
        firstFit(pages,pool)
        child = Individual(pages)
        child.length = len(pages)
        return child

    class Individual(genetic.Individual):
        
        optimization = "MAXIMIZE"
        separator = ','
        
        def makechromosome(self):
            pages = solver_tools.Pagination(capacity)
            tiles = solver_tools.Batch(refTiles)
            firstFit(pages,tiles.getShuffledClone())
            self.length = len(pages)
            return pages
        
        def evaluate(self, optimum = None):
            # print self.length,
            self.score = sum((page.weight/maxPageWeight)**2 for page in self.chromosome)/self.length
            # NB. This should be equivalent to the faster formula:
            # self.score = sum(page.weight*page.weight for page in self.chromosome)/self.length/maxPageWeight/maxPageWeight
            # print self.score
        
        def mutate(self,gene):
            tiles = self.chromosome.pop(gene)
            firstFit(self.chromosome,tiles)
            self.length = len(self.chromosome)
        
        def crossover(self,other):
            if self is other or self.length < 3 or other.length < 3:
                return (self,other)
            left1 = random.randrange(1,self.length-1)
            right1 = random.randrange(left1+1,self.length)
            left2 = random.randrange(1,other.length-1)
            right2 = random.randrange(left2+1,other.length)
            return mate(self,left1,right1,other,left2,right2), mate(other,left2,right2,self,left1,right1)
        
        def copy(self):
            twinPagination = solver_tools.Pagination(capacity)
            for page in self.chromosome:
                twinPagination.newPage(page)
            twin = Individual(twinPagination)
            twin.length = self.length
            twin.score = self.score
            # print "twin", twin.score
            return twin
    
    capacity = testSet["capacity"]
    refTiles = solver_tools.Batch(testSet["tiles"])
    maxPageWeight = float(sum(sorted(refTiles.weightBySymbol.values(),reverse=True)[:capacity]))
    pages = solver_tools.Pagination(capacity, name)
    env = genetic.Environment(Individual,**kargs)
    min_size_at_start = min(len(x.chromosome) for x in env.population)
    refTiles = set(tile for tile in refTiles)
    env.run()
    for page in env.best.chromosome:
        pages.newPage(page)
    return pages



if __name__=="__main__":
    import solve
    solve.main()