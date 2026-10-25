# Core Packages
import streamlit as st
import streamlit.components.v1 as stc


from utils import HTML_BANNER
from single_verse_app import run_singleverse
from multiverse_app import run_multiverse
from story_app import run_story

def main():
    # st.title("Bible App")
    stc.html(HTML_BANNER)
    menu = ["SingleVerse", "MultipleVerse", "Story", "About"]

    choice = st.sidebar.selectbox("Menu", menu)
    if choice == "SingleVerse":
    	run_singleverse()
        
    elif choice == "MultipleVerse":
        run_multiverse()

    elif choice == "Story":
    	run_story()

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
	- Explore 50 simplified Bible stories.
	- Search by title, name or phrase.
	- Read a Story of the Day.
	- Explore word frequencies and word length distributions.
	- Highlight named entities and parts of speech.
	"""
        )

        st.caption(
            "Built with Python, Streamlit, pandas, spacy, "
            "TextBlob, Matplotlib and Altair."
        )


    st.markdown(
    """
    <div style="text-align: center; margin-top: 40px; padding: 15px;">
        JBC@2026
    </div>
    """,
    unsafe_allow_html=True,
)


if __name__ == "__main__":
    main()
