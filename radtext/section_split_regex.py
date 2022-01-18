import logging

import bioc

from radtext.core import BioCProcessor


def is_empty(passage):
    return len(passage.text) == 0


def strip(passage):
    start = 0
    while start < len(passage.text) and passage.text[start].isspace():
        start += 1

    end = len(passage.text)
    while end > start and passage.text[end - 1].isspace():
        end -= 1

    passage.offset += start
    logging.debug('before: %r' % passage.text)
    passage.text = passage.text[start:end]
    logging.debug('after:  %r' % passage.text)
    return passage


class BioCSectionSplitterRegex(BioCProcessor):
    def __init__(self, regex_pattern):
        self.pattern = regex_pattern

    def process_document(self, doc: bioc.BioCDocument) -> bioc.BioCDocument:
        """
        Split one report into sections. Section splitting is a deterministic
        consequence of section titles.
        """

        # text = doc.passages[0].text
        # offset = doc.passages[0].offset

        def create_passage(text, offset, start, end, title=None):
            passage = bioc.BioCPassage()
            passage.offset = start + offset
            passage.text = text[start:end]
            if title is not None:
                passage.infons['section_concept'] = title[:-1].strip() if title[-1] == ':' else title.strip()
                passage.infons['type'] = 'title_1'
            strip(passage)
            return passage

        passages = list(doc.passages)
        del doc.passages[:]
        for passage in passages:
            text = passage.text
            offset = passage.offset
            local_start = 0
            for matcher in self.pattern.finditer(text):
                logging.debug('Match: %s', matcher.group())
                # add last
                local_end = matcher.start()
                if local_end != local_start:
                    passage = create_passage(text, offset, local_start, local_end)
                    if not is_empty(passage):
                        doc.add_passage(passage)

                local_start = local_end

                # add title
                local_end = matcher.end()
                passage = create_passage(text, offset, local_start, local_end, text[local_start:local_end])
                if not is_empty(passage):
                    doc.add_passage(passage)

                local_start = local_end

            # add last piece
            local_end = len(text)
            if local_start < local_end:
                passage = create_passage(text, offset, local_start, local_end)
                if not is_empty(passage):
                    doc.add_passage(passage)
        return doc
