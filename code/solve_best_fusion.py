#!/usr/bin/env python
# encoding: utf-8

import solver_tools

name = "BestFusion"

def run(testSet):
	pages = solver_tools.Pagination(testSet["capacity"], name)
	tiles = solver_tools.Batch(testSet["tiles"])
	for tile in tiles:
		candidates = [page for page in pages if tile.canFitIn(page)]
		if candidates:
			(minWeightedCost,bestPage) = min((tile.weightedCostIn(page),page) for page in candidates)
			if minWeightedCost < len(tile):
				bestPage.add(tile)
			else:
				pages.newPage(tile)
		else:
			pages.newPage(tile)
	return pages

