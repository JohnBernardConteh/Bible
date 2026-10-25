# Core Packages
import streamlit as st
import streamlit.components.v1 as stc

# EDA Packages
import pandas as pd
import neattext.functions as nfx

# Utils
from utils import (
    get_tags,
    mytag_visualizer,
    get_most_common_tokens,
    plot_mendelhall_curve,
    plot_word_freq_with_altair,
)


@st.cache_data
def load_bible(data):
    return pd.read_csv(data)


def run_multiverse():
    st.subheader("Multiple Verse Retrieval")

    df = load_bible("data/KJV_Bible.csv")

    # Select a book.
    book_list = df["book"].unique().tolist()

    book_name = st.sidebar.selectbox(
        "Book",
        book_list,
        format_func=lambda name: name.split("(")[0].strip(),
        key="multi_book",
    )

    display_book_name = book_name.split("(")[0].strip()
    book_df = df[df["book"] == book_name]
    chapters = sorted(book_df["chapter"].unique().tolist())

    selection_mode = st.sidebar.radio(
        "Selection mode",
        ["Select individual verses", "Select a passage range"],
        key="multi_selection_mode",
    )

    if selection_mode == "Select individual verses":
        chapter = st.sidebar.selectbox(
            "Chapter",
            chapters,
            key="multi_chapter",
        )

        chapter_df = book_df[book_df["chapter"] == chapter]
        available_verses = sorted(
            chapter_df["verse"].unique().tolist()
        )

        verses = st.sidebar.multiselect(
            "Verse",
            available_verses,
            default=available_verses[:1],
            key="multi_verses",
        )

        if not verses:
            st.warning("Please select at least one verse.")
            return

        verses = sorted(verses)

        selected_passage = chapter_df[
            chapter_df["verse"].isin(verses)
        ].sort_values(["chapter", "verse"])

        # Format individual or consecutive verse numbers.
        if len(verses) == 1:
            verse_details = str(verses[0])
        elif verses == list(range(verses[0], verses[-1] + 1)):
            verse_details = "{}-{}".format(
                verses[0], verses[-1]
            )
        else:
            verse_details = ",".join(str(v) for v in verses)

        passage_details = "{} {}:{}".format(
            display_book_name, chapter, verse_details
        )

    else:
        st.sidebar.caption(
            "Includes every verse from the start reference "
            "through the end reference."
        )

        # Select the start chapter and verse.
        start_chapter = st.sidebar.selectbox(
            "Start chapter",
            chapters,
            key="multi_start_chapter",
        )

        start_verses = sorted(
            book_df.loc[
                book_df["chapter"] == start_chapter, "verse"
            ].unique().tolist()
        )

        start_verse = st.sidebar.selectbox(
            "Start verse",
            start_verses,
            key="multi_start_verse",
        )

        # End chapter must be at or after the start chapter.
        end_chapters = [
            ch for ch in chapters if ch >= start_chapter
        ]

        end_chapter = st.sidebar.selectbox(
            "End chapter",
            end_chapters,
            key="multi_end_chapter",
        )

        end_verses = sorted(
            book_df.loc[
                book_df["chapter"] == end_chapter, "verse"
            ].unique().tolist()
        )

        # Within one chapter, prevent a reversed verse range.
        if end_chapter == start_chapter:
            end_verses = [
                v for v in end_verses if v >= start_verse
            ]

        end_verse = st.sidebar.selectbox(
            "End verse",
            end_verses,
            key="multi_end_verse",
        )

        # Retrieve the complete passage, including both endpoints.
        after_start = (
            (book_df["chapter"] > start_chapter)
            | (
                (book_df["chapter"] == start_chapter)
                & (book_df["verse"] >= start_verse)
            )
        )

        before_end = (
            (book_df["chapter"] < end_chapter)
            | (
                (book_df["chapter"] == end_chapter)
                & (book_df["verse"] <= end_verse)
            )
        )

        selected_passage = book_df[
            after_start & before_end
        ].sort_values(["chapter", "verse"])

        # Format the passage reference.
        if start_chapter == end_chapter:
            if start_verse == end_verse:
                passage_details = "{} {}:{}".format(
                    display_book_name,
                    start_chapter,
                    start_verse,
                )
            else:
                passage_details = "{} {}:{}-{}".format(
                    display_book_name,
                    start_chapter,
                    start_verse,
                    end_verse,
                )
        else:
            passage_details = "{} {}:{}–{}:{}".format(
                display_book_name,
                start_chapter,
                start_verse,
                end_chapter,
                end_verse,
            )

    st.info(passage_details)
    st.caption(f"{len(selected_passage)} verses selected.")

    # Display each verse under its chapter heading.
    for chapter_number, chapter_passage in selected_passage.groupby(
        "chapter", sort=True
    ):
        st.markdown(f"**Chapter {int(chapter_number)}**")

        for _, row in chapter_passage.iterrows():
            st.write(
                "{}. {}".format(
                    int(row["verse"]), row["text"]
                )
            )

    # Combine all selected verses for analysis.
    docx = " ".join(
        selected_passage["text"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    if not docx.strip():
        st.warning(
            "The selected passage contains no text to analyse."
        )
        return

    st.success("Study Mode")

    if st.button(
        "Analyse selected passage",
        key="multi_analyse",
    ):
        # Display coloured POS tags verse by verse.
        with st.expander("Visualize POS Tags", expanded=True):
            verses_html = []

            for chapter_number, chapter_passage in (
                selected_passage.groupby("chapter", sort=True)
            ):
                verses_html.append(
                    f"<h4>Chapter {int(chapter_number)}</h4>"
                )

                for _, row in chapter_passage.iterrows():
                    verse_text = (
                        "" if pd.isna(row["text"])
                        else str(row["text"])
                    )

                    tagged_docx = get_tags(verse_text)
                    processed_tags = mytag_visualizer(tagged_docx)

                    verses_html.append(
                        f"""
                        <div style="margin-bottom:14px;">
                            <strong>{int(row["verse"])}.</strong>
                            {processed_tags}
                        </div>
                        """
                    )

            stc.html(
                """
                <div style="
                    font-family:Arial, sans-serif;
                    font-size:16px;
                    line-height:1.8;
                    overflow-wrap:anywhere;
                ">
                """
                + "\n".join(verses_html)
                + "</div>",
                height=300,
                scrolling=True,
            )

        with st.expander("Key Words"):
            processed_docx = nfx.remove_stopwords(docx)
            keywords_tokens = get_most_common_tokens(
                processed_docx, 5
            )
            st.write(keywords_tokens)

        with st.expander("Mendelhall Verse Curve"):
            plot_mendelhall_curve(docx)

        with st.expander("Word Frequency Plot"):
            plot_word_freq_with_altair(docx)


  


    st.markdown(
    """
    <div style="text-align: center; margin-top: 40px; padding: 15px;">
        JBC@2026
    </div>
    """,
    unsafe_allow_html=True,
)