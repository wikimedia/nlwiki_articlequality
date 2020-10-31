"""
Process a collection of XML dumps looking for the introduction and removal of {{Beginnetje}} templates
and assume the introduction represents a quality label ("E") and the removal represents the quality 
label "D". Note: This script does not yet handle reverts (e.g. vandalism).  To do that, look into 
the mwreverts libraray

USAGE:
    nlwiki_template_extractor (-h|--help)
    nlwiki_template_extractor <xml-dump>... 
        [--processes=<num>]
        [--output=<path>]

OPTIONS
    -h --help   Print this documentation
    <xml-dump>  Path to an XML dump to process (could be compressed gzip, bz2, etc.)
    --processes=<num>  Number of parallel processes to use for extraction [default: <cpu_count>]
    --output=<path>    Where to write the output file [default: <stdout>]

"""
import sys
import docopt
import mwxml
import json
import re
import multiprocessing

STUB_TEMPLATE_NAME = "beginnetje"
TEMPLATE_RE = re.compile(r'{{\s*{0}'.format(STUB_TEMPLATE_NAME))  #TODO: Make sure this actually works

def main():
    args = docopt.docopt(__doc__)
    
    paths = args['<xml-dump>']
    if args['--processes'] == "<cpu_count>":
        threads = multiprocessing.cpu_count()
    else:
        threads = int(args['--processes'])
    
    if args['--output'] == "<stdout>":
        output = sys.stdout
    else:
        output = open(args['--output'], "w")
    
    run(paths, threads, output)

def run(paths, threads, output):
    
    def process_template_changes(dump, path):
        for page in dump:
            template_appeared = False
            for revision in page:
                try:
                    if not template_appeared and TEMPLATE_RE.search(revision.text.lower()): #TODO: Make sure this evaluated to False when we don't find anything
                        template_appeared = True
                        yield revision.id, "E"
                    elif template_appeared and not TEMPLATE_RE.search(revision.text.lower()):
                        yield revision.id, "D"
                        break
                except TypeError:
                    print("Revision.text was not a string")
                except AttributeError:
                    print("Revision.text was not a string")
    
    for rev_id, label in mwxml.map(process_template_changes, paths, threads):
        # Write the label to the output
        json.dump({'rev_id': rev_id, 'label': label}, output)       
