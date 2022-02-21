import tqdm
from bioc import BioCPassage
from radtext.models.constants import POSITIVE
from radtext.core import BioCProcessor
from radtext.models.neg.match_ngrex import NegGrexPatterns
from radtext.models.neg.match_regex import NegRegexPatterns


class BioCNeg(BioCProcessor):
    def __init__(self, regex_actor: NegRegexPatterns, ngrex_actor: NegGrexPatterns, verbose=False):
        super(BioCNeg, self).__init__('neg:negbio')
        self.regex_actor = regex_actor
        self.ngrex_actor = ngrex_actor
        self.verbose = verbose

    def process_passage(self, passage: BioCPassage, docid: str = None) -> BioCPassage:
        for ann in tqdm.tqdm(passage.annotations, disable=not self.verbose):
            ann.infons[POSITIVE] = True
            if 'nlp_system' in ann.infons:
                ann.infons['nlp_system'] += ';' + self.nlp_system
            else:
                ann.infons['nlp_system'] = self.nlp_system
            if 'nlp_date_time' in ann.infons:
                ann.infons['nlp_date_time'] += ';' + self.nlp_date_time
            else:
                ann.infons['nlp_date_time'] = self.nlp_date_time

            regex_assertion = self.regex_actor.assert_(passage, ann)
            if regex_assertion.match_uncertainty_pre_neg():
                continue
            if regex_assertion.match_double_neg():
                continue
            if regex_assertion.assert_neg():
                continue
            if regex_assertion.assert_uncertainty_post_neg():
                continue

            # graph
            ngrex_assertion = self.ngrex_actor.assert_(passage, ann, docid)
            if ngrex_assertion.assert_uncertainty_pre_neg():
                continue
            if ngrex_assertion.assert_double_neg():
                continue
            if ngrex_assertion.assert_neg():
                continue
            if ngrex_assertion.assert_uncertainty_post_neg():
                continue

        return passage
