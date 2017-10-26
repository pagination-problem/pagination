#!/usr/bin/env python
# encoding: utf-8

import solver_tools


name = "FirstFit"

def run(testSet):
	pages = solver_tools.Pagination(testSet["capacity"], name)
	tiles = solver_tools.Batch(testSet["tiles"])
	for tile in tiles:
		for page in pages:
			if tile.canFitIn(page):
				page.add(tile)
				break
		else:
			pages.newPage(tile)
	return pages
