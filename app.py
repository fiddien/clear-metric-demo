from flask import Flask, request, render_template
from parse import Sentence
from score import ClearMetric
import re

app = Flask('app', template_folder='template')

rules = [
    'Character is the subject',
    'Action is the verb',
    'Avoids long abstract subject',
    'Avoids long introductory phrases and clauses',
    'Avoids interrupting subject-verb connection',
]

@app.route('/', methods=['GET']) # Homepage
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def inference():
    sents = request.values.get('sent')
    example = request.values.get('option')
    if sents=='':
        if example is None:
            return render_template('index.html', result="")
        sents = example
    try:
        sents = Sentence(sents)
        scorer = ClearMetric(sents)
        scores = scorer.score_sents()
        return render_template('index.html', result=build_result(sents, scores))
    except AssertionError:
        return render_template('index.html', result="Internal Error")


def build_result(sents, scores):

    s = ''
    i = 0
    for sent, structure, story, score in \
        zip(sents.doc.sents, sents.structures, sents.stories, scores):
        i += 1
        s += f'<h2>Sentence #{i}</h2>\n'
        tokens = [t for t in sent]
        start = sent[0].i
        sent_str = sent.text
        
        if structure:
            for item in structure:
                # get the subject span
                su = item['subject']
                subj_start = su[0].idx - sent.start_char
                subj_end = subj_start + len( sent[ su[0].i-start : su[-1].i+1-start ].text )
                subj_str = f'<mark data-entity="subj">{sent.text[subj_start:subj_end]}</mark>'
                # get the verb span
                ve = item['verb']
                verb_start = ve[0].idx - sent.start_char
                verb_end = verb_start + len( sent[ ve[0].i-start : ve[-1].i+1-start].text )
                verb_str = f'<mark data-entity="verb">{sent.text[verb_start:verb_end]}</mark>'
                # resconstruct the sentence
                s += sent_str[:subj_start] + subj_str + sent_str[subj_end:verb_start] + verb_str + sent_str[verb_end:]
                s += '<hr>'
        else:
            s += f"{sent_str}<br><i>No pair of subject and verb found.</i><hr>"

        if story:
            for item in story:
                # get the character span
                char_start = tokens[item['character'][0].i].idx - sent.start_char
                char_end = tokens[item['character'][-1].i].idx + len(item['character'][-1].text) - sent.start_char
                char_str = f'<mark data-entity="char">{sent.text[char_start:char_end]}</mark>'
                # get the action span
                actn_start = tokens[item['action'][0].i].idx - sent.start_char
                actn_end = tokens[item['action'][-1].i].idx + len(item['action'][-1].text) - sent.start_char
                actn_str = f'<mark data-entity="actn">{sent.text[actn_start:actn_end]}</mark>'
                # resconstruct the sentence
                if char_start < actn_start:
                    s += sent_str[:char_start] + char_str + sent_str[char_end:actn_start] + actn_str + sent_str[actn_end:]
                else:
                    s += sent_str[:actn_start] + actn_str + sent_str[actn_end:char_start] + char_str + sent_str[char_end:]
                s += '<hr>'
        else:
            s += f"{sent_str}<br><i>No pair of character and action found.</i>"

        s += '<div class="result-box">'
        s += '<b>Adherence to the Principles of Clear Writing</b>'
        for i, r in enumerate(score):
            if r==1:
                s += f'<p style="color:red">𐄂 {rules[i]}<p>'
            else:
                s += f'<p>✓ {rules[i]}<p>'
        s += '</div>'
    return s

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=9696)
    # app.run()