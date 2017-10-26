#!/usr/bin/env python
# encoding: utf-8

import solver_tools

name = "ReplacementPresort"

def run(testSet):
	pages = solver_tools.Pagination(testSet["capacity"], name)
	pool = [solver_tools.Tile(tile) for tile in testSet["tiles"]]
	pool.sort(key=lambda tile:tile.size,reverse=True)
	for tile in pool:
		tile.forbiddenPages = []
	tile = pool.pop(0)
	# print "Place tile %s on empty page" % tile
	pages.newPage(tile)
	while pool:
		tile = pool.pop(0)
		# print "Forbidden pages: %s" % str([pages.index(page) for page in tile.forbiddenPages])
		candidates = set(pages).difference(tile.forbiddenPages)
		if not candidates:
			# print "Place tile %s on empty page %s " % (tile,len(pages))
			pages.newPage(tile)
			continue
		(bestWeightedCost,bestPage) = min((tile.weightedCostIn(page),page) for page in candidates)
		if bestWeightedCost == len(tile):
			# print "Place tile %s on empty page %s " % (tile,len(pages))
			pages.newPage(tile)
			continue
		# print "Add tile %s on page %s" % (tile,pages.index(bestPage))
		bestPage.add(tile)
		while bestPage.cost > pages.capacity:
			# print "Page %s exceeded!" % pages.index(bestPage)
			minEfficiency = min(bestPage.actualEfficiencies)
			maxEfficiency = max(bestPage.actualEfficiencies)
			# print (minEfficiency,maxEfficiency)
			if minEfficiency == maxEfficiency:
				break
			tile = bestPage[bestPage.actualEfficiencies.index(minEfficiency)]
			# print "Remove tile %s from page %s" % (tile,pages.index(bestPage))
			bestPage.remove(tile)
			tile.forbiddenPages.append(bestPage)
			pool.append(tile)
		# print "Page %s not saturated." % pages.index(bestPage)
	for i in xrange(len(pages)-1,-1,-1):
		if pages[i].cost > pages.capacity:
			pool.extend(pages.pop(i)[:])
	for tile in pool:
		for page in pages:
			if tile.canFitIn(page):
				page.add(tile)
				break
		else:
			pages.newPage(tile)
	# print pages
	return pages

