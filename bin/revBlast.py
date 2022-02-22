from subprocess import Popen, PIPE
import os
import sys
import logging
import Bio.Blast.NCBIXML as BlastReader

#Fasta File
IN_FILE = sys.argv[1]

#Out fasta file
OUT_FILE = sys.argv[2]
TEMP_DIR = os.getcwd()
TEMP_PREFIX = "blast_temp_"

name = TEMP_PREFIX + sys.argv[1].split("/")[-1].split(".")[0]
if not os.path.exists(IN_FILE):
    sys.exit(0)

#CREATING BLAST DATABASE
print(IN_FILE)
command = ["makeblastdb", "-in" , IN_FILE, "-out", name, "-dbtype", "nucl"]
p = Popen(command, stdout = PIPE)
p.wait()

#RUNING BLAST ALIGNER ON REVERSE COMPLEMENT

runBlast = ["blastn", "-query", IN_FILE, "-strand", "minus", "-db", name,
                "-out", name + ".xml", "-outfmt", "5"]

b = Popen(runBlast, stdout = PIPE)
b.wait()

#WRITING OUTPUT


fastaHandler = open(IN_FILE)
fastaHeader = fastaHandler.readline()
fastaHandler.close()
summary = "geneId,geneStart,geneEnd,geneStrand,queryStart,queryEnd,subjectStart,subjectEnd,matchlength,matchPct\n"
blast_records = list(BlastReader.parse(open(name + ".xml")))[0].alignments[0].hsps
for a in blast_records:
    summary += "{},{},{},{},{},{},{}\n".format(fastaHeader.rstrip('\n').lstrip('>'),
                                           a.query_start,
                                           a.query_end,
                                           a.sbjct_start,
                                           a.sbjct_end,
                                           len(a.match),
                                           a.match.count("|")/len(a.match))

summaryOut = open(OUT_FILE, 'a')
summaryOut.write(summary)
summaryOut.close()

for f in os.listdir(os.getcwd()):
    if f.startswith(TEMP_PREFIX):
        os.remove(f)
