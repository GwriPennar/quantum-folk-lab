# EXP-008A source and rights audit

Audit date: 2026-07-19

Scope: source discovery, rights analysis, and transcription-route assessment only. No IrishMAN row,
source PDF, or third-party ABC transcription was downloaded into or copied into this repository.

This is a project risk assessment, not legal advice. Copyright conclusions are jurisdiction-specific.

## A1. IrishMAN

### Dataset identity and revision

- Dataset: **Irish Massive ABC Notation (IrishMAN)**
- Host/owner: Hugging Face, `sander-wood/irishman`
- Current revision inspected: `30902e69ca45266207f8466e0d04e4bc742c5604`
- Current dataset-card metadata label: `mit`
- Current tree inspected without checking out data rows: `README.md`, `train.json`,
  `validation.json`, `leadsheet_ids.json`, `variation_ids.json`, and MIDI/XML archives
- Card: https://huggingface.co/datasets/sander-wood/irishman/blob/main/README.md
- Revision: https://huggingface.co/datasets/sander-wood/irishman/commit/30902e69ca45266207f8466e0d04e4bc742c5604

### What the card establishes

The card says the 216,284 records were collected from `thesession.org` and `abcnotation.com`,
converted ABC → XML → ABC, and stripped of natural-language fields including titles and lyrics. It
also identifies a 34,211-record subset with human-added chord symbols. The card asserts that all
tunes are public domain.

The same current README also contains a materially narrower copyright disclaimer: research use only,
not for commercial purposes, a statement that the authors *believe* the data are public domain, and
a takedown invitation for composition owners. The Git history contains 48 README-affecting revisions
between the initial 2023 card and the inspected 2024 head. Commit
`178f92e2b860f4e9a5cad91a18d4a321c6cc6f49` (2023-04-14) added an explicit warning that, while most
tunes were freely shared, some might be copyright-protected and users must determine tune-level
status. Commit `30cc65b34def245e876b3ac3219a990f1e79089c` (2024-03-16) replaced that wording with
research-only/non-commercial language, a belief that all data were public domain, and takedown
wording. The current `30902e6` revision retains the disclaimer alongside the unequivocal public-domain
claim and top-level MIT label. That combination is internally inconsistent for unrestricted
redistribution.

### Provenance and rights findings

- Titles, composers, collection names, tune numbers, printed pages, and other natural-language
  provenance do not survive preprocessing in the released rows.
- Tune-by-tune rights provenance therefore does not survive preprocessing.
- The current card does not identify the author or licence of each upstream ABC transcription.
- Round-trip conversion and control-code annotation make the released ABC a transformed compilation,
  not a demonstrated independent transcription from a named historical score.
- Chord symbols and editorial/conversion changes are present in at least a documented subset.
- A row cannot generally be linked from the released data to an exact historical source, edition,
  tune number, or scan page.
- The MIT metadata label may govern the dataset card, code, or compilation. It does not establish an
  MIT licence for every underlying melody, arrangement, chord annotation, or upstream ABC text.
- The public-domain assertion is unsupported tune-by-tune and is qualified by the current
  research-only/non-commercial disclaimer and takedown wording.
- Upstream attribution, database-right, source-site, and individual transcription obligations cannot
  be reconstructed reliably after provenance fields were removed.

### IrishMAN classification

**DISCOVERY/REFERENCE ONLY**

IrishMAN is not an authoritative redistribution source for EXP-008A. No row may be copied into the
fixture. At most it can alert a researcher that a melody representation may exist; identity, family,
historical source, and rights must then be established independently.

## A2. Historical printed source

### Edition identity

- Full title: *O'Neill's Music of Ireland: Eighteen Hundred and Fifty Melodies. Airs, Jigs,
  Reels, Hornpipes, Long Dances, Marches, Etc., Many of Which Are Now Published for the First Time*
- Collector/editor: Captain Francis O'Neill (1848–1936)
- Arranger: James O'Neill (1862–1949)
- Publisher: Lyon & Healy
- Place/year: Chicago, 1903
- Edition route: original 1903 edition, not a modern rearrangement
- Notation: a single treble melody line for unspecified melody instrument

Authoritative/primary records inspected:

- IMSLP work record and scan record:
  https://imslp.org/wiki/Music_of_Ireland_%28O%27Neill%2C_Francis%29
- National Library of Ireland catalogue record:
  https://catalogue.nli.ie/Record/vtls000144847
- Notre Dame catalogue record:
  https://marble.nd.edu/item/fe1b3100-51a2-41b3-8feb-1a5fd3abbf5a
- UK term guidance:
  https://www.gov.uk/copyright/how-long-copyright-lasts
- Francis O'Neill authority context:
  https://www.itma.ie/people/francis-oneill/

IMSLP identifies score item `#495828` as a 378-page complete score, scanned by an unknown scanner,
uploaded in 2017, with publisher information “Chicago: Lyon & Healy, 1903,” James O'Neill as arranger,
and a public-domain tag. The bibliographic title page and library records support the original-edition
identity. The scan PDF itself is not redistributed by this project.

### Rights rationale and limits

UK guidance gives the usual term for a musical work as life plus 70 years and for a published-edition
layout as 25 years from publication. Francis O'Neill died in 1936 and James O'Neill in 1949, so their
relevant UK terms expired no later than the end of 2019; the 1903 typographical-layout term expired
long before that. The book is therefore a defensible candidate source for an independent UK-oriented
transcription of a selected setting.

This does not prove every underlying tune anonymous or traditional. A tune-specific named composer,
later arrangement, or attribution can change the analysis and must be checked per setting. The
IMSLP-hosted modern “Crossing the Stream” arrangement by David Ian Rowlands is explicitly excluded.
The hosting site's scan metadata and download terms concern the scan copy; EXP-008A would encode only
facts and an independently read melody line, not redistribute the scan image or PDF.

Remaining uncertainty includes jurisdictional/transitional rules outside the UK, incomplete
tune-level authorship in the collection, and occasional ambiguity between collecting, arranging,
and source-performer contributions. These are manageable only through tune-by-tune review.

## A3. Existing O'Neill ABC projects

### John Chambers / trillian.mit.edu

- Index: https://trillian.mit.edu/~jc/music/book/ONeills/
- Revision notes: https://trillian.mit.edu/~jc/music/book/ONeills/Revision_Notes.html
- Search host context: https://abcnotation.com/searchCopyright

The site describes a 1996–1999 transcription project involving about 20 people and a 2020 reworking.
It documents condensed versions, transpositions for limited-range instruments, added layout/control
fields, modern `fine` substitutions, reclassification of settings, and alternative renderings. Named
transcribers can appear on individual files, but the inspected project pages do not provide an
explicit blanket licence or public-domain dedication for redistribution of the exact ABC text.
`abcnotation.com` is a search/index host and is not evidence that it owns or licenses indexed text.

Classification: **cross-check only**. Absence of a restriction is not a licence. No ABC text from
these projects may be copied. It may be used to flag a possible reading error after an independent
transcription from the 1903 score, with the cross-check recorded.

## A4. Audit conclusion

IrishMAN is unsuitable as a redistribution source but useful for discovery. The original 1903
O'Neill score is a candidate authoritative source for tune-by-tune independent transcription. Online
O'Neill ABC is cross-check-only unless a file-specific compatible licence is established. A project
ABC would be independently transcribed from the verified score and dedicated under CC0 where legally
possible, with tune-level authorship and source-page review still mandatory.

GO — HISTORICAL SOURCE AND TRANSCRIPTION ROUTE VERIFIED
