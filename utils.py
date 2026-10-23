# Core Packages
import streamlit as st
import streamlit.components.v1 as stc

# Text Analysis
import nltk
import spacy
from spacy import displacy
from textblob import TextBlob

# Data Processing
import pandas as pd
import re
from collections import Counter
from html import escape

# Data Visualization
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import altair as alt


# Download language resources once per app process.
@st.cache_resource
def prepare_nltk():
    resources = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "brown",
    ]

    for resource in resources:
        if not nltk.download(resource, quiet=True):
            raise RuntimeError(
                f"Could not download NLTK resource: {resource}"
            )

    return True


# Load spaCy only when entity analysis is used.
@st.cache_resource
def load_spacy_model():
    return spacy.load("en_core_web_sm")


HTML_RANDOM_TEMPLATE = """
<div style='padding:10px; background-color:#E1E2E1;
border-radius:8px 34px 9px 26px;
border:2px ridge #000000; color:#000000;'>

    <h5>Verse of the Day</h5>

    <p>{1}</p>

    <div style='background-color:#d9edf7; color:#0c5460;
    padding:10px; border-radius:5px; margin-top:10px;'>
        <strong>{0}</strong>
    </div>

</div>
"""

HTML_WRAPPER = """
<div style="overflow-x:auto;
border:1px solid #e6e9ef;
border-radius:0.25rem;
padding:15px;
margin-bottom:15px;">
    {}
</div>
"""

HTML_BANNER = """
<div style="background-color:#464e5f;
padding:10px; border-radius:10px;">
    <h1 style="color:white; text-align:center;">
        KJV Bible App
    </h1>
</div>
"""


def render_entities(raw_text):
    nlp = load_spacy_model()
    docx = nlp(raw_text)

    html = displacy.render(docx, style="ent")
    html = html.replace("\n\n", "\n")

    result = HTML_WRAPPER.format(html)
    stc.html(result, height=1000, scrolling=True)


def get_word_tokens(docx):
    # Combine words regardless of case or surrounding punctuation.
    return re.findall(
        r"\b[a-z]+(?:'[a-z]+)*\b",
        docx.lower(),
    )


def plot_mendelhall_curve(docx):
    tokens = get_word_tokens(docx)

    if not tokens:
        st.info("No words available to plot.")
        return

    word_length_count = Counter(
        len(token) for token in tokens
    )

    x, y = zip(*sorted(word_length_count.items()))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, y, marker="o")
    ax.set_title("Word Length Distribution")
    ax.set_xlabel("Word length (characters)")
    ax.set_ylabel("Number of words")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def get_most_common_tokens(docx, num=5):
    tokens = get_word_tokens(docx)
    return dict(Counter(tokens).most_common(num))


def plot_word_freq_with_altair(docx, num=10):
    # Apply the same counting rules used for keywords.
    most_common_tokens = get_most_common_tokens(docx, num)

    if not most_common_tokens:
        st.info("No words available to plot.")
        return

    word_freq_df = pd.DataFrame(
        list(most_common_tokens.items()),
        columns=["tokens", "counts"],
    )

    chart = alt.Chart(word_freq_df).mark_bar().encode(
        x=alt.X(
            "tokens:N",
            title="Word",
            sort="-y",
        ),
        y=alt.Y(
            "counts:Q",
            title="Frequency",
        ),
        tooltip=["tokens:N", "counts:Q"],
    )

    st.altair_chart(chart, use_container_width=True)


def get_tags(docx):
    if not docx.strip():
        return []

    prepare_nltk()
    return TextBlob(docx).tags


TAGS = {
    # Nouns
    "NN": "green",
    "NNS": "green",
    "NNP": "green",
    "NNPS": "green",

    # Verbs
    "VB": "blue",
    "VBD": "blue",
    "VBG": "blue",
    "VBN": "blue",
    "VBP": "blue",
    "VBZ": "blue",

    # Adjectives
    "JJ": "red",
    "JJR": "red",
    "JJS": "red",

    # Adverbs
    "RB": "teal",
    "RBR": "teal",
    "RBS": "teal",

    # Other tags
    "IN": "gray",
    "POS": "darkgoldenrod",
    "PRP$": "magenta",
    "PRP": "magenta",
    "DT": "black",
    "DET": "black",
    "CC": "black",
    "CD": "black",
    "WDT": "black",
    "WP": "black",
    "WP$": "black",
    "WRB": "black",
    "EX": "darkgoldenrod",
    "FW": "darkgoldenrod",
    "LS": "darkgoldenrod",
    "MD": "darkgoldenrod",
    "PDT": "darkgoldenrod",
    "RP": "darkgoldenrod",
    "SYM": "darkgoldenrod",
    "TO": "darkgoldenrod",
}


def mytag_visualizer(tagged_docx):
    colored_text = []

    for token, tag in tagged_docx:
        # Preserve tokens whose tags are not in the colour map.
        color = TAGS.get(tag, "black")

        colored_text.append(
            '<span style="color:{};" title="{}">{}</span>'.format(
                color,
                escape(str(tag), quote=True),
                escape(str(token)),
            )
        )

    return " ".join(colored_text)