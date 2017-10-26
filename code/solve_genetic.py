#!/usr/bin/env python
# encoding: utf-8

import genetic
import random
import solver_tools

name = "GeneticSimple"

def firstFit(pages,tiles):
    for tile in tiles:
        for page in pages:
            if tile.canFitIn(page):
                page.add(tile)
                break
        else:
            pages.newPage(tile)

def run(testSet,maxPageCount=None,knownPaginations=[],**kargs):
    
    class Individual(genetic.Individual):
        
        optimization = "MINIMIZE"
        separator = ','
        maxPageCount = 0
        
        def makechromosome(self):
            pages = solver_tools.Pagination(capacity)
            tiles = solver_tools.Batch(refTiles)
            firstFit(pages,tiles.getShuffledClone())
            result = [pages.pageIndexOfTile(tile) for tile in tiles]
            Individual.maxPageCount = max(max(result) + 1, Individual.maxPageCount)
            return result
        
        def evaluate(self, optimum = None):
            symbolsOnPages = [[] for _ in xrange(Individual.maxPageCount)]
            for (tileIndex,pageIndex) in enumerate(self.chromosome):
                symbolsOnPages[pageIndex].extend(refTiles[tileIndex])
            page_costs = [len(set(symbols)) for symbols in symbolsOnPages]
            if max(page_costs)>capacity:
                self.score = invalidPenalty + sum(max(0,n-capacity) for n in page_costs)
            else:
                for i in xrange(Individual.maxPageCount-1,-1,-1):
                    if page_costs[i]:
                        self.score = page_costs[i] + i * capacity
                        break
        
        def mutate(self,gene):
            self.chromosome[gene] = random.randrange(Individual.maxPageCount)
    
    # tiles = solver_tools.Batch(testSet["tiles"])
    capacity = testSet["capacity"]
    refTiles = solver_tools.Batch(testSet["tiles"])
    Individual.length = len(refTiles)
    invalidPenalty = capacity * testSet["tileCount"]
    # if knownPaginations:
    #     maxPageCount = min(len(knownPagination) for knownPagination in knownPaginations if knownPagination.isValid())
    
    # for (knownPaginationIndex,knownPagination) in enumerate(knownPaginations):
    #     if knownPagination.isValid() and len(knownPagination) == maxPageCount:
    #         for (tileIndex,tile) in enumerate(tiles):
    #             env.population[knownPaginationIndex].chromosome[tileIndex] = knownPagination.pageIndexOfTile(tile)
    env = genetic.Environment(Individual,**kargs)
    env.run()
    
    pages = solver_tools.Pagination(testSet["capacity"], name)
    for _ in range(max(env.best.chromosome)+1):
        pages.newPage()
    for (tileIndex,pageIndex) in enumerate(env.best.chromosome):
        pages[pageIndex].add(refTiles[tileIndex])
    return pages
