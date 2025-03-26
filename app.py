import math
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def fetch_codeforces_problems():
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    return response.json()['result']['problems']

def load_links():
    question_links = []
    with open("Leetcode/Qindex.txt", "r", encoding='utf-8') as f:
        question_links.extend({"url": link.strip(), "source": "leetcode"} for link in f.readlines())
    for problem in fetch_codeforces_problems():
        url = f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
        question_links.append({"url": url, "source": "codeforces"})
    return question_links

def load_documents():
    with open("tf-idf/documents.txt", "r", encoding='utf-8') as f:
        return [document.strip().split() for document in f.readlines()]

def load_vocab():
    vocab = {}
    with open("tf-idf/vocab.txt", "r", encoding='utf-8') as vocab_terms, open("tf-idf/idf-values.txt", "r") as vocab_idf_values:
        for term, idf_value in zip(vocab_terms, vocab_idf_values):
            vocab[term.strip()] = int(idf_value.strip())
    return vocab

def load_inverted_index():
    inverted_index = {}
    with open("tf-idf/inverted-index.txt", "r", encoding='utf-8') as f:
        inverted_index_terms = f.readlines()
    for row_num in range(0, len(inverted_index_terms), 2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num + 1].strip().split()
        inverted_index[term] = documents
    return inverted_index

def load_docs_heading():
    docs_heading = []
    with open("Leetcode/index.txt", "r", encoding='utf-8') as f:
        docs_heading.extend(f"Leetcode: {line.strip().split('.')[1].strip()}" for line in f.readlines())    
    docs_heading.extend(f"Codeforces: {problem['name']}" for problem in fetch_codeforces_problems())
    return docs_heading

documents = load_documents()
vocab_idf_values = load_vocab()
inverted_index = load_inverted_index()
question_links = load_links()
docs_heading = load_docs_heading()


def get_tf_dictionary(term):
    tf_values = {}
    if term in inverted_index:
        for doc_id in inverted_index[term]:
            tf_values[doc_id] = tf_values.get(doc_id, 0) + 1
    for doc_id in tf_values:
        tf_values[doc_id] /= len(documents[int(doc_id)])
    return tf_values

def get_idf_values(term):
    return math.log(len(documents) / vocab_idf_values.get(term, 1))

def calculate_sorted_order_of_documents(query_terms):
    potential_documents = {}
    for term in query_terms:
        if term not in vocab_idf_values:
            continue
        tf_value_by_document = get_tf_dictionary(term)
        idf_value = get_idf_values(term)
        for doc_id in tf_value_by_document:
            potential_documents[doc_id] = potential_documents.get(doc_id, 0) + tf_value_by_document[doc_id] * idf_value
    for doc_id in potential_documents:
        potential_documents[doc_id] /= len(query_terms)
    return dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))

def top_results(potential_documents, selected_sources):
    return [link["url"] for doc_id in potential_documents for link in question_links if link["source"] in selected_sources and question_links[int(doc_id)] == link]

@app.route("/", methods=["GET", "POST"])
def start_page():
    if request.method == "POST":
        query_terms = request.form.get("Query").strip().lower().split()
        selected_sources = request.form.get("sources", "").split(",")
        potential_documents = calculate_sorted_order_of_documents(query_terms)
        top_links = top_results(potential_documents, selected_sources)
        top_docs = [docs_heading[question_links.index({"url": link, "source": src})] for link in top_links for src in selected_sources if {"url": link, "source": src} in question_links]
        return render_template("output.html", links=top_links, docs_name=top_docs)
    return render_template("index.html")

@app.route("/<query>", methods=["GET"])
def search(query):
    query_terms = query.strip().lower().split()
    selected_sources = request.args.getlist("sources")
    potential_documents = calculate_sorted_order_of_documents(query_terms)
    top_links = top_results(potential_documents, selected_sources)
    top_docs = [docs_heading[question_links.index({"url": link, "source": src})] for link in top_links for src in selected_sources if {"url": link, "source": src} in question_links]
    return render_template("output.html", links=top_links, docs_name=top_docs)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
