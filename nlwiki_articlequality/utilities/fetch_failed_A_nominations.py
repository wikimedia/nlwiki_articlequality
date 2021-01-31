"""
Process a collection of XML dumps looking for the introduction and removal of {{Beginnetje}} templates
and assume the introduction represents a quality label ("E") and the removal represents the quality 
label "D". Note: This script does not yet handle reverts (e.g. vandalism).  To do that, look into 
the mwreverts libraray

USAGE:
    fetch_failed_A_nominations (-h|--help)
    fetch_failed_A_nominations
        [--output=<path>]
        [--debug]

OPTIONS
    -h --help   Print this documentation
    --output=<path>    Where to write the output file [default: <stdout>]
    --debug     Print debug logging
"""
import json
import sys

import docopt
import mwapi
import mwparserfromhell

A_CLASS_CATEGORY = "Categorie:Wikipedia:Etalage-artikelen"
NOMINATIONS_PAGE_TITLE = "Wikipedia:Etalage/Aanmelding kandidaten/Aanmeldingen"
NLWIKI_HOST = "https://nl.wikipedia.org"

def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )

    if args['--output'] == "<stdout>":
        output = sys.stdout
    else:
        output = open(args['--output'], "w")

    session = mwapi.Session(NLWIKI_HOST, user_agent="paritoshsingh1612@gmail.com")
    for title in get_nominated_titles(session):
        page_doc = get_title_details(session, title)
        if 'missing' in page_doc:
            continue
        categories = set(c['title'] for c in page_doc.get('categories', []))

        if A_CLASS_CATEGORY not in categories:
            # We found a potential B class article
            output.write(json.dumps({
                'rev_id': page_doc['revisions'][0]['revid'],
                'timestamp': page_doc['revisions'][0]['timestamp'],
                'title': title,
                'wp10': "B"}) + "\n")

def get_nominated_titles_from_text(text):
    wikicode = mwparserfromhell.parse(text)
    for heading in wikicode.filter_headings():
        if heading.level == 3:
            heading_links = list(heading.title.filter_wikilinks())
            if len(heading_links) == 1:
                yield str(heading_links[0].title)

def get_nominated_titles(session):
    results = session.get(action='query', prop='revisions', rvdir='newer',
                          titles=NOMINATIONS_PAGE_TITLE,
                          rvprop=['content', 'timestamp'], rvslots='main', rvlimit=50,
                          formatversion=2, continuation=True)

    titles_we_have_seen = set()
    for doc in results:
       for rev_doc in doc['query']['pages'][0]['revisions']:
           text = rev_doc['slots']['main']['content']

           for title in get_nominated_titles_from_text(text):
               if title.lower() not in titles_we_have_seen:
                   yield title
                   titles_we_have_seen.add(title.lower())

def get_title_details(session, title):
    doc = session.get(action='query', prop=['categories', 'revisions'], titles=title, redirects=True, rvlimit=1, formatversion=2)
    return doc['query']['pages'][0]



if __name__ == "__main__":
    main()
