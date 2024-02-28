import functools

from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation


class Segmenter:
    def __init__(self, max_characters=None):
        self._split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
        self._concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$", remove_former_matched=False)
        self._segmenter = make_pipeline(normalize, split_newline, self._concat_tail_no, self._split_punc2)
        self.max_characters = max_characters
    
    def segmentation(self, text):
        res = list(self._segmenter(text))
        res = self.merge(res)
        return res

    def merge(self, res):
        if self.max_characters is None:
            return res
        
        accum_len = 0
        concat_s = list()
        concat_list = list()
        print(res)
        for s in res:
            if accum_len + len(s) <= self.max_characters:
                concat_s.append(s)
                accum_len += len(s)
            else:
                concat_list.append("".join(concat_s))
                accum_len = 0
                concat_s = list()
                concat_s.append(s)
                accum_len = len(s)
        if len(concat_s) > 0:
            concat_list.append("".join(concat_s))
        return concat_list