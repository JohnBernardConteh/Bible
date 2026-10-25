# Core Packages
import streamlit as st

import re
import random

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


# Utils
STORY_FOLDER = Path(__file__).resolve().parent / "bible_stories"


@st.cache_data
def load_stories(story_files):
    stories = []

    for filename, modified_time in story_files:
        story_path = Path(filename)

        raw_text = story_path.read_text(
            encoding="utf-8-sig"
        )

        # Use the first Markdown heading as the story title.
        title_match = re.search(
            r"^#[ \t]+(.+)$",
            raw_text,
            flags=re.MULTILINE,
        )

        if title_match:
            title = title_match.group(1).strip()

            story_text = (
                raw_text[:title_match.start()]
                + raw_text[title_match.end():]
            )

        else:
            title = f"Story {int(story_path.stem)}"
            story_text = raw_text

        # Remove image links.
        story_text = re.sub(
            r"!\[[^\]]*\]\([^)]*\)",
            "",
            story_text,
        )

        # Remove excessive blank lines.
        story_text = re.sub(
            r"\n[ \t]*\n(?:[ \t]*\n)+",
            "\n\n",
            story_text,
        ).strip()

        if not story_text:
            continue

        # Create plain text for searching and previews.
        plain_text = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            story_text,
        )

        plain_text = re.sub(
            r"[#*_`>]",
            "",
            plain_text,
        )

        plain_text = re.sub(
            r"\s+",
            " ",
            plain_text,
        ).strip()

        stories.append({
            "id": story_path.stem,
            "title": title,
            "text": story_text,
            "plain_text": plain_text,
        })

    return stories


def get_story_preview(text, limit=350):
    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0] + "..."


def display_story(story):
    st.info(story["title"])

    st.write(
        get_story_preview(story["plain_text"])
    )

    with st.expander("Read Full Story"):
        st.markdown(story["text"])


def clear_story_search():
    # Selecting a story switches away from search results.
    st.session_state["bible_story_search"] = ""


# Application
def run_story():
    st.subheader("Bible Stories")

    # Check the stories folder.
    if not STORY_FOLDER.is_dir():
        st.error(
            "The bible_stories folder was not found. "
            "Place it beside app.py and story_app.py."
        )
        return

    # Find numbered story files.
    story_paths = sorted(
        (
            path
            for path in STORY_FOLDER.glob("*.md")
            if path.stem.isdigit()
        ),
        key=lambda path: int(path.stem),
    )

    if not story_paths:
        st.warning(
            "No story files were found. "
            "Add files such as 01.md and 02.md "
            "to bible_stories."
        )
        return

    try:
        # Refresh the cache when story files change.
        story_files = tuple(
            (
                str(path),
                path.stat().st_mtime_ns,
            )
            for path in story_paths
        )

        stories = load_stories(story_files)

    except (OSError, UnicodeError) as exc:
        st.error(f"Could not read the story files: {exc}")
        return

    if not stories:
        st.warning(
            "The story files contain no readable text."
        )
        return

    story_lookup = {
        story["id"]: story
        for story in stories
    }

    # Story Menu
    # Start with no story selected.
    selected_story_id = st.sidebar.selectbox(
        "Select a Story",
        options=[None] + list(story_lookup),
        format_func=lambda story_id: (
            "Choose a story"
            if story_id is None
            else story_lookup[story_id]["title"]
        ),
        key="bible_story_selection",
        on_change=clear_story_search,
    )

    # Search remains available in every view.
    search_term = st.text_input(
        "Search for a Story",
        placeholder="Enter a title, name or phrase",
        key="bible_story_search",
    ).strip()

    # Search Results
    # A search hides both the selected story and daily story.
    if search_term:
        search_value = search_term.casefold()

        matching_stories = [
            story
            for story in stories
            if search_value in (
                story["title"]
                + " "
                + story["plain_text"]
            ).casefold()
        ]

        st.info(
            f"Found {len(matching_stories)} "
            f"matching stories for '{search_term}'."
        )

        if matching_stories:
            matching_lookup = {
                story["id"]: story
                for story in matching_stories
            }

            result_story_id = st.selectbox(
                "Select a matching story",
                options=list(matching_lookup),
                format_func=lambda story_id: (
                    matching_lookup[story_id]["title"]
                ),
                key="bible_story_search_result",
            )

            display_story(
                matching_lookup[result_story_id]
            )

        else:
            st.warning(
                "No matching stories found. "
                "Try another name, word or phrase."
            )

    # Selected Story
    # Selecting a story hides the daily story.
    elif selected_story_id is not None:
        display_story(
            story_lookup[selected_story_id]
        )

    # Story of the Day
    # Display only when no story or search is active.
    else:
        today = datetime.now(
            ZoneInfo("Africa/Freetown")
        ).date()

        daily_random = random.Random(
            f"bible-story-{today.isoformat()}"
        )

        daily_story = stories[
            daily_random.randrange(len(stories))
        ]

        st.subheader("Story of the Day")

        st.caption(
            today.strftime("%d %B %Y")
        )

        # Show a preview with a Read Full Story expander.
        display_story(daily_story)

    # Attribution
    st.caption(
        "Stories adapted from unfoldingWord® Open Bible Stories, "
        "licensed under CC BY-SA 4.0. "
        "These are simplified Bible retellings."
    )

    st.markdown(
        "[Story source](https://www.openbiblestories.org/)"
        " | "
        "[CC BY-SA 4.0 licence]"
        "(https://creativecommons.org/licenses/by-sa/4.0/)"
    )


if __name__ == "__main__":
    run_story()