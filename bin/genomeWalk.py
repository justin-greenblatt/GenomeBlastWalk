#This iterates over the genome and annotation and applies blast on the gene region

from subprocess import Popen, PIPE
import os
import sys
from Bio import SeqIO

#Genome
IN_FILE_GENOME = sys.argv[1]

#GTF
IN_FILE_GTF = sys.argv[2]

#outFile
OUT_FILE = sys.argv[3]

MINUS_GENE_REGION = 2000
PLUS_GENE_REGION = 2000

print("START")

new = open(OUT_FILE,'x')
new.close()

genomeIterator = SeqIO.parse(IN_FILE_GENOME, "fasta")

gtfIterator = open(IN_FILE_GTF, 'r')

flag = True

chromosome = next(genomeIterator, None)
gene = getNextGene(gtfIterator)

def getNextGene(iterator):
	line = next(iterator)
	while line.startswith('#') or line.split('\t')[2] != "gene":
	    line = next(gtfIterator, None)
	    if line == None:
	        sys.exit(0)
	        break

#Start Looping over genome and annotations

while flag:
    
    if chromosome == None:
    	print("END")
    	sys.exit(0)
    	break
    
    #skipComments
    while gene.split('\t')[0] == chromosome.id:
        
        #Getting data of the gene
        geneID = re.search(r'gene_id \"(.+?)\"', text).group(1)
        geneStart = int(gene.split('\t')[3])
        geneEnd = int(gene.split('\t')[4])
        geneStrand = int(gene.split('\t')[6])
        geneSeq = str(chromosome.seq[max(0, geneStart - MINUS_GENE_REGION):min(geneEnd + 2000, len(chromosome.seq))])

        #Writing gene data to temporary file 
        tempFilename = "temp_fasta_" + geneID + '.fa'
        tempGeneFasta = open(tempFilename, 'w')
        fastaHeader = ">" + ",".join([geneID, geneStart, geneEnd, geneStrand]) + "\n"
        tempGeneFasta.write(fastaHeader)
        tempGeneFasta.write(geneSeq)
        tempGeneFasta.close()
    
        #Running revBlast on gene
        command = ["sudo", "python3", REV_BLAST_PATH, tempFilename, OUT_FILE]
        p = Popen(command, stdout = PIPE)
        p.wait()

        #Removing temporary file
        os.remove(tempFilename)
    
        gene = getNextGene(gtfIterator)
    chromosome = next(genomeIterator, None)