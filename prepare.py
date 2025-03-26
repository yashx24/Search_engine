import requests
import json

documents = []
vocab = {}
inverted_index = {}
codeforces_urls = []


with open("Leetcode/index.txt", "r", encoding="utf8") as f:
    lines = f.readlines()


def preprocess_index(document_text):
    terms = [term.lower() for term in document_text.strip().split()[1:]]
    return terms


def preprocess_text(document_text):
    text = ""
    for LINE in document_text:
        text += " " + LINE.strip()
    text = text.split("Example 1:")[0]
    terms = [term.lower() for term in text.strip().split()]
    return terms


def fetch_codeforces_problems():
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    data = response.json()
    with open("codeforces_problems.json", "w", encoding="utf-8") as f:
        json.dump(data['result'], f, indent=4)
    problems = data['result']['problems']
    return problems

def preprocess_codeforces_problem(problem):
    name = problem['name'].lower().split()
    tags = problem['tags']
    return name + tags

for index, line in enumerate(lines):
    tokens_index = preprocess_index(line)
    line_index_filepath = f"Leetcode/Qdata/{index + 1}/{index + 1}.txt"
    try:
        with open(line_index_filepath, "r", encoding="utf8") as f:
            doc_text = f.readlines()
            tokens_doc_text = preprocess_text(doc_text)
        tokens = tokens_index + tokens_doc_text
        documents.append(tokens)
        tokens = set(tokens)
        for token in tokens:
            if token not in vocab:
                vocab[token] = 1
            else:
                vocab[token] += 1
    except FileNotFoundError:
        print(f"File {line_index_filepath} not found.")


codeforces_problems = fetch_codeforces_problems()
for problem in codeforces_problems:
    tokens = preprocess_codeforces_problem(problem)
    documents.append(tokens)
    tokens = set(tokens)
    for token in tokens:
        if token not in vocab:
            vocab[token] = 1
        else:
            vocab[token] += 1
    url = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
    codeforces_urls.append(url)


vocab = dict(sorted(vocab.items(), key=lambda item: item[1], reverse=True))


with open("tf-idf/vocab.txt", "w", encoding="utf-8") as file:
    for key in vocab.keys():
        file.write(key + "\n")


with open("tf-idf/idf-values.txt", "w", encoding="utf-8") as file:
    for key in vocab.keys():
        file.write(str(vocab[key]) + "\n")


with open("tf-idf/documents.txt", "w", encoding="utf-8") as file:
    for document in documents:
        file.write(" ".join(document) + "\n")


for index, document in enumerate(documents):
    for token in document:
        if token not in inverted_index:
            inverted_index[token] = [index]
        else:
            inverted_index[token].append(index)


with open("tf-idf/inverted-index.txt", "w", encoding="utf-8") as file:
    for key in inverted_index.keys():
        file.write(key + "\n")
        file.write(" ".join([str(doc_id) for doc_id in inverted_index[key]]) + "\n")


with open("codeforces_urls.txt", "w", encoding="utf-8") as file:
    for url in codeforces_urls:
        file.write(url + "\n")

print("Number of documents: ", len(documents))
print("Size of vocab: ", len(vocab))
print("Sample document: ", documents[1])
