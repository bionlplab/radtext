import bioc
import pytest

from radtext.models.sentence_split_nltk import split, BioCSSplitterNLTK


def test_split():
    text = 'No pneumothorax. No pneumothorax.'
    rst = [(line, offset) for line, offset in split(text)]
    assert len(rst) == 2
    assert rst[0][0] == 'No pneumothorax.'
    assert rst[0][1] == 0
    assert rst[1][0] == 'No pneumothorax.'
    assert rst[1][1] == 17

    rst = [(line, offset) for line, offset in split('')]
    assert len(rst) == 0

    with pytest.raises(TypeError):
        iter = split(None)
        next(iter)


def test_split_newline():
    text = 'hello world\nhello world!'
    rst = [(line, offset) for line, offset in split(text, newline=True)]
    assert len(rst) == 2
    assert rst[0][0] == 'hello world'
    assert rst[0][1] == 0
    assert rst[1][0] == 'hello world!'
    assert rst[1][1] == 12

    rst = [(line, offset) for line, offset in split(text, newline=False)]
    assert len(rst) == 1
    assert rst[0][0] == text
    assert rst[0][1] == 0


def test_BioCSSplitterNLTK():
    text = 'No pneumothorax.\nNo pneumothorax.'
    document = bioc.BioCDocument()
    p = bioc.BioCPassage.of_text(text)
    document.add_passage(p)
    assert p.text == text
    assert len(p.sentences) == 0

    splitter = BioCSSplitterNLTK()
    document = splitter.process_document(document)
    p = document.passages[0]
    assert len(p.sentences) == 2
    assert p.sentences[0].text == 'No pneumothorax.'
    assert p.sentences[0].offset == 0
    assert p.sentences[1].text == 'No pneumothorax.'
    assert p.sentences[1].offset == 17


#     def test_init(self):
#         ssplit = NegBioSSplitter(newline=True)
#         text = 'No pneumothorax \nNo pneumothorax.'
#         rst = [(line, offset) for line, offset in ssplit.split(text)]
#         assert len(rst) == 2
#
#         ssplit = NegBioSSplitter()
#         text = 'No pneumothorax \nNo pneumothorax.'
#         rst = [(line, offset) for line, offset in ssplit.split(text)]
#         assert len(rst) == 1
#
#     def test_split_line(self, splitter):
#         text = 'No pneumothorax.\nNo pneumothorax.'
#         rst = [(line, offset) for line, offset in splitter.split_line(text)]
#         assert len(rst) == 2
#         assert rst[0][0] == 'No pneumothorax.'
#         assert rst[0][1] == 0
#         assert rst[1][0] == 'No pneumothorax.'
#         assert rst[1][1] == 17
#
#         text = 'No pneumothorax. No pneumothorax.'
#         rst = [(line, offset) for line, offset in splitter.split_line(text)]
#         assert len(rst) == 1
#         assert rst[0][0] == text
#         assert rst[0][1] == 0
#

#
#     def test_split_doc(self, splitter):
#         text = 'No pneumothorax.\nNo pneumothorax.'
#         document = text_to_bioc([text], 'd/p')
#         p = document.passages[0]
#         assert p.text == text
#         assert len(p.sentences) == 0
#
#         document = splitter.__call__(document)
#         p = document.passages[0]
#         assert len(p.sentences) == 2
#         assert p.sentences[0].text == 'No pneumothorax.'
#         assert p.sentences[0].offset == 0
#         assert p.sentences[1].text == 'No pneumothorax.'
#         assert p.sentences[1].offset == 17
