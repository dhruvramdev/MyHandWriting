# Coded By BugBoy : Github(https://github.com/bannyvishwas2020)
import re
import random
from yattag import Doc

doc, tag, text, line = Doc().ttl()
config = {
    'word_break': True
}


class Character:
    def __init__(self, char, letter_type, letter_set='set0'):
        self.char = char
        self.letter_type = letter_type
        self.letter_set = letter_set
        self.classes = ['blue']
        self.style = {
            'width': Character.get_width_char(char),
            'height': 25,
            'margin-top': 5,
            'margin-bottom': 10,
            'margin-right': 0
        }

    def randomize(self):
        # Randomize 33% of times
        limit = random.randint(2, 3)
        if random.random() < 0.33:
            keys = list(self.style.keys())
            random_keys = random.choices(keys, k=random.randint(1, limit))
            for key in random_keys:
                self.style[key] = self.style[key] + random.randint(-2, 2)

    def get_source(self):
        return "images/letters/{}/{}/{}.png".format(self.letter_set, self.letter_type, self.char)

    def get_classes(self):
        return " ".join(self.classes)

    def get_styles(self):
        output = []
        for key in self.style.keys():
            output.append("{}: {}px".format(key, self.style[key]))
        return ";".join(output)

    @staticmethod
    def get_width_char(ch):
        width_mapper = {
            'w': 16,
            'i': 8
        }
        return width_mapper.get(ch.lower(), 10)

    @staticmethod
    def from_char(ch):
        char_code = ord(ch)
        letter_set = "set0"

        # max 10 sets of letters
        # random_letter = round(random.random() * 10)
        # enable the below statement if 10 sets of letters available
        # letter_set="set{}".format(random_letter)

        if 65 <= char_code <= 90:
            letter_type = "caps"
            ch = ch.lower()
            return Character(ch, letter_type, letter_set)
        elif 97 <= char_code <= 177:
            letter_type = "small"
            return Character(ch, letter_type, letter_set)
        elif 48 <= char_code <= 57:
            letter_type = "others"
            ch = "{}".format(char_code)
            return Character(ch, letter_type, letter_set)
        else:
            letter_type = "others"
            ch = "{}".format(char_code)
            return Character(ch, letter_type, letter_set)


class Word:
    def __init__(self, word, options=None, ending=False):
        self.content = [word]
        self.ending = ending
        self.options = ['word']
        if options:
            self.options.extend(options)

    def __str__(self):
        return "Word: {}\nOptions: {}".format(" ".join(self.content), " ".join(self.options))

    def add_word(self, word):
        self.content.append(word)

    def extend_options(self, options):
        self.options.extend(options)


def construct_image(character):
    doc.stag(
        'img',
        src=character.get_source(),
        klass=character.get_classes(),
        style=character.get_styles(),
        onerror="this.style.display='none'"
    )


def construct_word(word, options, ending=' '):
    print("Constructing : ", word)
    with tag('div', klass=' '.join(options)):
        for char in word:
            char_obj = Character.from_char(char)
            char_obj.randomize()
            construct_image(char_obj)
        if ending == ' ':
            line('span', '', klass='space')


def construct_from_set(word_set):
    for word in word_set.content:
        print(word)
        construct_word(word, word_set.options)

    if word_set.ending:
        line('span', '', klass='space')


def regex_matcher(word):
    match = re.search(r'#\[(\w*)\]#\(((\w*,)?\w*)\)', word)
    if match:
        return match.group(1), match.group(2).split(',')
    else:
        raise Exception('Incorrect Formatting')


def preprocess_words(words):
    new_words = []
    pending_word = None

    for i in range(len(words)):
        word = words[i]
        if '#[' in word:
            start_index = word.find('#[')
            before_string = word[0:start_index]
            if len(before_string) > 0:
                new_words.append(Word(before_string, ending=False))

            if ']#' in word:
                content, options = regex_matcher(word)
                new_words.append(Word(content, options))
            else:
                pending_word = Word(word[start_index + 2:])

        else:
            if ']#' in word:
                if pending_word is None:
                    raise Exception("Check Formatting")

                start_index = word.find(']#')
                before_string = word[0:start_index]
                if len(before_string) > 0:
                    pending_word.add_word(before_string)

                after_string = word[start_index + 2:]
                assert after_string[0] == '('
                assert ')' in after_string
                options_end = after_string.find(')')
                options = after_string[1:options_end].split(",")
                pending_word.extend_options(options)

                new_words.append(pending_word)
                pending_word = None

                after_string = after_string[options_end + 1:]
                if len(after_string) > 0:
                    # Set Ending of last word to blank
                    new_words[-1].ending = False
                    new_words.append(Word(after_string))
            else:
                if pending_word:
                    pending_word.add_word(word)
                else:
                    new_words.append(Word(word))

    return new_words


def main():
    html = ["<html><head><link href='static/style.css' rel='stylesheet' type='text/css'/></head><body><div id='paper'>"]
    with open('content.txt', 'r') as file:
        input_lines = file.readlines()

    # Strips the newline character
    for current_line in input_lines:
        current_line = current_line.strip()
        # print("Line :", current_line)
        words = current_line.split(' ')
        # print(words)
        word_sets = preprocess_words(words)

        with tag('div', klass='lines'):
            for word_set in word_sets:
                # print(word_set)
                construct_from_set(word_set)

    html.append(doc.getvalue())
    html.append('</div></body></html>')
    out_file = open('page.html', 'w')
    out_file.writelines(html)
    out_file.close()


if __name__ == "__main__":
    main()
