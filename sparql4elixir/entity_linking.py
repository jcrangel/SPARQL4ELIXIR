from nltk.tokenize import sent_tokenize, word_tokenize 
from configs import MAX_SCORE_PARSER_TRIPLES
from functools import reduce

def tokenize_sentence(sentence):
    tokens = word_tokenize(sentence)
    return tokens

def parser_sentence(sentence, index, endpoint):
    sentence_splitted = tokenize_sentence(sentence)
    window_size = len(sentence_splitted)
    matchs = []
    while window_size > 0 and window_size <= len(sentence_splitted):
        window_start = 0
        window_end = window_start + window_size
        while window_end <= len(sentence_splitted):
            term_search = reduce(lambda x, y: "{} {}".format(x, y), sentence_splitted[window_start:window_end])
            resultSearch = index.search(term_search)
            if resultSearch is not None and len(resultSearch) > 0:
                selected_hit = resultSearch[0]
                if selected_hit['score'] > MAX_SCORE_PARSER_TRIPLES:
                    selected_hit = None
                if selected_hit is not None and selected_hit not in matchs:
                    matchs.append(selected_hit)
            window_start += 1
            window_end = window_start + window_size
        window_size -= 1
    return matchs
