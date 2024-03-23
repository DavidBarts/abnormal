# Define the following if Pandoc is not on the standard path. If you
# do, it must end with a trailing slash.

PANDOC_DIR =

.PHONY: init test readme

init:
	echo Nothing to do.

test:
	./run-tests

readme: README.md

# Because I dislike Markdown (syntactically significant end-of-line
# whitespace, really?), I maintain the README for this project in
# reStructuredText.

%.md: %.rst
	$(PANDOC_DIR)pandoc -f rst -t markdown_strict -o $@ $<
