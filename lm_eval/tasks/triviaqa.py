"""
TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension
https://arxiv.org/pdf/1705.03551.pdf

TriviaQA is a reading comprehension dataset containing over 650K question-answer-evidence
triples. TriviaQA includes 95K question-answer pairs authored by trivia enthusiasts
and independently gathered evidence documents, six per question on average, that provide
high quality distant supervision for answering the questions.

Homepage: https://nlp.cs.washington.edu/triviaqa/
"""
import inspect
import string
from lm_eval.base import Task, rf
from lm_eval.metrics import mean

_CITATION = """
@InProceedings{JoshiTriviaQA2017,
    author = {Joshi, Mandar and Choi, Eunsol and Weld, Daniel S. and Zettlemoyer, Luke},
    title = {TriviaQA: A Large Scale Distantly Supervised Challenge Dataset for Reading Comprehension},
    booktitle = {Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics},
    month = {July},
    year = {2017},
    address = {Vancouver, Canada},
    publisher = {Association for Computational Linguistics},
}
"""


class TriviaQA(Task):
    VERSION = 3
    DATASET_PATH = "trivia_qa"
    DATASET_NAME = "rc.nocontext"

    def has_training_docs(self):
        return True

    def has_validation_docs(self):
        return True

    def has_test_docs(self):
        return False

    def training_docs(self):
        return self.dataset["train"]

    def validation_docs(self):
        return self.dataset["validation"]

    def test_docs(self):
        raise NotImplementedError()

    def doc_to_text(self, doc):
        return f"Question: {doc['question']}\nAnswer:"

    def should_decontaminate(self):
        return True

    def doc_to_decontamination_query(self, doc):
        return doc["question"]

    def doc_to_target(self, doc):
        return " " + doc["answer"]["value"]

    def construct_requests(self, doc, ctx):
        """Uses RequestFactory to construct Requests and returns an iterable of
        Requests which will be sent to the LM.
        :param doc:
                The document as returned from training_docs, validation_docs, or test_docs.
        :param ctx: str
                The context string, generated by fewshot_context. This includes the natural
                language description, as well as the few shot examples, and the question
                part of the document for `doc`.
        """
        continuation = rf.greedy_until(ctx, {"until": ["\n", ".", ","]})
        return continuation

    def process_results(self, doc, results):
        continuation = (
            results[0]
            .strip()
            .lower()
            .translate(str.maketrans("", "", string.punctuation))
        )
        list_of_candidates = [
            alias.lower().translate(str.maketrans("", "", string.punctuation))
            for alias in doc["answer"]["aliases"]
        ]
        return {"em": float(continuation in list_of_candidates)}

    def aggregation(self):
        return {
            "em": mean,
        }

    def higher_is_better(self):
        return {"em": True}
