from os import environ
from os.path import join

GENOME_FOLDER = join(environ.get("HOME"), "data", "genomes")
GENOME_WALK_FOLDER = join(environ.get("HOME"), "data", "genomes")
REPEAT_MASK_FOLDER = join(environ.get("HOME"), "data", "repeatMasker")
REV_BLAST_PATH = join(environ.get("HOME"), "GenomeBlast/bin/revBlast.py")
BLAST_REV_TEMP_DIR = join(environ.get("HOME"), "bin", "temp")
