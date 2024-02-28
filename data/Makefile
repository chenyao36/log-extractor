half := 28241
all: \
	Apache.part-1-of-2.log \
	Apache.part-2-of-2.log \
	Apache.shuf.part-1-of-2.log \
	Apache.shuf.part-2-of-2.log

%.part-1-of-2.log: %.log
	head -n $(half) $< > $@
%.part-2-of-2.log: %.log
	tail -n $(half) $< > $@

%.shuf.log: %.log
	shuf $< > $@

%.log: %.tar.gz
	tar xzf $<

Apache.tar.gz:
	curl 'https://zenodo.org/records/8196385/files/Apache.tar.gz?download=1' -o Apache.tar.gz

