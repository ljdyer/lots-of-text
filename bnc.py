from nltk.corpus.reader.bnc import BNCCorpusReader
from nltk.tokenize.treebank import TreebankWordDetokenizer

bnc_reader = BNCCorpusReader(root="E:\\bnc\\download\\Texts\\", fileids=r'[A-K]/\w*/\w*\.xml')

list_of_fileids = ['A/A0/A00.xml', 'A/A0/A01.xml', 'A/A0/A02.xml', 'A/A0/A03.xml']

twd = TreebankWordDetokenizer()

for file_id in list_of_fileids:
    sents = bnc_reader.sents(fileids=[file_id])
    print(' '.join([twd.detokenize(sent) for sent in sents[:100]]))