import functools

from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation


class Segmenter:
    def __init__(self):
        self._split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
        self._concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$", remove_former_matched=False)
        self._segmenter = make_pipeline(normalize, split_newline, self._concat_tail_no, self._split_punc2)
    
    def segmentation(self, text):
        return list(self._segmenter(text))