# Core Packages
import streamlit as st
import streamlit.components.v1 as stc


from utils import HTML_BANNER
from single_verse_app import run_singleverse
from multiverse_app import run_multiverse

def main():
    # st.title("Bible App")
    stc.html(HTML_BANNER)
    menu = ["SingleVerse", "MultipleVerse", "About"]

    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "SingleVerse":
    	run_singleverse()
        
    elif choice == "MultipleVerse":
        run_multiverse()

    else:
        st.subheader("About the Bible Study App")

        st.write(
            "Bible Study App helps you read and explore the "
            "King James Version (KJV) of the Bible."
        )

        st.markdown(
            """
	### What you can do
	- Find a verse by book, chapter and verse number.
	- Select multiple verses from a chapter.
	- Search for words or phrases across the Bible.
	- Read a randomly selected verse.
	- Explore word frequencies and word length distributions.
	- Highlight named entities and parts of speech.

	### Purpose
	This project combines Bible reading with text analysis
	to support personal study and demonstrate Python,
	Streamlit and natural language processing.

	### About the analysis
	Word searches find matching text rather than interpret topics.
	Language analysis tools may misidentify biblical names and
	older English expressions. Use the results as study aids.

	
	Developed by **John Bernard Conteh**.
	"""
        )

        st.caption(
            "Built with Python, Streamlit, pandas, spacy, "
            "TextBlob, Matplotlib and Altair."
        )


if __name__ == "__main__":
    main()
