from flair.nn import Classifier
from flair.splitter import SegtokSentenceSplitter
from NewsSentiment import TargetSentimentClassifier
import sys
from json import dumps


class FlairSentiment:
    # NER_TAGGER = "flair/ner-english-large"
    NER_TAGGER = "ner-ontonotes-large"

    def __init__(self):
        self.sentiment_tagger = Classifier.load("sentiment")
        self.ner_tagger = Classifier.load(self.NER_TAGGER)
        self.splitter = SegtokSentenceSplitter()
        self.tsc = TargetSentimentClassifier()

    #        self.linker = Classifier.load("linker")

    def process_text(self, text: str) -> list:
        sentences = self.splitter.split(text)
        self.sentiment_tagger.predict(sentences)
        self.ner_tagger.predict(sentences)
        #        self.linker.predict(sentences)

        output = []
        for sentence in sentences:
            if sentence:
                try:
                    spans = []
                    sent = sentence.to_plain_string()
                    for span in sentence.get_spans("ner"):
                        l = sent[: span.start_position]
                        m = sent[span.start_position : span.end_position]
                        r = sent[span.end_position :]
                        sentiment = self.tsc.infer_from_text(l, m, r)
                        # Skip unkown labels, only consider known labels as they cause blank nodes
                        for label in span.labels:
                            if label.value == "<unk>": continue
                            val = label.value
                            spans.append(
                                {
                                    "text": span.text,
                                    "start": span.start_position,
                                    "end": span.end_position,
                                    "value": val,
                                    "score": f"{label.score:.2f}",
                                    "sentiment": sentiment[0]["class_label"],
                                    "probability": f"{sentiment[0]['class_prob']:.2f}",
                                }
                            )
                    output.append(
                        {
                            "sentence": sent,
                            "tag": sentence.tag.lower(),
                            "score": f"{sentence.score:.2f}",
                            "spans": spans,
                        }
                    )
                except Exception as e:
                    sys.stderr.write(f"{e}\nSentiment targetting failure:\n{sentence}")
                    # raise ValueError(f"{e}\nsent:\n{sentence}")
        return output


if __name__ == "__main__":
    classifier = FlairSentiment()
    output = classifier.process_text(sys.stdin.read())
    for rec in output:
        print(dumps(rec, indent=True))
