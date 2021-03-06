import gzip
from subprocess import Popen, PIPE
from collections import Counter
from os import chdir, getcwd, remove, listdir
from os.path import join, isfile
from requests import get
from re import findall
from Bio import SeqIO
from settings.regularExpressions import ENSEMBLE_FTP_REGEX_GET_SPECIES
from settings.directories import GENOME_FOLDER, GENOME_WALK_FOLDER, GENOME_WALK_PATH, ENSEMBL_HTML_PATH, GTF_FOLDER
from settings.links import ENSEMBL_DATA_LINK_PREFIX, ENSEMBLE_FTP_LINK
from myUtils import downloadFromURL
from sys import exit

class ensemblGenome:
    def __init__(self, preLink, name, species):
        self.name = name
        self.preLink = preLink.lower()
        self.species = species
        dataTypes = (
                     ("dna", "fasta", "dna"),
                     ("cdna", "fasta", "cdna"),
                     ("ncrna", "fasta", "ncrna"),
                     ("protein", "fasta", "pep"),
                     ("gtfAnnotation", "gtf", ""),
                     ("gff3Annotation", "gff3", ""),
                     ("genebankAnnotatedSeq", "genebank", ""),
                     ("emblAnnotatedSeq", "embl", ""),
                     ("tsvAnnotation", "tsv", ""),
                     ("rdfAnnotation", "rdf", ""),
                     ("jsonAnnotation", "json", ""),
                     ("WholeDatabase", "mysql", ""),
                     ("gvfVariation", "gvf", ""),
                     ("vcfVariation", "vcf", ""),
                     ("gffRegulation", "regulation", ""),
                     ("regulationDataFiles", "data_files", ""),
                     ("bamBigWig", "bamcov","")
                     )

        self.linkDict = {a[0]: join(ENSEMBL_DATA_LINK_PREFIX, a[1], self.preLink, a[2]) for a in dataTypes}
        self.fileDirectories = {}

    def getGenome(self, folder = GENOME_FOLDER):

        #Downloading ensemble Links for genome
        getLink = self.linkDict["dna"]
        print(getLink)
        raw = get(getLink,verify=False).text
        genomeLink = join(getLink, findall("=\"(.*?sm.toplevel.fa.gz)",raw)[0])
        print(genomeLink)

        genomeAlreadyDownloaded = False
        for f in listdir(GENOME_FOLDER):
            print("downloaded",join(GENOME_FOLDER, f))
            if self.preLink.lower() in f.lower():
                genomeAlreadyDownloaded = True
                self.fileDirectories["dna"] = join(GENOME_FOLDER,f)

        if isfile(join(GENOME_FOLDER, genomeLink.split('/')[-1])):
            genomeAlreadyDownloaded = True
            self.fileDirectories["dna"] = join(GENOME_FOLDER, genomeLink.split('/')[-1])

        if not genomeAlreadyDownloaded:
        #Download Genome
            old = getcwd()
            chdir(folder)
            self.fileDirectories["dna"] = join(GENOME_FOLDER,downloadFromURL(genomeLink))
            chdir(old)
            print("GenomeDownloaded")
        else:
            print("GENOME ALREADY DOWNLOADED")

    def parseGenome(self):

        self.chromossomes = {}
        print("Parsing",self.fileDirectories["dna"])
        genomeHandler = gzip.open(self.fileDirectories["dna"], "rt")
        genomeIterator = SeqIO.parse(genomeHandler, "fasta")
        self.baseCounter = Counter()
        self.genomeBaseData = Counter()
        self.softMaskSizes = Counter()
        for c in genomeIterator:
            print("Parsing", c.id)
            sequence = str(c.seq)
            self.chromossomes[c.id] = len(sequence)
            maskedSize = 0

            for n in sequence:
                self.genomeBaseData[n] +=1
                if n.islower():
                    maskedSize +=1
                else:
                    if maskedSize > 0:
                        self.softMaskSizes[maskedSize] +=1
                        maskedSize = 0

    def getGtf(self):
        getLink = self.linkDict["gtfAnnotation"]
        raw = get(getLink,verify=False).text
        gtfLink = None
        try:
            gtfLink = findall("=\"(.*?\\.chr\\.gtf\\.gz)",raw)[0]
        except:
            gtfLink = findall("=\"(.*?\\.gtf\\.gz)",raw)[0]

        genomeAlreadyDownloaded = False
        for f in listdir(GTF_FOLDER):
            print("downloaded",join(GTF_FOLDER, f))
            if self.preLink.lower() in f.lower():
                genomeAlreadyDownloaded = True
                self.fileDirectories["gtfAnnotation"] = join(GTF_FOLDER,f)

        if isfile(join(GTF_FOLDER, gtfLink.split('/')[-1])):
            genomeAlreadyDownloaded = True
            self.fileDirectories["gtfAnnotation"] = join(GTF_FOLDER, gtfLink.split('/')[-1])

        if not genomeAlreadyDownloaded:
            old = getcwd()
            chdir(GTF_FOLDER)
            self.fileDirectories["gtfAnnotation"] = join(GTF_FOLDER, downloadFromURL(join(getLink, gtfLink)))
            chdir(old)
        else:
            print("GTF FILE ALREADY DOWNLOADED")

    def runGenomeWalk(self):
        blastOutFile = join(GENOME_WALK_FOLDER, self.preLink + ".gw")
        blastControlOutFile = join(GENOME_WALK_FOLDER, self.preLink + "_control.gw")

        if not blastOutFile in self.fileDirectories:
            if not "gtfAnnotation" in self.fileDirectories:
                try:
                    self.getGtf()
                except:
                    print("error getting gtf for " + self.name)
                    exit(0)
            if not "dna" in self.fileDirectories:
                try:
                    self.getGenome()
                except:
                    print("error getting genome for " + self.name)
                    exit(0)
            try:
                 p = Popen(
                      ["python3", GENOME_WALK_PATH,
                      self.fileDirectories["dna"],
                      self.fileDirectories["gtfAnnotation"],
                      blastOutFile,
                      blastControlOutFile],
                      stdout = PIPE)
                 p.wait()
                 remove(self.fileDirectories["dna"])
                 remove(self.fileDirectories["gtfAnnotation"])
                 self.fileDirectories.pop("dna")
                 self.fileDirectories.pop("gtfAnnotation")
            except:
                pass
        self.fileDirectories.pop("gtfAnnotation")

def getEnsemblGenomes():
    h = open(ENSEMBL_HTML_PATH)
    ensembleHtmlData = h.read()
    h.close()
    return list([ensemblGenome(*a) 
            for a in findall(ENSEMBLE_FTP_REGEX_GET_SPECIES, ensembleHtmlData)])
