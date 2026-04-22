# Tech Doc ---- Product design

# Product Goal

This product is a learning and memorization app that helps people retain different types of material. It enables users to create, organize, and review learning content in a structured way so they can remember knowledge more effectively over time

## V1

V1 is a single-user memorization tool for students preparing for exams. It helps users turn study content into reviewable learning materials, practice them through simple card-based review, and revisit them over time with system-supported scheduling.

# Target user and scenarios

## V1

Target User for V1

> V1 is designed for middle school students preparing for the high school entrance examination. These users need to memorize large amounts of study content efficiently and review it repeatedly over time. They need a simple and reliable tool to organize learning materials and support daily memorization practice.

Primary Learning Scenarios

> The primary learning scenarios for V1 are English word memorization and recitation of Chinese ancient texts and poems. These scenarios best match the initial card types and review flow of the product.
>
> In V1, users mainly study English words through simple front/back recall and practice Chinese ancient text recitation through cloze-based review.

Secondary / Compatible Scenarios

> V1 may also support formula memorization in math, chemistry, and physics, as well as fact-based learning in politics, history, and geography. However, these are secondary scenarios rather than the main design focus of the first version.

# Core User Flow

1. User creates source content
2. User chooses a note type
3. System generates one or more cards
4. User assigns the generated cards to a deck
5. User starts a study session
6. User reveals or answers the card
7. User rates the result
8. System stores the review log and updates the next review time

## V1 Assumptions

In V1, notes represent source learning content in the user’s personal database. Decks do not own notes directly; instead, they organize the review cards generated from notes.

- Single user
- Local-first
- Manual content creation is the primary input method
- Notes represent source learning content in the user’s personal database
- Notes may generate one or more review cards depending on the note type
- Each generated card belongs to one deck at a time
- Tags and hints belong to notes
- Only simple note types are included in V1, such as basic, reverse, and cloze
- In V1, user-rated review is the primary rating mode
- Cloze practice may still be included in V1, but users primarily evaluate their own answers after seeing the expected result
- Automatic checking is not a core V1 requirement, because it would require more detailed note type design and answer-matching rules

# MVP scope

## V1

1. Users can create, update, delete, and search study content
2. Users can organize generated review cards into decks
3. V1 supports simple learning types, including basic, reverse, and cloze
4. Users can start a study session and review cards
5. Users can rate their review results, and the system records the rating for later scheduling
6. The system supports basic repeated review by scheduling cards for future study
7. Users can add tags to study content to support organization and memorization
8. The system records review history, and users can view basic review logs

# Feature List

## V1

### Content

1. Users create a note and choose a note type
2. The system generates one or more review cards from a note
3. Users assign generated review cards to a deck
4. Users add tags to notes for organization and memorization support
5. Users can search notes by keywords or partial text
6. Users can update notes and their tags
7. Users can add hints to notes and view them during review

### Learning

1. Users can start a study session from a deck
2. Users can view the prompt side of a card and reveal the answer side
3. Review results are primarily rated by the user in V1
4. The system records review logs and updates the next review time

# Out of Scope

## Out of Scope for V1

- Multi-user sharing
- Public deck sharing and marketplace
- AI-assisted card generation
- Custom study plans and advanced scheduling
- Importing external files or decks is not part of the primary V1 scope

## Engineering Non-goals for V1

- No distributed system
- No async task queue
- Local-first storage only
- SQLite is the default storage solution for V1 and is sufficient for the expected scale

# Future Architecture Considerations

If the product evolves from single-user local use to cloud sync or multi-user sharing, SQLite may later be replaced by PostgreSQL.

Async processing may be introduced later for file import, AI-assisted card generation, and large public deck publishing workflows.



