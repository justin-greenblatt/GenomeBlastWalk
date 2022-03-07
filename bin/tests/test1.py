import sys
from os import environ
from os.path import join
sys.path.insert(1, join(environ.get("HOME"), "Projects/blastGenome/bin"))

import ensemblData
#import genomeWalk
import myUtils
import repeatMaskData
#import revBlast

genomes = ensemblData.getEnsemblGenomes()
rm = repeatMaskData.testData()
print("Yalla Balagan")