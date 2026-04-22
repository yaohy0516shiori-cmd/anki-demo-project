# Tech detail

# System Scope 

## V1

### Scope Statement

> V1 is a single-user, local-first memorization system for exam preparation. The system supports creating source learning content, generating review cards from that content, organizing generated cards into decks, running study sessions, recording review results, and scheduling future review. The main goal of the system is to support a stable personal memorization workflow rather than multi-user collaboration, cloud sync, or advanced automation.

------

### In Scope

> The V1 system includes the following capabilities:
>
> - Create, update, delete, and search source learning content
> - Support simple note types such as basic, reverse, and cloze
> - Generate one or more review cards from a note
> - Organize generated cards into decks
> - Start a study session from a deck
> - Review cards by revealing an answer or checking a user response, depending on the note type
> - Use user-rated review as the primary rating mode
> - Record review logs for each review event
> - Update the next review time with a simple scheduling strategy
> - Store user data locally for persistent use

------

### Out of Scope

> The following capabilities are not part of the V1 system scope:
>
> - Multi-user collaboration or sharing
> - Public deck publishing or marketplace features
> - Cloud sync across devices
> - AI-assisted note or card generation
> - Advanced automatic answer checking for all note types
> - Complex custom study plans
> - Large-scale distributed architecture
> - Async task pipelines for file import or background processing

------

### Operating Assumptions

> The V1 system is built under the following assumptions:
>
> - The system serves one user only
> - Local storage is the default operating mode
> - Manual content creation is the primary input method
> - Notes represent source learning content in the user’s personal content library
> - Notes may generate one or more review cards depending on the note type
> - Each generated card belongs to one deck at a time in V1
> - Tags and hints belong to notes rather than cards
> - User-rated review is the primary review mode in V1
> - Cloze practice may be included, but users evaluate their own answers after seeing the expected result
> - Importing external files or decks is not part of the primary V1 workflow

# Core Domain Objects

## Note/

A note represents the source learning content created by the user. It is stored in the user’s personal content library and serves as the source from which one or more review cards may be generated. A note contains the main learning content, its note type, and note-level metadata such as tags and hints.

Parameters:

```python
class Note:
    """
    Core concept:
    - represents source learning content
    - belongs to the user's content library
    - may generate one or more review cards

    Core fields:
    - note_id
    - note_type_id
    - fields
    - tags
    - hints
    """
```



## NoteType/

A note type defines how a note should be interpreted and how review cards should be generated from it. In V1, the supported note types are basic, reverse, and cloze. Different note types may generate different numbers of cards and different review interactions.

Parameters:

```python
class NoteType:
    def __init__(self,note_type_id:int | None,name:str,field_names:List[str],kind:str):
        '''
        Validate and create a note type
        Args:
            note_type_id: The id of the note type
            name: The name of the note type
            field_names: The fields of the note type
            kind: The kind of the note type
        Returns:
            A NoteType object
        private attributes to prevent external modification
        __init__ will be called when a new note type is created
        judge the type of the arguments
        '''
        kind_list=["basic", "cloze", "basic_reverse"]
```



## Card/

A card is the review unit used during study sessions. Cards are generated from notes and are used for repeated review. Each card belongs to one deck at a time in V1 and stores review-related state such as status, next review time, interval, repetitions, and lapses.

```python
class Card:
    '''
        Validate and create a note type
        Args:
    	select_status={'new','learning','review','relearning'}
        note_id: card belongs to which note,
        deck_id: card belongs to which deck,
        card_id: unique identifier of a review card
		template_ord: identifies which generated card template or cloze instance this 	card represents under a note
        status:str='new', only four status
        due: date | None=None, the next scheduled review date or time
        interval: int=0, review countdown
        ease: float=2.5, factor of difficulty
        reps: int=0, count
        lapses: int=0, count
        step_index: the current learning or relearning step, if applicable
        created_at:str | None=None
        updated_at:str | None=None
     '''
```

In V1, card_id is the unique card identifier. The pair (note_id, template_ord) helps describe which card was generated from a note.

## Deck/

A deck is a study organization unit that groups generated review cards for review sessions. In V1, decks do not own notes directly. Instead, they organize cards that were generated from notes.

```python
class Deck:
    '''
    deck_id:
    create_at:
    update_at:
    deck_name: default f"Deck{nums}"
    '''
```



## ReviewLog/

A review log records one review event on a card. It stores the review result, the card state before and after the review, and the review time. Review logs are used to track study history and support later analysis.

```python
class ReviewLog:
    '''
        record complete review process for a card
        which includes:
        card/rating/what change after review
        view_rating=['good','again'] the review result submitted by the user in V1
        # Construct one review log with old/new state and scheduling fields
         Core fields:
        - review_log_id
        - card_id
        - deck_id
        - rating
        - old_status / new_status
        - old_due / new_due
        - old_interval / new_interval
        - old_ease / new_ease
        - old_lapses / new_lapses
        - old_reps / new_reps
        - old_step_index / new_step_index
        - review_time
    '''
    
```



## Scheduler/

The scheduler is the domain component that decides the next review timing and updated card state after a review result is submitted. In V1, the scheduler uses a simple review strategy rather than an advanced adaptive algorithm.

```python
class Scheduler_v1:
    """
    Core concept:
    - updates card review state after a submitted review result

    V1 behavior:
    - supports simple transitions among new, learning, review, and relearning
    - accepts simple rating values such as "good" and "again"
    - returns updated review-related card state
    """
```



# Core Use Cases

## Use Case 1: Create Note

The user creates a note and chooses a note type. The system validates the input content, stores the note in the user’s content library, and keeps its note-level metadata such as tags and hints.

## Use Case 2: Generate Cards from Note

After a note is created or updated, the system generates one or more review cards according to the selected note type. The generated cards reference the source note and become available for later study.

## Use Case 3: Assign Cards to Deck

The user assigns generated cards to a deck. In V1, each generated card belongs to one deck at a time. The deck is then used as the entry point for study sessions.

## Use Case 4: Start Study Session

The user starts a study session from a selected deck. The system loads eligible cards from that deck according to the current review state and review timing.

## Use Case 5: Review Card

During a study session, the user reviews a card by revealing the answer or checking their own response, depending on the note type. In V1, review results are primarily rated by the user.

## Use Case 6: Submit Review Result

After the user gives a review result, the system records a review log, updates the card state, and calculates the next review time using the scheduler.

## Use Case 7: Search and Update Notes

The user can search notes by keywords or partial text, update note content, update tags, and update hints. When a note is updated, the system may regenerate its related review cards according to the note type rules.

# Data Ownership Rules

## Rule 1: Notes own source learning content

Notes are the source content objects in the system. The main study content is stored at the note level rather than the card level.

## Rule 2: Note types define card generation rules

A note type belongs to the note interpretation layer. It determines how many cards may be generated from a note and how they should be reviewed.

## Rule 3: Cards reference notes

Cards do not own the original learning content directly. Instead, each card references its source note and represents a reviewable instance generated from that note.

## Rule 4: Decks organize cards, not notes

Decks do not directly own notes in V1. Their purpose is to organize generated review cards for study sessions.

## Rule 5: Each card belongs to one deck at a time in V1

Although a note may generate multiple cards, each generated card is assigned to one deck at a time in the first version. Multi-deck ownership is outside the current V1 scope.

## Rule 6: Tags belong to notes

Tags are note-level metadata used for organization, search, and memorization support. They are not primarily stored at the card level in V1.

## Rule 7: Hints belong to notes

Hints are note-level support content. They may be shown on the answer side during review, but their source of ownership remains the note.

## Rule 8: Review logs belong to review events on cards

A review log records one review event for one card. It is linked to the card’s review history rather than to the note as a content object.

## Rule 9: Scheduler updates card state, not note content

The scheduler only changes review-related card state, such as next review time and repetition state. It does not modify the original note content.

## Rule 10: Deck assignment affects study entry, not note ownership

Assigning a generated card to a deck determines where the card is studied from, but it does not change the ownership of the source note.

# Module Responsibilities

## Note Service

- Create, update, delete, and search notes
- Validate note content against the selected note type
- Coordinate note-related workflows when note changes affect generated cards

## Note Repository

- Persist and load note data
- Support create, read, update, delete, and search operations for notes
- Do not contain card-generation or scheduling logic

## Card Service

- Generate one or more cards from a note according to its note type
- Reconcile generated cards when a note is updated
- Retrieve cards by note, card id, or deck
- Manage review-related card state updates

## Card Repository

- Persist and load generated card data
- Support lookup by card_id, note_id, and deck_id
- Support updating review-related card state

## Deck Service

- Create, update, delete, and query decks
- Assign generated cards to a deck
- Move cards between decks in V1
- Provide deck-level entry points for study sessions

## Deck Repository

- Persist and load deck data
- Support basic deck CRUD
- Support deck-related card membership queries

## Review Log Service

- Record one review event after a card is rated
- Coordinate logging and scheduler output during review submission
- Query review history for cards or study history views

## Review Log Repository

- Persist review event records
- Retrieve review history by card or by time range
- Do not contain scheduling logic

## Render

- Render review-facing prompt and answer content from a note and a generated card
- Support rendering rules for basic, reverse, and cloze note types

## Study Service

- Start a study session from a selected deck
- Load eligible cards for the session
- Provide the next card in study order
- Coordinate answer reveal or response-checking flow
- Submit review results through review logging and scheduler logic

## Scheduler

- Calculate the next review-related state for a card after a submitted rating
- Return updated scheduling fields without persisting them directly

# Scheduler

## V1

A simple scheduling policy for V1 review flow. It updates card review state such as status, due, interval, repetitions, lapses, and step_index after a submitted rating.

Scheduler with same-day steps.

​    State meaning:
   - new: never answered before
   - learning: same-day learning flow
   - review: graduated review flow
   - relearning: failed review, same-day recovery flow

   step_index is used to represent the current step in learning or relearning flow:
- None for new and review
- int >= 0 for learning and relearning

​    Default rule in this file:
   - new -> learning(step_index=0) on first answer
   - learning needs 4 successful goods to graduate to review
   - review + again -> relearning(step_index=0)
   - review + good -> update interval, stop review today
   - relearning needs 3 successful goods to return to review

Input:
- current card state
- submitted rating
- review date (optional, for testing or deterministic scheduling)

Output:
- updated review-related card state

​    ==It does NOT save anything. It only returns the calculated result.==

# Minimal Persistence Decisions

## V1 Persistence Goal

V1 needs a simple local persistence layer so that user-created content, generated review cards, decks, and review history can survive application restarts. The persistence design should support the core memorization workflow without introducing cloud sync, multi-user coordination, or distributed storage complexity.

## Storage Choice

V1 uses **SQLite** as the default persistence solution.

Reason:

- V1 is single-user
- V1 is local-first
- The expected data scale is small to medium
- SQLite is easy to embed, test, and debug
- It is sufficient for note, card, deck, and review log persistence in the first version

PostgreSQL or other database systems are not required in V1. They may be considered later if the product evolves toward cloud sync, multi-user sharing, or larger-scale deployment.

## Objects That Must Be Persisted

The V1 persistence layer must store these domain objects:

### Note

Persist source learning content and note-level metadata.

### Card

Persist generated review cards and their review-related state.

### Deck

Persist deck definitions used as study entry points.

### ReviewLog

Persist review event history for cards.

## Object Relationships to Preserve

The persistence layer must preserve the following relationships:

- A note has one note type
- A note may generate one or more cards
- A card references one source note
- A card belongs to one deck at a time in V1
- A deck organizes cards, not notes
- A review log records one review event for one card
- Tags and hints belong to notes, not cards

## Minimal Persistence Rules

### Rule 1: Notes are stored independently from decks

Notes live in the user’s content library. They do not belong directly to a deck.

### Rule 2: Cards store review state

Cards must persist review-related state such as:

- status
- due
- interval
- reps
- lapses
- step_index
- deck assignment

### Rule 3: Review logs are append-style records

Review logs should be treated as historical records of review events. They are mainly created and queried, not edited as a normal workflow.

### Rule 4: Scheduler does not persist data directly

The scheduler only calculates the next card state. Repositories persist the updated card state and review log.

### Rule 5: Rendering data comes from notes

Cards should not duplicate the full source learning content unnecessarily. They should reference notes, and review rendering should use note data plus card metadata.

## Repository-Level Decision

V1 uses a repository pattern to separate domain logic from persistence logic.

The persistence layer should include at least:

- Note Repository
- Card Repository
- Deck Repository
- ReviewLog Repository

Repositories are responsible for:

- storing and loading data
- basic CRUD and lookup operations
- persistence-specific concerns

Repositories are not responsible for:

- card generation rules
- scheduling rules
- review workflow orchestration
- rendering rules

## Minimal Query Needs in V1

The persistence layer must support at least these lookup patterns:

### Notes

- get note by id
- search notes by keyword or partial text
- list notes
- update note
- delete note

### Cards

- get card by id
- list cards by note
- list cards by deck
- update card review state
- delete or reconcile cards when note generation rules change

### Decks

- get deck by id
- list decks
- create, update, delete deck

### Review Logs

- create review log
- list logs by card
- optionally list logs by time or recent activity

## What Is Not Required Yet

The V1 persistence layer does **not** need:

- cloud sync
- multi-user ownership or permissions
- shared deck publishing
- event queues
- background workers
- distributed storage
- caching layers such as Redis
- analytics warehouse systems
- large-scale data platforms such as Hadoop
- advanced database sharding or replication

## Design Preference for V1

The persistence design should favor:

- clarity over flexibility
- correctness over optimization
- simple relationships over future-proof abstraction
- easy local testing over production-scale complexity
