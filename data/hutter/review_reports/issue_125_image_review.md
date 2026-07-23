# Hutter Strong mapping image review — issue #125

Reviewed against the cropped Hutter page images under `data/hutter/verse_images/`.
The printed Hutter text is authoritative. The alternate GPT-5.5 OCR was used only
as a locator/cross-check and was rejected whenever it disagreed with the image.

## Coverage

| Checkpoint | Words | Mapped | Unresolved | Coverage |
| --- | ---: | ---: | ---: | ---: |
| Issue baseline | 107,954 | 101,014 | 6,940 | 93.57% |
| Before this image-review pass | 107,954 | 102,021 | 5,933 | 94.50% |
| After the first image-review pass | 107,921 | 102,185 | 5,736 | 94.69% |
| After extraction-gated follow-up | 107,906 | 102,240 | 5,666 | 94.75% |
| After repeated-form image review | 107,900 | 102,290 | 5,610 | 94.80% |
| After all four-occurrence forms | 107,900 | 102,315 | 5,585 | 94.82% |
| After first three-occurrence batches | 107,882 | 102,381 | 5,501 | 94.90% |
| After all three-occurrence forms and first doubletons | 107,851 | 102,498 | 5,353 | 95.04% |
| After expanded doubleton image review | 107,824 | 102,699 | 5,125 | 95.25% |
| After continued image-led doubleton review | 107,786 | 102,901 | 4,885 | 95.47% |
| After exhaustive remaining-doubleton review | 107,746 | 103,025 | 4,721 | 95.62% |
| After proper-name and singleton review | 107,710 | 103,161 | 4,549 | 95.78% |
| After continued singleton image review | 107,710 | 103,316 | 4,394 | 95.92% |
| After OCR-difference image review | 107,710 | 103,476 | 4,234 | 96.07% |
| After second OCR-difference image review | 107,710 | 103,618 | 4,092 | 96.20% |
| After regeneration-safety and clitic review | 107,710 | 103,619 | 4,091 | 96.20% |
| After exact pronominal-form review | 107,710 | 103,619 | 4,091 | 96.20% |
| After continued inflection image review | 107,710 | 103,676 | 4,034 | 96.25% |
| After suffix-form image review | 107,710 | 103,729 | 3,981 | 96.30% |

The word total changed because image-confirmed OCR repairs split or merged tokens
differently. Relative to the issue baseline, 2,959 fewer tokens are unresolved.
Titus, the last book below 90% during this pass, moved from 89.0% to 93.7%.

## Suffix-form image review

This pass tested remaining suffix-analysis candidates against the page crops
before assigning a lemma. It resolved 53 tokens across 17 books, reducing the
queue from 4,034 to 3,981 without changing the corpus text or word total.
Accepted forms include suffixed bodies, crowns, times, genealogy, order,
poverty, remembrance, lamps, ships, burdens, merchandise, adversaries, and
inflections of showing, pursuing, immersing, falling, serving, and destroying.

The review also exposed why mechanical suffix removal is unsafe. Acts 26:31
`בְּיֵינוֹתָם` is visibly Hutter's `בֵּינוֹתָם`, “among themselves,”
not “their wines”; the extracted extra yod now receives a verse-scoped H996
mapping. The body forms in Romans 1:24 and 1 Corinthians 6:15 map to
`גְּוִיָּה` (H1472), not the superficially similar `גּוֹי` (H1471).
Likewise, the assembly forms in Luke 13:10 and Matthew 13:54 are not
“testimonies.” Candidates whose extracted word was absent from the crop,
including apparent forms in Romans 9:28 and John 19:35, were rejected.

Caesarea in Matthew 16:13 now has the exact custom entry D0283. This keeps the
place name distinct from the existing custom entry for the title Caesar.
Every accepted lexical override is restricted to its reviewed verse.

## Continued inflection image review

This pass reviewed the strongest remaining independent-OCR and suffix-analysis
candidates against the Hutter crops. It resolved 57 previously unresolved
tokens across 18 books, reducing the queue from 4,091 to 4,034 without changing
the 107,710-word corpus total.

The accepted forms include image-confirmed inflections for watching, keeping,
stoning, serving, appointing, leaving, borrowing, governing, trembling,
working, puffing up, doubting, bearing, placing, knowing, and taking. Reviewed
suffixed nouns cover affliction, consolation, confidence, conduct, generosity,
possessions, storehouses, decrees, lack, lamps, and witnesses. Every lexical
override is restricted to its reviewed verse so an unusual Hutter spelling
cannot propagate to an unrelated context.

Three genuine New Testament terms now have custom entries: D0280 for Nicodemus,
D0281 for Tiberias, and D0282 for the Aramaic `טַלְיָא`, girl or maiden. These
are no longer forced toward superficially similar Old Testament lemmas.

The image for 2 Peter 1:19 also disproved the transcription `כּוֹכְבֵיכֶם`
(your stars). The page clearly prints `בִּלְבַבְכֶם`, in your hearts, which is
now restored and mapped to H3824 with only the printed ב preposition.

## Exact pronominal-form review

This correctness pass reviewed the recurring pointed forms for *to/for us*,
*to/for you*, *to/for her*, and *in/among them or you*. Representative crops
were checked directly, including Acts 1:2, 3:6, 4:17, 4:29, 5:8, 6:2,
16:12, and 22:19, plus Luke 4:34. The scans confirm the extracted forms and
their less common vowel-point variants.

Seven exact custom entries now cover `לָנוּ` (also the printed variants
`לָּנוּ` and `לְנוּ`), `לְךָ`, `לָךְ`, `לָהּ`, `בָּהֶם`,
`בָּם`, and `בָּךְ`. An explicit `mapping_forms` field records these
reviewed variants without weakening exact-token matching. Optional outer
conjunctions remain supported, but consonant-only or embedded matches are not.

The regeneration corrected 564 assignments. Coverage did not change because
all 564 tokens already carried a Strong value, but those values were often
semantically impossible: `לָנוּ` alone had been scattered over 51 unrelated
Strong IDs. The reviewed exact forms now have stable definitions, and the
`exact_custom_lemma` total increased from 1,589 to 2,153. The same image review
also removed two stale `<unk>` markers from 1 John 4:17, restoring the printed
`לָנוּ` and `אֲנַחְנוּ`.

## Regeneration-safety and clitic review

The Delitzsch #119 review added accurate custom definitions for short inflected
function words such as `לִי`, `לוֹ`, `בִּי`, `בָּהּ`, and `בוֹ`. A
plain regeneration initially treated those definitions as prefix-strippable
global lemmas. That could map `בְּלִי` through `לִי`, map `לוֹבָה` through
`בָּהּ`, and change more than a thousand unrelated assignments.

Custom definitions now declare their reuse scope. Reviewed clitics use an
`exact` scope that requires the complete pointed token, with only an optional
outer conjunction allowed. Delitzsch review entries default to
`instances_only`; globally reusable Hutter lexemes keep their existing global
behavior. The regenerated report records 1,589 `exact_custom_lemma` mappings
and no longer permits an embedded short form to outrank the full printed word.

This also replaces widespread semantically invalid legacy assignments: `לוֹ`
no longer maps to H7592 (ask), `לִי` no longer borrows unrelated positional
Strong numbers, and the pointed clitics `בִּי`, `בוֹ`, `בָּהּ`, and `בָּנוּ`
use their reviewed custom meanings. Corrected Delitzsch evidence also restores
H7121 for `קוֹרֵא`, H3899 for `לֶחֶם`, H4417 for `מֶּלַח`, and
H1167 for the reviewed `בַעַל` occurrences.

Seven collision-prone verses were checked directly against their page images.
The source now preserves `כִּי־הָלַכְנוּ` in 2 Corinthians 10:2,
`כְּמוֹ גַרְעִין` in Matthew 17:20, `הוּגְשׁוּ` in Matthew
19:13, `כְּמוֹ` in 1 Thessalonians 2:6, and the distinct son,
sleeping, and build forms in John 4:46, Matthew 28:13, and
1 Thessalonians 5:11. Titus 1:10 `וּבְחוֹ` remains unresolved after
the image disproved the earlier `וּבְנוֹ` transcription; no lexical assignment was
invented for the still-uncertain printed form.

## Second OCR-difference image review

This continuation reviewed another 144 singleton crops selected from independent
OCR disagreements. It made 132 source repairs where the page image and verse
context agreed, and added 10 lexical mappings for genuine printed forms. The
repairs span 23 books and include damaged forms of resurrection, belief,
justification, blessing, bodily members, drunkenness, crucifixion, choking,
seizing, and honoring.

The review deliberately retained genuine inflections instead of replacing them
with normalized OCR readings. Examples include `בְּדַעְתֵּנוּ`,
`בִּבְרָכַת`, `שִׁכְּרוּנוֹת`, `נֵתִיחִים`, `נִצְדָּקִים`,
`וַיִּתְפְּשֵׂהוּ`, `וַיִּתְחַנְּקוּ`, `וַיֵּצֵּלִיבוּ`, and
`וְיִכַבְּדוּם`; these now have image-supported mappings. Acts 17:13
`וַיַּרְהֲמוּ` remains unresolved because its precise lexical root is still
not sufficiently certain from print and context alone.

## Image-confirmed source corrections

- Acts: 1:11; 2:42; 3:16; 6:14; 7:5; 8:3,32; 9:40; 10:45; 12:23;
  13:50; 15:8; 16:19; 17:19; 20:15,19,33; 22:23; 26:19; 27:2,33.
- Luke: 3:1; 5:19; 7:45; 8:18; 10:40; 11:28; 21:25.
- 1 Corinthians: 1:18; 2:11,12; 7:30; 9:9; 10:4; 12:3; 14:28; 15:38,51.
- Revelation: 17:12.
- James: 2:8.
- Galatians: 3:20,24; 4:19; 6:13.
- Mark: 2:4; 5:12; 14:31,37.
- John: 6:64; 9:7; 10:35; 18:16; 19:15,16.
- Romans: 6:6,8; 8:30.
- 1 Timothy: 4:8,9.
- 2 Timothy: 2:15.
- Hebrews: 3:7.
- Ephesians: 1:19; 5:6,14.
- Matthew: 21:22; 22:13.
- 1 Peter: 1:8.
- Titus: 1:2,4,5,6; 3:9,10,12,13,14.

These repairs include repeated OCR confusions such as `אמד`/`אמר`, `עבד`/`עמד`,
`ישנ` representing several different printed words, and `אתנו` representing
`אחזנו`, `אתם`, `אותנו`, or a genuine `אתנו` depending on the image.

## Reviewed lexical decisions

- Preserved genuine Hutter forms of archaic `הוה` and mapped them to H1933;
  image-visible confusions with `הזה`, `היה`, or `הוא` were corrected instead.
- Mapped image-confirmed believing/faithful forms to H539, sleeping forms to
  H3462, `יסכן` to H5532, and genuine `אתנו` to H854.
- Reused H4970 for Hutter `מתיא` (Matthias) and the existing D0196 entry for
  Hutter's Greek-form spellings of Andrew.
- Added custom entries for names/titles without an accurate Hebrew Strong entry:
  D0210 Martha, D0211 Caesar, D0212 Artemas, and D0213 Nicopolis.

## Explicitly deferred examples

The following were left unresolved because the crop is incomplete, the print is
ambiguous, or the alternate OCR appears to normalize/hallucinate the expected
biblical wording: Acts 27:40;
Romans 1:27, 16:18-19; 2 Corinthians 11:16; Hebrews 12:3; James 3:4;
Galatians 5:21; Revelation 17:6; and Titus 2:5. Their generated queue entries
retain the explicit unsupported-mapping reason.

## Extraction-gated follow-up

The follow-up review validates the printed token before lexical assignment. It:

- corrected all seven `כמ` queue items as bad splits or OCR substitutions;
- distinguished `בכתים` (Kittim/Macedonia) from `מפתים` (bread fragments);
- added verse-scoped overrides for homographs such as `אחר`, `דינו`, and `ענה`;
- corrected false `דינו` readings in Revelation 3:7 and Romans 2:5;
- corrected the Greek burial-cloth loanword `האטון` in John 20:5-7;
- validated Hutter `איזה`, `בעלילות`, and `אמיר` against every affected image;
- mapped the printed numeral abbreviation `י״ב` without treating it as damaged OCR.

## Repeated-form image review

The next pass reviewed every image behind selected forms occurring four times.
It corrected false repetition before assigning a lexeme:

- `ויבהלו`: three printed forms map to H927; Luke 24:5 instead prints `ובהיותן`.
- `ויציעו`: the printed `הציעו`/`ויציעו` forms map to H3331, with incorrect
  conjunctions repaired in Luke 19:36 and Mark 11:8.
- `ונצרו`: only Jude 1:21 prints the H5341 form; 2 Peter 3:17 and Romans
  12:18 and 16:17 were repaired from their images.
- `לקרב`, `נטהרו`, `נשלחו`, and `תענו` were mapped to H7126, H2891, H7971,
  and H6030 after all occurrences were checked. False duplicates in Hebrews
  10:2 and Acts 19:29 were removed.
- `יכלה` maps to H3615 only where the image prints it; Luke 12:48 and
  1 Timothy 1:17 were corrected instead.
- `נאורה` and the one genuine possessive `של` receive reviewed corpus entries
  D0218 and D0219. Three other apparent `של` tokens were image-proven OCR errors.
- `שבע` maps to H7651 in the two genuine numeral contexts; Acts 3:20 and
  Matthew 21:33 were transcription errors rather than numeral occurrences.

The remaining four-occurrence clusters were also exhausted:

- `ונתר` separated into printed `ויתרון` (H3504) and `וינתן` (H5414).
- `יצר` was disambiguated by verse as H3335, H3336, or H5341; Luke 1:35 was
  an inserted transcription error rather than a fourth occurrence.
- all four `ישה` and `ישלו` items were corrected to their image-visible forms,
  including `ישוה`, `ישאף`, `יש־לו`, `ישלטו`, and `יושרו`.
- `נדים` remains genuine only in 2 Peter 3:16 (H5074); Colossians prints
  `זרים מנודים`, while 1 John twice prints parenthetical `עדים`.
- Matthew's three `עברה` forms map contextually to H5674. The visually distinct
  nautical term in Acts 27:28 remains unresolved instead of being conflated.

## Three-occurrence image review

The first 26 of 58 clusters occurring three times were reviewed across every
crop. The follow-up reviewed the remaining 32 clusters, so no unresolved form
now occurs three or more times. Highlights:

- corrected the earlier `ויבהלו` decision from Aramaic H927 to Hebrew H926;
  the same Hebrew root now maps the genuine `נבהלים` forms.
- mapped image-confirmed families for kissing (H5401), bringing (H935),
  receiving (H6901), healing (H7495), leading (H3212), gathering (H6950),
  breaking/defrauding (H1214), fruit-bearing (H6509), placing (H7760),
  working (H6466), and walking/conduct (H1980).
- all three apparent `לגלות` occurrences proved false: the images print
  `להיות`, `להליץ`, and `ולקוות` in their respective verses.
- repaired a copied wrong verse in 2 John 1:11 and another in John 12:18,
  removing false `קבלוהו`, `הבחירים`, and `יתמלא` tokens.
- split false merged forms such as `התירוהו` where Luke and Mark actually print
  `התירו אותו`; retained the genuine suffixed form in John 11:44.
- added D0220 for Hutter's image-confirmed noun `תלמוד`, teaching or doctrine,
  rather than forcing that post-biblical noun into an inexact Strong entry.

The final three-occurrence batch also:

- separated genuine `אחזנו`, `נבל`, `סגדו`, `ויסרו`, `עוולה`, `תחתו`, and
  `תועים` from image-proven OCR substitutions in the same normalized clusters;
- repaired repeated corruptions in John 16:16-19, Revelation 12:4,10 and 13:6,
  and the Macedonia passages in Acts 16:9-10;
- corrected false fragments such as `גוכל`, `ואיז`, `אסיפיל`, `זעוד`, `נת`,
  `דאת`, `הקק`, `חתתים`, `ירושת`, and `התוענות` to the words visible in print;
- mapped the image-confirmed helper, likeness, confession, worship, foolish,
  discipline, injustice, dismay, and wandering forms with verse-scoped evidence
  where a normalized spelling was ambiguous.

The first doubleton sheet then validated and mapped the printed forms for
holding, enemy, denarius, warning, reviving, foundations, trial, image, psalms,
and Bernice. Forms were added only after both source images were checked.

The expanded doubleton pass reviewed paired crops side by side and reduced the
doubleton queue from 345 to 250 clusters. It:

- repaired paired OCR substitutions including `אגי` → `אני`, `גידל` → `נולד`,
  `גלוף` → `גוף`, `דלגי` → `רגלי`, and `בכבורה` → `בגבורה`;
- restored damaged or duplicated wording in Acts 27:10, John 16:33,
  Romans 9:8 and 16:19, and 2 Corinthians 4:10, 5:11, and 12:7;
- added D0221 and D0222 for the two printed components of `אריוס פגוס`
  (Areopagus), and D0223 for Hutter's `אכאיה` (Achaia);
- mapped reviewed paired forms for prison, consolation, prayer, bodily members,
  seals, tongues, foundations, the divine name, warning, shame, and Achaia;
- corrected false paired readings before mapping genuine occurrences, including
  `בעשרה`, `במצוי`, `בקר`, `ודבר`, `וחם`, `ויסעדו`, and `וישכ`.

## Continued doubleton image review

The next paired-image pass reduced unresolved tokens from 5,125 to 4,885. It:

- corrected image-visible OCR substitutions in Matthew 14:23 and 15:31,
  John 8:28, 16:2, 16:4 and 19:19, Acts 4:31, 9:34 and 27:20, Mark 4:27,
  Romans 13:8, and 2 Timothy 3:8;
- rebuilt particularly damaged but legible clauses in John 8:44, Acts 27:23
  and 27:33, Mark 11:31 and 12:1, Romans 9:3 and 11:5-6, and Revelation
  11:10, 13:18 and 20:10 (stored under the existing source reference);
- separated genuine forms from identical normalized OCR errors for `הנן`,
  `ויתעה`, `וישלחוהו`, `ומומים`, `חבל`, `חרבה`, `חתונה`, `ירבש`, and `ירוה`;
- added image-supported corpus entries D0224-D0229 for `מקטרג`, Jannes,
  Jambres, Nereus, the post-biblical verb `תרגם`, and Lazarus;
- mapped additional image-confirmed families for blaspheming, imploring,
  defiling, inheritance, silence, translation, guarding, healing, tearing,
  planting, confessing, drinking, debt, purification, and authority.

## Exhaustive remaining-doubleton review

The continuation reviewed the remaining paired forms and reduced unresolved
tokens from 4,885 to 4,721. No unresolved normalized form now occurs three or
more times. It:

- corrected false duplicated readings across Acts, the Pauline letters,
  Hebrews, the Catholic letters, the Gospels, and Revelation before making any
  lexical assignment;
- rebuilt legible but badly damaged verses including Mark 6:33, John 14:21,
  Acts 27:12, 2 Corinthians 1:6, Titus 2:11-13, and Romans 11:18;
- separated genuine contextual forms from OCR homographs, including `נגלים`,
  `מרה`, `נילד`, `נהדר`, `נשכב`, `נשקה`, `נראי`, and `נצרו`;
- added D0230 and D0231 for the image-confirmed names Mattathias and Matthat;
- mapped reviewed forms for hoping, remembering, being born, sowing, closing,
  commanding, approaching, filling, becoming corrupt, justification, baskets,
  fine flour, trade, preservation, endings, and suffering;
- repaired recurring OCR confusions such as `נקטות` for `וקדרות`, `סוכל` for
  `נושא`, `סולת` for `הוללות`, and false `נתה` readings rather than assigning
  Strong numbers to transcription artifacts.

## Proper-name and singleton review

The next continuation reduced unresolved tokens from 4,721 to 4,549. It first
reviewed the remaining high-value paired forms, then moved into individually
image-confirmed singleton forms. It:

- reused existing corpus entries for Felix, Crete, Achaia, Onesimus, Iscariot,
  and Hutter's crucifixion and ship-boat vocabulary;
- added D0232-D0251 for genuine post-biblical vocabulary and New Testament
  entities including Spain, Iturea, Illyricum, Adramyttium, Aeneas, Agabus,
  Eunice, Elymas, Ananias, Epaphras, Aretas, Archelaus, and Arni;
- mapped reviewed inflections for working, occurring, hoping, believing,
  gathering, girding, loving, holding, eating, writing, advising, making,
  swearing, reaping, weaving, and hearing;
- corrected paired transcription artifacts for Peter's name, the tax collectors,
  groups, bodily members, questions, works, suffering, and several damaged
  clauses rather than preserving the accidental OCR spelling as a lexeme;
- retained isolated forms as unresolved whenever the crop or verse context did
  not support one unambiguous lexical assignment.

## Continued singleton image review

The next image-led singleton pass reduced unresolved tokens from 4,549 to
4,394. It:

- added D0252-D0264 for image-confirmed post-biblical vocabulary and proper
  names, including decency, confusion, Miletus, Samothrace, Cenchreae,
  Hymenaeus, the Adriatic Sea, and Hutter's forms for goddess and magi;
- mapped visually confirmed prefixed and inflected forms for remembering,
  sowing, gathering, walking, receiving, seeking, fleeing, returning, needing,
  honoring, loving, testing, healing, and calling;
- resolved reviewed nouns for decrees, foundations, garments, tongues, meals,
  covenants, assemblies, gifts, harps, souls, paths, trials, distress, and
  liability;
- reused established Strong entries for image-confirmed variants of Aeneas,
  Adramyttium, Macedonia, Perga, Gehenna, and other corpus vocabulary;
- left forms unresolved when the image or verse context did not establish a
  sufficiently unambiguous lexical identity.

## OCR-difference image review

This pass reduced unresolved tokens from 4,394 to 4,234 while leaving the word
count unchanged. It separately handled transcription faults and genuine lexical
forms:

- reviewed targeted crops where the primary transcription and independent OCR
  differed by one or two letters, accepting 98 corrections only when the page
  image and verse meaning agreed;
- repaired dropped, duplicated, or confused letters in forms for saints,
  adulterers, gathering, hiding, healing, remembering, inheritance, houses,
  vineyards, heaven, Patmos, Caiaphas, Barnabas, and the Galilean;
- corrected damaged clauses across Acts, the Gospels, Pauline letters,
  Hebrews, the Catholic letters, and Revelation rather than assigning Strong
  numbers to accidental OCR spellings;
- extended the existing D0243 mapping to all eight image-confirmed occurrences
  of `אודות`, meaning concerning or about;
- mapped reviewed repeated inflections for pursuing, exalting, authority,
  examining, imitating, knowing, leading, profiting, desiring, denying,
  completing, inheriting, separating, establishing, enduring, and being
  ashamed;
- used verse-scoped mappings where identical normalized forms had different
  senses, including friend versus shepherd and ability versus consumption.
