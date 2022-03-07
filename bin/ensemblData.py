
from os import chdir, getcwd, remove
from os.path import join
from requests import get
from re import findall

from settings.regularExpressions import ENSEMBLE_FTP_REGEX_GET_SPECIES
from settings.directories import GENOME_FOLDER, GENOME_WALK_FOLDER, ENSEMBL_HTML_PATH
from settings.links import ENSEMBL_DATA_LINK_PREFIX, ENSEMBLE_FTP_LINK
from myUtils import downloadFromURL


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
        
    def getGenome(self, folder):

        #Downloading ensemble Links for genome
        raw = get(join(ENSEMBL_DATA_LINK_PREFIX,self.linkDict["dna"])).text
        genomeLink = findall("=\"(.*?sm.toplevel.fa.gz)",raw)[0]
        
        #Download Genome
        old = getcwd()
        chdir(folder)
        self.fileDirectories["dna"] = downloadFromURL(genomeLink)
        chdir(old)
        
        #gettinGenomeData
        self.chromossomes = {}
        genomeIterator = SeqIO.parse(self.fileDirectories["dna"], "fasta")
        self.baseCounter = Counter()
        self.genomeBaseData = {} 
        self.softMaskSizes = Counter()
        for c in genomeIterator:
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


        self.genomeSize = sum(list(self.chromossomes.items()))



    def getGtf(self,folder):

        raw = requests.get(join(ENSEMBL_DATA_LINK_PREFIX,self.linkDict["gtfAnnotation"])).text
        genomeLink = findall("=\"(.*?\\.chr\\.gtf\\.gz)",raw)[0]
        old = getcwd()
        chdir(folder)
        self.fileDirectories["gtfAnnotation"] = downloadFromURL(genomeLink)
        chdir(old)
  
    def runGenomeWalk(self):
        blastOutFile = join(GENOME_WALK_FOLDER, self.preLink + ".gw")
        blastControlOutFile = join(GENOME_WALK_DIR, self.preLink + "_control.gw") 
            
        if not blastOutFile in self.fileDirectories:             
            if not "gtfAnnotation" in self.fileDirectories:
                try:
                    self.getGtf()
                except:
                    print("error getting gtf for " + self.name)
            if not "dna" in self.fileDirectories:
                try:
                    self.getGenome()
                except:
                    print("error getting genome for " + self.name)     
   
            p = Popen(
                      ["python3", GENOME_WALK_DIR,
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

def getEnsemblGenomes():
    h = open(ENSEMBL_HTML_PATH)
    ensembleHtmlData = h.read()
    h.close()
    return list([ensemblGenome(*a) 
            for a in findall(ENSEMBLE_FTP_REGEX_GET_SPECIES, ensembleHtmlData)