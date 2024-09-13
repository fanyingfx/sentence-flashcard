import spacy
english_nlp = spacy.load("en_core_web_sm")
__all__ = ["english_nlp"]
# EXAMPLE_TEXT = "The dog was called Wellington. It belonged to Mrs. Shears who was our friend. She lived on the opposite side of the road, two houses to the left."
# doc=nlp(EXAMPLE_TEXT)
# print(doc.text)

# for token in doc:
#     print(token.text,token.lemma_)


