# NLP pipeline package for Krishi Saral
# Each stage of the pipeline lives in its own file so it can be
# explained independently during a presentation:
#
#   1. sentence_segmentation.py  -> split raw text into sentences
#   2. tokenizer.py               -> split sentences into words
#   3. text_cleaner.py            -> lowercase / remove noise
#   4. stopword_handler.py        -> remove common stop-words
#   5. lemmatizer.py              -> reduce words to their base form
#   6. keyword_extractor.py       -> find the most important words
