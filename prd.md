### Product Specification: AI-Powered Personalized Language Learning Application

#### 1.0 Introduction and Vision

This document provides a unified technical specification for the design and implementation of a local-first, AI-powered language learning application. Its purpose is to serve as the single source of truth for the internal development team, outlining the architecture, data model, and minimum viable product (MVP) scope.

The product's core vision is to create a "personal language operating system." This system will transform passive language exposure into an active, adaptive learning experience by building a personalized knowledge graph of the user's understanding, tracking specific error patterns, and tailoring practice to systematically address individual weaknesses.

#### 1.1 Core Problem

The current market for language learning applications is dominated by generic, one-size-fits-all platforms that fail to address the specific needs of individual learners. These applications treat learning as the memorization of vocabulary lists, neglecting the interconnected nature of language. The primary problem this application solves is the gap between these systems and the need for a deeply personalized tool that models an individual's unique error patterns, knowledge gaps, and learning context. It moves beyond simple "correct/incorrect" scoring to build an "error fingerprint" that drives every aspect of the learning experience.

#### 1.2 Target Audience

The target audience for this document is the internal development team. The content is structured and technical, intended to provide clear, actionable requirements for engineering and design.

#### 1.3 Guiding Principles

The architecture and product strategy are guided by a set of core principles that ensure a focused and effective initial product.

- **Local-First & Privacy-Preserving**: All user data, including learning history and personal texts, must be processed and stored on the user's local machine. Privacy is a foundational, non-negotiable feature.
- **Graph-Shaped, Not List-Based**: The data model must prioritize the rich relationships between linguistic items—such as collocations, confusables, and grammatical patterns—over simple, disconnected vocabulary lists. Fluency lives in the connections.
- **Personalization as the Core Model**: The application's behavior is not a feature to be added but the central organizing principle. The entire system must adapt based on a detailed "error fingerprint" of the user.
- **Ruthless MVP Scope**: The initial version must focus on a tight, high-value core loop that can be shipped quickly. This allows for rapid validation of the core concept and provides a stable foundation for future iteration.
- **Constrained LLM Usage**: The Large Language Model (LLM) will be treated as a powerful but specialized component. It will be used for specific, well-defined tasks with strict, structured outputs (primarily JSON) to ensure reliability, prevent hallucinations, and maintain system stability.

These principles inform the following specification, which details the MVP required to bring this vision to life.

---

### 2.0 Minimum Viable Product (MVP) Definition

The strategic goal of the MVP is to ship a genuinely useful and coherent core learning loop as quickly as possible. This approach allows us to validate the central thesis—that a graph-based, error-driven model is superior to list-based learning—and establish a stable platform for subsequent feature development. The scope is intentionally and ruthlessly constrained to this core loop.

#### 2.1 The Core User Loop

The fundamental MVP experience is defined by a four-step user loop that transforms passive content into an active, personalized practice session.

1. **Capture**: The user ingests German text into the application. This is the entry point for all new linguistic material.
2. **Understand & Store**: The system uses a local LLM to extract learnable items (words, phrases, patterns) and their relationships from the captured text. This structured data is stored in a local, graph-like database.
3. **Personalize**: The system tracks every user interaction, logging successes and, more importantly, failures. These events are classified against an error taxonomy to build and continuously update the user's personal "error profile."
4. **Practice**: The system generates targeted drills and review sessions based on the user's specific, calculated weaknesses, prioritizing the items and patterns that need the most attention.

#### 2.2 MVP Feature Set

The MVP will only include the features necessary to execute the core user loop.

- **Text Ingestion**: A simple interface for pasting raw German text.
- **LLM-Powered Extraction**: Identification of vocabulary, phrases, and basic grammatical patterns from ingested text, outputting a structured JSON format.
- **Local Storage**: Persistence of all user data, including the knowledge graph and learning telemetry, in a local SQLite database. The schema will be "graph-shaped" using nodes and edges tables.
- **Personalized Review Deck**: A daily review queue driven by a simple mastery/weakness score that prioritizes items the user struggles with.
- **Targeted Drills**: Generation of two initial drill types: minimal-pair cloze deletions (e.g., *seit* vs. *für*) and collocation completion drills (e.g., *eine Entscheidung ___*).
- **Constrained Chat Coach**: A brief, targeted chat session designed to elicit the use of specific vocabulary and patterns from the user's review deck, followed by a "patch notes" summary of corrections.
- **Error Telemetry**: Systematic logging of all interaction outcomes (reviews, drills, chat attempts) into an `encounters` table to power the personalization engine.

#### 2.3 Deliberately Out of Scope (Post-MVP)

To maintain focus and ensure a rapid launch, the following features are explicitly deferred. They can be added in future iterations without requiring a rewrite of the core architecture.

| Feature                        | Reason for Deferral                                                                 |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Audio/ASR Pipelines            | Adds significant scope and dependencies (e.g., Whisper integration).               |
| Screenshot/PDF OCR             | OCR adds complexity and external dependencies; pasting text covers 90% of use cases. |
| Multi-Device Sync              | Introduces significant architectural complexity (cloud storage, encryption, auth). |
| Advanced Graph Visualization   | A "nice-to-have" feature that does not impact the core learning loop.              |
| Complex Roleplay/Gamification  | Hard to make feel natural; high LLM prompt complexity and state management.        |
| Beautiful Analytics Dashboards | UI polish that can be added after the core personalization logic is proven.        |

With the scope of the MVP clearly defined, we can now detail the technical architecture that will support this functionality.

---

### 3.0 System Architecture

The system architecture is designed for simplicity, privacy, and rapid development. It prioritizes a local-first approach that can be executed on a standard user machine (e.g., a Mac) without external dependencies or network calls, ensuring user data remains entirely private.

#### 3.1 Technology Stack

The technology stack is chosen for its maturity, ease of local setup, and robust tooling.

- **UI Frontend**: A simple local web application. React is recommended for the initial build due to its component-based architecture.
- **API Backend**: Python with the FastAPI framework, providing a modern, high-performance API layer.
- **Database**: SQLite, which is serverless, file-based, and perfectly suited for a local-first application. It will be used to implement the "graph-shaped" data model.
- **Local LLM Runtime**: Ollama, for its ergonomic and straightforward management of local LLM execution.
- **LLM Model(s)**: A two-model approach is specified.  
  A small, fast model (e.g., Llama 3 8B or Mistral 7B) will be used for high-frequency tasks like extraction and classification, while a larger, quality-focused model will be reserved for more nuanced tasks like explanation and generation. While a single-model approach was considered for simplicity, we are adopting the two-model strategy to enforce a clean separation of concerns: a smaller, faster model for high-frequency, low-latency tasks like extraction, and a larger model for high-quality, less frequent tasks like explanation. This provides a more scalable long-term architecture.

#### 3.2 Core Service Modules

The backend will be organized into distinct service modules, each with a clear responsibility.

- `ingest_service`: Handles the intake of raw text from the user, stores it, and triggers the extraction process.
- `extract_service`: Manages calls to the local LLM to extract linguistic items from text, validates the structured JSON output, and prepares it for storage.
- `graph_store`: Provides a dedicated interface for all CRUD (Create, Read, Update, Delete) operations on the SQLite database, abstracting the "graph" logic.
- `review_service`: Contains the logic for generating daily review decks and selecting appropriate drill types based on the user's calculated weakness profile.
- `coach_service`: Manages the constrained chat sessions, including target selection, conversation flow, and post-chat analysis and feedback.

This architecture directly supports the data model that forms the heart of the application.

---

### 4.0 Data Model & Storage

The application's strategic advantage lies in its data model. We will use a "graph-shaped database" implemented in SQLite. This approach captures the rich, interconnected nature of language without the operational overhead of a dedicated graph database, which is unnecessary for the MVP.

#### 4.1 Database Schema

The schema is designed to be minimal yet powerful, with a clear separation between linguistic items, their relationships, and the user's learning history.

- **`items` (Nodes)**: Stores the core learnable units.

| Column Name    | Data Type | Description                                                  |
| -------------- | --------- | ------------------------------------------------------------ |
| `id`           | INTEGER   | Primary Key                                                 |
| `type`         | TEXT      | Type of item (e.g., word, phrase, pattern).                 |
| `canonical_form` | TEXT    | The base or dictionary form of the item.                    |
| `metadata_json`  | TEXT    | A JSON blob for storing rich metadata (gender, plural, POS, CEFR guess, etc.). |

- **`edges`**: Stores the relationships between items.

| Column Name  | Data Type | Description                                                                   |
| ------------ | --------- | ----------------------------------------------------------------------------- |
| `id`         | INTEGER   | Primary Key                                                                   |
| `source_id`  | INTEGER   | Foreign Key to `items.id`.                                                   |
| `target_id`  | INTEGER   | Foreign Key to `items.id`.                                                   |
| `relation_type` | TEXT   | Type of relationship (e.g., `collocates_with`, `confusable_with`, `governs_case`). |

- **`encounters` (Events)**: The learning telemetry log, which is the most critical table for personalization.

| Column Name        | Data Type | Description                                                                                     |
| ------------------ | --------- | ----------------------------------------------------------------------------------------------- |
| `id`               | INTEGER   | Primary Key                                                                                     |
| `item_id`          | INTEGER   | Foreign Key to `items.id`. The item being practiced.                                           |
| `mode`             | TEXT      | The context of the interaction (e.g., `review`, `drill`, `chat`).                              |
| `correct`          | BOOLEAN   | The outcome of the interaction (True/False).                                                   |
| `prompt`           | TEXT      | The question or prompt presented to the user.                                                  |
| `actual_answer`    | TEXT      | The user's submitted answer.                                                                   |
| `expected_answer`  | TEXT      | The correct answer.                                                                            |
| `context_sentence` | TEXT      | The full sentence from which the item or drill was derived.                                    |
| `error_type`       | TEXT      | The classified error type from the taxonomy.                                                   |
| `confusion_target_id` | INTEGER | Foreign Key to `items.id`. If a confusable error, points to the confused item.                 |
| `response_time_ms` | INTEGER   | The time in milliseconds taken to respond; a proxy for hesitation.                             |
| `timestamp`        | DATETIME  | The timestamp of the event.                                                                    |

- **`error_tags`**: A simple lookup table for the error taxonomy.

| Column Name | Data Type | Description                                            |
| ----------- | --------- | ------------------------------------------------------ |
| `id`        | INTEGER   | Primary Key                                           |
| `name`      | TEXT      | The unique name of the error tag (e.g., `GENDER`, `CASE`). |

#### 4.2 Error Taxonomy

A minimal, high-value error taxonomy for German is essential for effective personalization. All incorrect user answers will be classified by the LLM into one of these categories.

- **GENDER**
  - `der_die`: Masculine/feminine confusion.
  - `der_das`: Masculine/neuter confusion.
  - `die_das`: Feminine/neuter confusion.

- **CASE**
  - `nom_akk`: Nominative/Accusative confusion.
  - `akk_dat`: Accusative/Dative confusion.
  - `dat_gen`: Dative/Genitive confusion.

- **PREP_CASE**
  - Incorrect case following a specific preposition (e.g., *wegen + Dativ* instead of *Genitiv*).

- **WORD_ORDER**
  - `verb_final`: Failure to place the verb at the end of a subordinate clause.
  - `inversion`: Failure to invert subject/verb after a fronted element.

- **VERB_FORM**
  - `conjugation`: Incorrect verb ending for person/number.
  - `participle`: Incorrect past participle form.
  - `auxiliary`: Confusion between *haben* and *sein* in *Perfekt* tense.
  - `tense`: Incorrect tense selected for the context.

- **ADJECTIVE_ENDING**
  - Incorrect adjective declension.

- **COLLOCATION**
  - Unnatural word combination (e.g., *Entscheidung machen* vs. *treffen*).

- **CONFUSABLE**
  - Semantic confusion between similar words (e.g., *kennen* vs. *wissen*).

- **LEXICAL**
  - A generally incorrect word choice not covered by other categories.

This structured data model is the foundation upon which the personalization engine operates.

---

### 5.0 Personalization Engine

The personalization engine is the application's key differentiator. Its function is an adaptive loop: Practice → Measure → Diagnose → Retarget. This is achieved through disciplined event logging and a straightforward scoring model, not complex machine learning algorithms, ensuring the engine remains fast, transparent, and effective.

#### 5.1 Learning Telemetry Layer

The engine is fueled by data. Every significant user interaction generates a structured event that is logged in the `encounters` table. The critical MVP events to capture are:

- **EXTRACT_SEEN**: An item has been identified in a user's text for the first time.
- **REVIEW_RESULT**: The user marked a review item as correct or incorrect.
- **DRILL_RESULT**: The outcome of a specific, targeted drill (e.g., a cloze test).
- **CHAT_FEEDBACK**: The outcome of an attempt to use a target word in the coached chat (e.g., used correctly, used incorrectly with a specific error type).

#### 5.2 Mastery & Weakness Scoring

A simple, weighted formula calculates a "weakness score" for each item in the user's knowledge graph. This score determines its priority for practice. The formula combines recency, error frequency, and relationship penalties.

$$
\text{Weakness(Item)} =
(w_{\text{wrong}} \times \text{wrong\_count\_recent})
+ (w_{\text{confusable}} \times \text{confusable\_penalty})
+ (w_{\text{decay}} \times \text{time\_since\_last\_success})
- (w_{\text{correct}} \times \text{correct\_streak})
$$

Where:

- `wrong_count_recent`: A weighted count of recent incorrect encounters.
- `confusable_penalty`: A penalty applied if the item is frequently confused with another.
- `time_since_last_success`: A decay factor that increases an item's score as more time passes since it was last answered correctly.
- `correct_streak`: A bonus that reduces an item's score when it is answered correctly multiple times in a row.

#### 5.3 Adaptive Product Behavior

The calculated weakness scores and error profile directly and automatically alter the application's behavior for each user.

##### 5.3.1 Personalized Deck Composition

The daily review deck is not a random selection. Its composition is algorithmically determined to maximize learning efficiency:

- 60% of the deck is composed of the user's weakest items, as determined by the highest weakness scores.
- 20% is dedicated to known confusables that the user frequently mixes up.
- 20% focuses on practicing patterns tied to the user's top three error types (e.g., word order patterns if `WORD_ORDER` is a common error).

##### 5.3.2 Adaptive Drill Selection

The system adapts the type of drill generated based on the user's "error fingerprint"—the aggregate counts of their logged `error_tags`.

- High `CONFUSABLE` errors trigger minimal-pair multiple-choice drills (e.g., "Choose *seit* or *für*").
- High `WORD_ORDER` errors trigger sentence reordering drills.
- High `GENDER` errors trigger article-only prompts (e.g., "Fill in the blank: ___ Entscheidung").
- High `COLLOCATION` errors trigger "choose the correct verb" drills (e.g., "Which verb goes with *Entscheidung*? *treffen* or *machen*?").

This direct mapping will be used for the MVP. Post-MVP iterations will incorporate a more sophisticated selection algorithm that also considers session success rate, switching to confidence-building drills (e.g., recognition of known items) if the user's error rate becomes too high.

This adaptive logic is powered by carefully structured interactions with the local Large Language Model.

---

### 6.0 LLM Integration & Contracts

Our strategy for LLM integration is to treat the model as a powerful but constrained tool for specific linguistic tasks. It is not a general-purpose conversationalist. All interactions with the LLM must be through well-defined "contracts" that require strict, validated JSON outputs. This approach is critical for ensuring system reliability and preventing unpredictable behavior.

#### 6.1 LLM Task #1: Extraction

This contract defines the pipeline for extracting learnable items from raw text.

- **Inputs**: A block of raw German text.
- **Output (JSON)**: A structured JSON object containing lists of sentences, extracted items, and their relationships.

```json
{
  "sentences": [
    {
      "idx": 0,
      "text": "Ich muss heute eine Entscheidung treffen."
    }
  ],
  "items": [
    {
      "type": "chunk",
      "canonical": "eine Entscheidung treffen",
      "english_gloss": "to make a decision (idiomatic)",
      "pos_hint": "PHRASE",
      "meta": {
        "gender": "die",
        "cefr_guess": "B1"
      },
      "why_worth_learning": "common collocation; replaces non-native *Entscheidung machen*",
      "evidence": {
        "sentence_idx": 0,
        "sentence": "Ich muss heute eine Entscheidung treffen.",
        "left_context": "",
        "right_context": ""
      }
    }
  ],
  "edges": [
    {
      "src_canonical": "eine Entscheidung treffen",
      "dst_canonical": "sich entscheiden für",
      "type": "near_synonym",
      "weight": 0.6,
      "note": "related decision expression"
    }
  ]
}
```

#### 6.2 LLM Task #2: Error Classification

This contract defines the "Judge" prompt used to classify a user's mistake.

- **Inputs**: The user's incorrect sentence, the correct version, and the surrounding context.
- **Output (JSON)**: A JSON object that conforms to the Error Taxonomy (Section 4.2).

```json
{
  "error_type": "gender",
  "error_subtype": "der_die",
  "confusion_target": null,
  "explanation": "The noun 'Entscheidung' is feminine, so it requires the article 'die', not 'der'."
}
```

#### 6.3 LLM Task #3: Drill Generation

This contract defines how personalized drills are created on-demand.

- **Inputs**: The target item to be drilled, the user's top `error_types`, and one or more context sentences.
- **Output (JSON)**: A list of one or more drill objects.

```json
{
  "drills": [
    {
      "type": "cloze",
      "prompt": "Ich muss heute eine ____ treffen.",
      "answer": "Entscheidung",
      "choices": null
    },
    {
      "type": "mcq",
      "prompt": "Ich wohne ___ zwei Jahren in Zürich.",
      "answer": "seit",
      "choices": [
        "seit",
        "für",
        "ab"
      ]
    }
  ]
}
```

#### 6.4 LLM Task #4: Explanation ("Why is this like that?")

This contract powers the on-demand explanation feature.

- **Inputs**: A specific German sentence and an optional user question (e.g., "Why dative here?").
- **Output (JSON)**: A JSON object containing a concise, structured explanation.

```json
{
  "explanation_one_liner": "Because 'warten auf' is a fixed verb-preposition pair that always governs the accusative case.",
  "pattern_name": "Verb + preposition governs case",
  "pattern_template": "warten auf + Akk",
  "examples": [
    "Ich warte auf den Bus.",
    "Wir warten auf eine Antwort."
  ],
  "common_mistake": "Using dative after 'auf' in this fixed verb-prep phrase is a common error."
}
```

A phased implementation plan is necessary to build these interconnected systems in a manageable and stable way.

---

### 7.0 Phased Implementation Plan

The project will be developed in small, high-value, iterative cycles. This ensures the core loop is functional and stable at each stage before adding further complexity, minimizing risk and allowing for continuous testing.

#### 7.1 Iteration 1: Core Loop & Basic Telemetry

This initial phase focuses on building the foundational data pipeline and a minimal user interface. The goal is a functional, end-to-end loop.

1. **Repo & Stack Setup**: Initialize the monorepo with separate directories for the FastAPI backend and React frontend. Create local run scripts (`make dev`) to start both services and verify the Ollama runtime is available.
2. **Database & Schema**: Implement the full SQLite schema as defined in Section 4.1 using a migration tool like Alembic. Create initial CRUD functions in the `graph_store` service.
3. **Ingest & Extract Pipeline**: Build the `POST /sources` endpoint and the `extract_service`. This service will call the local LLM with the extraction prompt, validate the JSON response, and write the resulting items and edges to the database.
4. **Basic Review Deck**: Implement the `GET /review/today` endpoint. For this iteration, prioritization can be simple (e.g., least recently seen items).
5. **Record Results**: Build the `POST /review/result` endpoint. This will write basic `review_correct` or `review_wrong` signals to the `encounters` table.
6. **Minimal UI**: Create the three essential screens: a page with a text area to paste text and trigger extraction, a "Today's Deck" view to display and answer review cards, and a placeholder screen for the Coach Chat.

#### 7.2 Iteration 2: Personalization & Error-Awareness

This phase activates the personalization engine, making the application adaptive.

1. **Implement Error Taxonomy**: Populate the `error_tags` lookup table and add the necessary logic to the `graph_store` to handle error classification data.
2. **Activate Error Classification**: Integrate the error classification LLM call. When a user submits an incorrect answer during a review, the `review_service` will call the LLM to get an `error_type` and log it to the `encounters` table.
3. **Implement Weakness Scoring**: Write the business logic to calculate the weakness score for each item based on the formula in Section 5.2, using data from the `encounters` table.
4. **Upgrade Deck Composition**: Refactor the `review_service` to use the calculated weakness score and error profile for personalized deck building, following the 60/20/20 composition rule from Section 5.3.1.
5. **Introduce Adaptive Drills**: Implement the logic in the `review_service` to select a drill type based on the user's aggregate error profile, as defined in Section 5.3.2.
6. **Simple Profile UI**: Add a basic UI component or page that displays the user's "Top 3 weak areas" or a simple list of their "error fingerprint" by querying the aggregated `encounters` data.

---

This specification provides a complete roadmap for the MVP. By following this plan, we will develop a highly differentiated and effective language learning tool that delivers on the vision of a true personal language operating system.