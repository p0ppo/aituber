import os
import re
import requests

from bs4 import BeautifulSoup


# To be merged into utils.py
def get_text_by_region(url, start_s, end_s):
    response = requests.get(url)
    html = response.content.decode("utf-8")
    st_split = html.split(start_s)
    if len(st_split) != 2:
        return None
    text = st_split[1].split(end_s)[0]
    text_re = re.sub(re.compile('<.*?>'), '', text)
    return text_re


class FF14Scraper():
    def __init__(self):
        self._url = "https://ffxiv.consolegameswiki.com"

        self._subpages = {
            # Main Quest
            "Main": {
                "url": "/wiki/Main_Scenario_Quests",
                "table_class": "pve table",
            },
        }

        self._regions = {
            # Journal
            "Journal": {
                "start_s": '<span class="mw-headline" id="Journal">Journal</span></h2>\n',
                "end_s": '<h2><span class="mw-headline" id="Dialogue">'
            },

            # Dialogue
            # FIXME: Currently do not support all patterns in HTML source.
            #"Dialogue": {
            #    "start_s": '<h2><span class="mw-headline" id="Dialogue">Dialogue</span></h2>\n',
            #    "end_s": '</pre>\n<h3><span class="mw-headline" id="Conjurer">Conjurer</span></h3>'
            #},
        }

    def scrape(self):
        res = list()
        for idx_s, subpage in self._subpages.items():
            print(f"Parsing {idx_s}.")
            response = requests.get(self._url + subpage["url"])
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all("table", class_=subpage["table_class"]):
                thead = item.find('tbody')
                for tr in thead.find_all("tr"):
                    if tr.find("a") is not None:
                        sub_url = tr.find("a").get("href")
                        for _, region in self._regions.items():
                            text = get_text_by_region(
                                self._url + sub_url,
                                region["start_s"],
                                region["end_s"]
                                )
                            if text is None:
                                continue
                            #res.append([os.path.basename(sub_url), text])
                            res.append([text])
        return res


if __name__ == "__main__":
    scraper = FF14Scraper()
    docs = scraper.scrape()

    #from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import TensorflowHubEmbeddings, HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    #from langchain.embeddings import HuggingFaceEmbeddings
    #from llama_index.embeddings.langchain import LangchainEmbedding

    #embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

    #db = Chroma.from_texts(sum(docs, []), embeddings, persist_directory="D:/Streaming/dev/aituber/aituber/src/rag/vec/test3")
    db = Chroma(embedding_function=embeddings, persist_directory="D:/Streaming/dev/aituber/aituber/src/rag/vec/test3")
    #db.persist()
    print(db)

    texts = db.similarity_search_with_relevance_scores("グリダニアについて教えて", k=5)
    print(texts)