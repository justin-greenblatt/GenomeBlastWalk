from os import environ
from os.path import join
APLICATION_PATH = join(environ.get("HOME"), "GenomeBlastWalk")
GENOME_FOLDER = join(APLICATION_PATH, "data", "genomes")
GENOME_WALK_FOLDER = join(APLICATION_PATH, "data", "genomes")
REPEAT_MASK_FOLDER = join(APLICATION_PATH, "data", "repeatMasker")
REV_BLAST_PATH = join(APLICATION_PATH,  "/bin/revBlast.py")
BLAST_REV_TEMP_DIR = join(APLICATION_PATH, "data","temp")
ENSEMBL_HTML_PATH = join(APLICATION_PATH, "data","ensemblGenomes.html")
