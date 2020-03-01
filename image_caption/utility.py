from pickle import load
from numpy import argmax
from keras.preprocessing.sequence import pad_sequences


# load doc into memory
def load_doc(filename):
    with open(filename, 'r') as file:
        return file.read()


# load a pre-defined list of photo identifiers
def load_set(filename):
    doc = load_doc(filename)
    lines = [line for line in doc.split('\n') if len(line) > 0]
    dataset = [line.split('.')[0] for line in lines]
    return set(dataset)


# covert a dictionary of clean descriptions to a list of descriptions
def to_lines(descriptions):
    return [d for key in descriptions.keys()
            for d in descriptions[key]]


# load photo features
def load_photo_features(filename, dataset):
    all_features = load(open(filename, 'rb'))
    features = {k: all_features[k] for k in dataset}
    return features


# load clean descriptions into memory
def load_clean_descriptions(filename, dataset):
    doc = load_doc(filename)
    descriptions = {}
    tokens_list = [line.split() for line in doc.split('\n')]
    tokens_list = [tokens for tokens in tokens_list if tokens[0] in dataset]
    for tokens in tokens_list:
        image_id, image_desc = tokens[0], tokens[1:]
        image_descriptions = descriptions.setdefault(image_id, [])
        desc = 'startseq ' + ' '.join(image_desc) + ' endseq'
        image_descriptions.append(desc)
    return descriptions


# calculate the length of the description with the most words
def max_length(descriptions):
    lines = to_lines(descriptions)
    return max(d.count(' ') for d in lines)


# map an integer to a word
def word_for_id(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None


# fit a tokenizer given caption descriptions
def create_tokenizer(descriptions):
    lines = to_lines(descriptions)
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(lines)
    return tokenizer


# generate a description for an image
def generate_desc(model, tokenizer, photo, max_length):
    # seed the generation process
    in_text = 'startseq'
    # iterate over the whole length of the sequence
    for i in range(max_length):
        # integer encode input sequence
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        # pad input
        sequence = pad_sequences([sequence], maxlen=max_length)
        # predict next word
        yhat = model.predict([photo, sequence], verbose=0)
        # convert probability to integer
        yhat = argmax(yhat)
        # map integer to word
        word = word_for_id(yhat, tokenizer)
        # stop if we cannot map the word
        if word is None:
            break
        # append as input for generating the next word
        in_text += f" {word}"
        # stop if we predict the end of the sequence
        if word == 'endseq':
            break
    return in_text