datasets/nlwiki-20201101-E_and_D.json:
	./utility /mnt/data/xmldatadumps/public/nlwiki/20201101/nlwiki-20201101-pages-meta-history?.xml-p*.bz2 > $@


datasets/nlwiki-20210116-A_B_and_C.json:
	wget https://quarry.wmflabs.org/run/522840/output/0/json-lines -qO- > $@

datasets/nlwiki-20201101-E_and_D.no_bots.json: datasets/nlwiki-20201101-E_and_D.json
	cat $< | grep -P '"username": ".*[bB]ot.*' > $@

datasets/nlwiki-20201101.balanced_sample.json: \
		datasets/nlwiki-20201101-E_and_D.no_bots.json \
		datasets/nlwiki-20210116-A_B_and_C.json
	(cat datasets/nlwiki-20201101-E_and_D.json | grep '"wp10": "E"' | shuf -n 100; \
	 cat datasets/nlwiki-20201101-E_and_D.json | grep '"wp10": "D"' | shuf -n 100; \
	 cat datasets/nlwiki-20210116-A_B_and_C.json | grep '"wp10": "C"' | shuf -n 100; \
	 cat datasets/nlwiki-20210116-A_B_and_C.json | grep '"wp10": "B"' | shuf -n 100; \
	 cat datasets/nlwiki-20210116-A_B_and_C.json | grep '"wp10": "A"' | shuf -n 100) | shuf > $@

