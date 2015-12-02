import os

import pytest
import lxml.etree

from aristo.core.knowledge_creator import KnowledgeCreator

test_data = [
    (["sinkhole"], 1, 1),
    (["56fsvhvnbv"], 2, 0),
    (["sinkhole", "cell"], 1, 2),
    (["sinkhole", "cell"], 5, 2)

]


@pytest.mark.parametrize("articles, batch_size, expected_answer", test_data)
def test_should_download_articles(tmpdir, articles, batch_size, expected_answer):
    output_file = str(tmpdir.mkdir("test_should_predict_the_correct_answer").join("wiki.xml"))
    sut = KnowledgeCreator()
    actual = 0;
    for file in sut.download_corpus(articles, output_file, batch_size):
        doc = lxml.etree.parse(file)
        actual = actual + doc.xpath('count(/*[local-name() = "mediawiki"]/*[local-name() = "page"])')
    assert actual == expected_answer

def test_dummy():
    file ="/Users/aparnaelangovan/Documents/Programming/python/aristo/repo/aristo/core/../../../corpus/mediafile_20151202_220624_1.xml"
    doc = lxml.etree.parse(file)
    actual = doc.xpath('count(/*[local-name() = "mediawiki"]/*[local-name() = "page"])')
    assert actual == 10