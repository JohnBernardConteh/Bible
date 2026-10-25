# Core Packages
import streamlit as st
import streamlit.components.v1 as stc

import re

from datetime import datetime
from zoneinfo import ZoneInfo


# EDA Packages
import pandas as pd
import neattext.functions as nfx
import random

# Data Visualization Packages
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# Utils
@st.cache_data
def load_bible(data):
    df = pd.read_csv(data)
    return df


# from utils import HTML_RANDOM_TEMPLATE, render_entities, get_tags, mytag_visualizer
from utils import *



def run_singleverse():
    st.subheader("Single Verse Retrieval")
    df = load_bible("data/KJV_Bible.csv")
    # st.dataframe(df)
    book_list = df["book"].unique().tolist()
    book_name = st.sidebar.selectbox("Book", book_list)

    chapter = st.sidebar.number_input("Chapter", 1)
    verse = st.sidebar.number_input("Verse", 1)
    bible_df = df[df["book"] == book_name]
    # st.dataframe(bible_df)

    # Layout
    c1, c2 = st.columns([2, 1])

    # Single Verse Layout
    with c1:
        # Find the number of chapters in the selected book.
        total_chapters = int(bible_df["chapter"].max())

        if chapter not in bible_df["chapter"].values:
            st.warning(
                f"{book_name} has {total_chapters} chapters. "
                f"Enter a chapter from 1 to {total_chapters}."
            )

        else:
            # Get the verses in the selected chapter.
            chapter_df = bible_df[bible_df["chapter"] == chapter]
            total_verses = int(chapter_df["verse"].max())

            if verse not in chapter_df["verse"].values:
                st.warning(
                    f"{book_name}, chapter {chapter}, has "
                    f"{total_verses} verses. "
                    f"Enter a verse from 1 to {total_verses}."
                )

            else:
                # Display the selected verse.
                selected_passage = chapter_df[chapter_df["verse"] == verse]

                st.info(f"{book_name} {chapter}:{verse}")
                st.write(selected_passage["text"].iloc[0])

            

                # Verse of the Day
                with c2:
                    # Use Sierra Leone time to determine the current day.
                    today = datetime.now(
                        ZoneInfo("Africa/Freetown")
                    ).date()

                    # A local generator gives the same selection for this date.
                    daily_random = random.Random(today.isoformat())
                    daily_index = daily_random.randrange(len(df))
                    daily_passage = df.iloc[daily_index]

                    mytext = daily_passage["text"]
                    reference = "{} {}:{}".format(daily_passage["book"].split("(")[0].strip(), int(daily_passage["chapter"]), int(daily_passage["verse"]))


                    stc.html(
                        HTML_RANDOM_TEMPLATE.format(reference, mytext),
                        height=300
                    )




            # Search for Topic/Term
            search_term = st.text_input(
                "Term/Topic", key="single_verse_search"
            ).strip()

            if search_term:
                retrieved_df = df[
                    df["text"].str.contains(
                        search_term, case=False, na=False, regex=False
                    )
                ]

                # Count every occurrence of the search term.
                term_count = sum(
                    str(text).lower().count(search_term.lower())
                    for text in retrieved_df["text"]
                )

                st.info(
                    f"'{search_term}' appears {term_count} times "
                    f"in {len(retrieved_df)} verses in the Bible."
                )

                with st.expander("View Results", expanded=True):
                    results = retrieved_df[
                        ["book", "chapter", "verse", "text"]
                    ].reset_index(drop=True)

                    # st.dataframe(results)

                    if not results.empty:
                        # Select a verse to display its full text.
                        selected_index = st.selectbox(
                            "Select a verse to read its full text",
                            options=results.index.tolist(),
                            format_func=lambda i: "{} {}:{}".format(
                                results.loc[i, "book"].split("(")[0].strip(), int(
                                    results.loc[i, "chapter"]), int(
                                    results.loc[i, "verse"])),
                            key="search_result_verse"
                        )

                        selected = results.loc[selected_index]

                        st.info("{} {}:{}".format(selected["book"].split("(")[0].strip(), int(selected["chapter"]), int(selected["verse"])))
                        st.write(selected["text"])
                    else:
                        st.warning("No matching verses found.")




    st.markdown(
    """
    <div style="text-align: center; margin-top: 40px; padding: 15px;">
        JBC@2026
    </div>
    """,
    unsafe_allow_html=True,
)