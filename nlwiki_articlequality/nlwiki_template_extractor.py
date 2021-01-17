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
        [--debug]

OPTIONS
    -h --help   Print this documentation
    <xml-dump>  Path to an XML dump to process (could be compressed gzip, bz2, etc.)
    --processes=<num>  Number of parallel processes to use for extraction [default: <cpu_count>]
    --output=<path>    Where to write the output file [default: <stdout>]
    --debug     Print debug logging
"""
import sys
import docopt
import mwxml
import json
import re
import multiprocessing
import logging

STUB_TEMPLATE_NAME = "beginnetje"
TEMPLATE_RE = re.compile(r'{{\s*{0}'.format(STUB_TEMPLATE_NAME))  #TODO: Make sure this actually works

def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    
    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    
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
                rev_doc = {'rev_id': revision.id, 
                           'page_namespace': page.namespace, 
                           'page_title': page.title, 
                           'timestamp': str(revision.timestamp),
                           'username': str(revision.user.text) if revision.user is not None else None}


                if revision.text is not None:
                    if not template_appeared and TEMPLATE_RE.search(revision.text.lower()): #TODO: Make sure this evaluated to False when we don't find anything
                        template_appeared = True
                        rev_doc['wp10'] = "E"
                        yield rev_doc
                    elif template_appeared and not TEMPLATE_RE.search(revision.text.lower()):
                        rev_doc['wp10'] = "D"
                        yield rev_doc
                        break
                else:
                    logging.debug("Revision.text for {0} is not a string".format(rev_doc))
    
    for label_doc in mwxml.map(process_template_changes, paths, threads):
        # Write the label to the output
        json.dump(label_doc, output)       
        output.write("\n")
