# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ElkarHizketak: Conversational Question Answering dataset in Basque"""

import json

import datasets


_CITATION = """\
@inproceedings{otegi-etal-2020-conversational,
    title = "{Conversational Question Answering in Low Resource Scenarios: A Dataset and Case Study for {B}asque}",
    author = "Otegi, Arantxa  and
      Agirre, Aitor  and
      Campos, Jon Ander  and
      Soroa, Aitor  and
      Agirre, Eneko",
    booktitle = "Proceedings of the 12th Language Resources and Evaluation Conference",
    year = "2020",
    publisher = "European Language Resources Association",
    url = "https://aclanthology.org/2020.lrec-1.55",
    pages = "436--442",
    ISBN = "979-10-95546-34-4",
}
"""

_DESCRIPTION = """
ElkarHizketak is a low resource conversational Question Answering
(QA) dataset in Basque created by Basque speaker volunteers. The
dataset contains close to 400 dialogues and more than 1600 question
and answers, and its small size presents a realistic low-resource
scenario for conversational QA systems. The dataset is built on top of
Wikipedia sections about popular people and organizations. The
dialogues involve two crowd workers: (1) a student ask questions after
reading a small introduction about the person, but without seeing the
section text; and (2) a teacher answers the questions selecting a span
of text of the section.  """

_HOMEPAGE = "http://ixa.si.ehu.es/node/12934"

_LICENSE = "Creative Commons Attribution-ShareAlike 4.0 International Public License (CC BY-SA 4.0)"

_URLs = {
    "train": "http://ixa2.si.ehu.es/convai/elkarhizketak-v1.0/elkarhizketak-train-v1.0.json",
    "validation": "http://ixa2.si.ehu.es/convai/elkarhizketak-v1.0/elkarhizketak-dev-v1.0.json",
    "test": "http://ixa2.si.ehu.es/convai/elkarhizketak-v1.0/elkarhizketak-test-v1.0.json",
}


class Elkarhizketak(datasets.GeneratorBasedBuilder):
    """ElkarHizketak: Conversational Question Answering dataset in Basque. Version 1.0."""

    VERSION = datasets.Version("1.0.0")

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="plain_text",
            description="Plain text",
            version=VERSION,
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "dialogue_id": datasets.Value("string"),
                    "wikipedia_page_title": datasets.Value("string"),
                    "background": datasets.Value("string"),
                    "section_title": datasets.Value("string"),
                    "context": datasets.Value("string"),
                    "turn_ids": datasets.Sequence(datasets.Value("string")),
                    "questions": datasets.Sequence(datasets.Value("string")),
                    "yesnos": datasets.Sequence(datasets.ClassLabel(names=["y", "n", "x"])),
                    "answers": datasets.Sequence(
                        {
                            "texts": datasets.Sequence(datasets.Value("string")),
                            "answer_starts": datasets.Sequence(datasets.Value("int32")),
                            "input_texts": datasets.Sequence(datasets.Value("string")),
                        }
                    ),
                    "orig_answers": {
                        "texts": datasets.Sequence(datasets.Value("string")),
                        "answer_starts": datasets.Sequence(datasets.Value("int32")),
                    },
                }
            ),
            supervised_keys=None,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        data_dir = dl_manager.download_and_extract(_URLs)
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "filepath": data_dir["train"],
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "filepath": data_dir["validation"],
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "filepath": data_dir["test"],
                },
            ),
        ]

    def _generate_examples(self, filepath):
        """Yields examples."""
        with open(filepath, encoding="utf-8") as f:
            elkarhizketak = json.load(f)
            for section in elkarhizketak["data"]:
                wiki_page_title = section.get("title", "").strip()
                background = section.get("background", "").strip()
                section_title = section.get("section_title", "").strip()

                for dialogue in section["paragraphs"]:
                    context = dialogue["context"].strip()
                    dialogue_id = dialogue["id"]

                    yesnos = []
                    questions = []
                    turn_ids = []
                    answers = []
                    orig_answers = {"texts": [], "answer_starts": []}

                    for turn in dialogue["qas"]:
                        yesnos.append(turn["yesno"])
                        questions.append(turn["question"])
                        turn_ids.append(turn["id"])

                        ans_ = {
                            "texts": [t["text"].strip() for t in turn["answers"]],
                            "answer_starts": [t["answer_start"] for t in turn["answers"]],
                            "input_texts": [t["input_text"] for t in turn["answers"]],
                        }
                        answers.append(ans_)

                        orig_answers["texts"].append(turn["orig_answer"]["text"])
                        orig_answers["answer_starts"].append(turn["orig_answer"]["answer_start"])

                    yield dialogue_id, {
                        "dialogue_id": dialogue_id,
                        "wikipedia_page_title": wiki_page_title,
                        "background": background,
                        "section_title": section_title,
                        "context": context,
                        "turn_ids": turn_ids,
                        "questions": questions,
                        "yesnos": yesnos,
                        "answers": answers,
                        "orig_answers": orig_answers,
                    }
