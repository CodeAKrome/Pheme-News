import spacy
import nltk
from spacytextblob.spacytextblob import SpacyTextBlob
from toolbox import pretty

# nltk.download('stopwords')
from nltk.corpus import stopwords
from collections import defaultdict
from collections import Counter


nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("spacytextblob")


def transform_dict(a):
    b = {}
    for c in a:
        b[c] = {}
        for key, value in a[c].items():
            b[c][key] = dict(Counter(value))
    return b


def assess(doc):
    assessments = []
    for token in doc:
        for assessment in token._.assessments:
            assessments.append((assessment[0][0], assessment[1]))
    return assessments


def nlpize(sentences):
    nlp_data = {
        "lemma": [],
        "ner": [],
        "sent": [],
        "subj": [],
        "assess": [],
        "ner_sent": {},
    }
    for sentence in sentences:
        doc = nlp(sentence)
        lemmas = [token.lemma_ for token in doc if not token.is_stop]
        lemmas = [lemma for lemma in lemmas if lemma[0].isalpha()]
        nlp_data["lemma"].append(lemmas)
        nlp_data["ner"].append([(ent.text, ent.label_) for ent in doc.ents])
        nlp_data["sent"].append(doc._.polarity)
        nlp_data["subj"].append(doc._.subjectivity)
        nlp_data["assess"].append(assess(doc))
        for ent in doc.ents:
            if ent.label_ not in nlp_data["ner_sent"]:
                nlp_data["ner_sent"][ent.label_] = {"good": [], "bad": []}
            if doc._.polarity > 0:
                nlp_data["ner_sent"][ent.label_]["good"].append(ent.text)
            elif doc._.polarity < 0:
                nlp_data["ner_sent"][ent.label_]["bad"].append(ent.text)

    nlp_data["ner_sent"] = transform_dict(nlp_data["ner_sent"])
    return nlp_data


def selftest():
    text = [
        "Washington and Riyadh confirm talks in Jeddah amid reports of more airstrikes and explosions in Khartoum despite US threat of sanctions",
        "Direct talks between the warring Sudanese army and the paramilitary Rapid Support Forces will start in Jeddah on Saturday, the US and Saudi governments have confirmed, even as fighting showed little signs of abating in the Sudanese capital.",
        "A joint US-Saudi statement welcomed the “start of pre-negotiation talks” and urged sustained global support to quell the fighting.",
        "“The Kingdom of Saudi Arabia and the United States urge both parties to take in consideration the interests of the Sudanese nation and its people and actively engage in the talks toward a ceasefire and end to the conflict,” the statement said.",
        "Hundreds of people have died in nearly three weeks of fighting between forces aligned with Sudan’s de facto leader, Abdel Fattah al-Burhan, who leads the regular army, and his deputy turned rival Mohamed Hamdan Daglo, who commands the Rapid Support Forces (RSF).",
        "Multiple truces have been reached since the fighting erupted on 15 April, but none has been respected.",
        "The army confirmed late on Friday that it had sent envoys to Saudi Arabia to discuss “details of the truce in the process of being extended” with its paramilitary foes.",
        "Burhan had given his backing to a seven-day ceasefire announced on Wednesday, but early on Friday, the RSF said it was extending by three days a previous truce brokered under US-Saudi mediation.",
        "The US-Saudi statement noted the efforts of other countries and organisations behind this weekend’s talks, including Britain, the United Arab Emirates, the League of Arab States, the African Union and other groups.",
        "In Khartoum, witnesses reported continued airstrikes and explosions on Friday, including near the airport.",
        "The fighting raged despite a threat of sanctions from US president, Joe Biden, against those responsible for “threatening the peace, security and stability of Sudan” and “undermining Sudan’s democratic transition”.",
        "The north African country suffered decades of sanctions during the rule of autocrat Omar al-Bashir, who was ousted in a palace coup in 2019 after mass street protests.",
        "Biden said: “The violence taking place in Sudan is a tragedy – and it is a betrayal of the Sudanese people’s clear demand for civilian government and a transition to democracy. It must end.”",
        "The conflict has killed about 700 people, mostly in Khartoum and the western Darfur region, according to the Armed Conflict Location and Event Data Project.",
        "The UN children’s agency, Unicef, warned on Friday that “the situation in Sudan has become fatal for a frighteningly large number of children”.",
        "Spokesperson James Elder said Unicef had received reports from a trusted partner – not yet independently verified by the UN – that 190 children were killed and 1,700 wounded during the conflict’s first 11 days.",
        "He said the figures had been gathered from health facilities in Khartoum and Darfur since 15 April, meaning that they only cover children who actually made it to facilities in those areas.",
        "“The reality is likely to be much worse,” Elder said.",
        "Aid workers have struggled to get much-needed supplies to areas hit by violence. According to the International Medical Corps, at least 18 aid workers have been killed amid the fierce urban fighting.",
        "Nearly 450,000 civilians had already fled their homes since the fighting began, the International Organisation for Migration said, including more than 115,000 who had sought refuge in neighbouring countries.",
        "The UN refugee agency, UNHCR, said it was preparing for an outflow of 860,000 people, adding that $445m would be needed to support them just until October.",
        "The UN warned that if the fighting continued, it could raise the already large number of Sudanese threatened by hunger and malnutrition by as many as 2.5 million.",
        "“That raises the number to a total of 19 million people in the next three to six months,” said Farhan Haq, a spokesperson for the UN chief, António Guterres.",
    ]
    data = nlpize(text)
    pretty(data)


if __name__ == "__main__":
    selftest()
