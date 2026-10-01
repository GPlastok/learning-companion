---
name: unslop
description: >-
  Cut AI tells from the prose in technical documents in any repo: plans, specs, refinement notes, build logs, decision records, READMEs, CLAUDE.md and other docs. Run it before handing over any document, when another skill asks for it, or when the user types /unslop. Edits prose only: code, paths, commands, IDs, checkboxes and any format another tool reads stay exactly as they are. Not for code, commit messages or text an app shows its users.
---

# Unslop

Edit the prose in a document so it reads as written by a person who knows the code: plain,
specific and short. The reader is whoever picks the work up next, often in a fresh session
with no memory of this one. Every sentence should tell them something they need to know or
do.

## Scope

**Documents.** Plans, specs, refinement or research notes, reports, build logs, decision
records, `README*`, `CLAUDE.md`, `AGENTS.md` and other docs written to be read by the
people (or agents) working on the project.

**Not code.** Source, tests, code comments, commit messages and text the app shows to its
users are out of scope. They follow the code's own conventions.

**Logs, lightly.** In a log of commands and their output, fix the prose around the entries,
but never reword a command or a quoted result.

## What never changes

Documents are often read by other skills, scripts or people who search them, so their
structure is part of their meaning. Before editing, read the document whole and work out
which parts are structure. If a skill or guidance file defines the document's format (look
for the skill that wrote it, or the project's `CLAUDE.md`/`AGENTS.md`), read that too.

Leave these exactly as they are:

- Code identifiers, file paths, commands, test names, and anything in backticks or code
  blocks.
- IDs and cross-references, such as numbered criteria, decisions or questions (`AC3`,
  `D2`, `Q1`), step references, ticket numbers and links.
- Checkboxes and their ticked state.
- Section headings and their order when a template or another skill sets them.
- Fixed line formats a template defines, for example `D1. (Q1) <question>: <answer>.
  Source: <who>, <date>.` A colon or bold lead-in that is part of such a format isn't a
  tell (patterns 14 and 16 don't apply).
- Text quoted or supplied from elsewhere, such as a ticket's acceptance criteria or a
  user's wording. It is someone else's words, kept verbatim on purpose.
- Dates, counts, measurements and quoted output.

If a protected line reads badly, leave it and mention it in your reply.

## Process

1. Read the whole document, and the format definition if there is one, so you know which
   parts are protected.
2. Scan the prose for the patterns below.
3. Rewrite. Keep the meaning, and keep the length or make it shorter.
4. Self-audit. Ask what still makes it read as machine-written, and fix that.
5. Compare the protected parts with the original. Every identifier, number, checkbox and
   quoted line should be unchanged.

## Voice

Removing patterns is half the job. The other half is writing the way an engineer leaves
notes for a teammate.

- **Be specific.** "`parseDate` returns `null` for an empty string" beats "handles edge
  cases". Name the file, the function, the number.
- **Don't add opinions where the document leaves a choice open.** Open questions, option
  lists and surveys are often neutral on purpose, so the reader decides. Don't add a
  recommendation or a judgement that leans one way. Keep opinions where the document
  already has them, such as a decision and its reason.
- **Vary rhythm.** Mix short sentences with longer ones, but never at the cost of clarity.
- **One idea per sentence** in instructions and steps. The reader works through them in
  order.
- **No enthusiasm.** These are working notes, not a pitch.

## Patterns to detect and fix

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Cut puffery, state what happened.
2. **Name-dropping.** Listing media outlets without context. Pick one, say what was said.
3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
4. **Promotional language.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use neutral descriptions.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.
6. **Formulaic challenges.** "Despite challenges... continues to thrive." Replace with specific facts.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. **"Not just X, but Y."** State the point directly instead.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes. Use a period, a comma, or parentheses instead. Parentheses are fine and often the right tool for a genuine aside, so use them rather than contorting a sentence to avoid one. En dashes stay in their real job (number and date ranges). The pattern to kill is the paired em dash used as the default aside, several times per page; that rhythm is the tell, not the character.
14. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Replace with straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
21. **Cutoff disclaimers.** "While specific details are limited..." Find sources or remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted.
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
25. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.
