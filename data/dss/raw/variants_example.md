# DSS Variants - Example Format

This file demonstrates the expected format for DSS textual variants in Markdown.
Each section represents a book, and variants are listed as bullet points with
specific formatting.

## Isaiah Variants

**Isaiah 1:1** - MT: "כָּל־הָאָרֶץ" vs DSS: "כָל־הָאָרֶץ". Minor spelling change in DSS manuscript 1QIsaa.

**Isaiah 2:3** - MT: "וְהָלְכוּ עַמִּים רַבִּים" vs DSS: "וְהָלְכוּ גּוֹיִם רַבִּים". DSS uses "גּוֹיִם" instead of "עַמִּים" for nations.

**Isaiah 3:12** - MT: "וְנָשִׁים מָשְׁלוּ בוֹ" vs DSS: "וְנָשִׁים מָשְׁלוּ בָּם". DSS has plural "בָּם" instead of singular "בוֹ".

**Isaiah 7:14** - MT: "הִנֵּה הָעַלְמָה הָרָה" vs DSS: "הִנֵּה הָעַלְמָה הָרָה וְיֹלֶדֶת". DSS includes additional word "וְיֹלֶדֶת".

**Isaiah 40:3** - MT: "קוֹל קוֹרֵא" vs DSS: "קוֹל קוֹרֵא בַּמִּדְבָּר". DSS adds "בַּמִּדְבָּר" for "in the wilderness".

## 1 Samuel Variants

**1 Samuel 1:1** - MT: "וַיְהִי אִישׁ אֶחָד" vs DSS: "וַיְהִי אִישׁ". DSS omits "אֶחָד" (one).

**1 Samuel 1:24** - MT: "וַתַּעַל עִמּוֹ" vs DSS: "וַתַּעַל עִמָּהֶם". DSS has plural "עִמָּהֶם" instead of singular "עִמּוֹ".

**1 Samuel 2:25** - MT: "וְלֹא יִשְׁמְעוּ לְקוֹל אֲבִיהֶם" vs DSS: "וְלֹא יִשְׁמְעוּ לְקוֹל אֲבִיהֶם כִּי חָפֵץ יְהוָה לַהֲמִיתָם". DSS adds explanatory phrase.

**1 Samuel 10:1** - MT: "וַיִּקַּח שְׁמוּאֵל אֶת־פַּךְ הַשֶּׁמֶן" vs DSS: "וַיִּקַּח שְׁמוּאֵל פַּךְ הַשֶּׁמֶן". DSS omits definite article "אֶת־".

**1 Samuel 10:27** - MT: "בְּנֵי בְלִיַּעַל" vs DSS: "בְּנֵי הָרְשָׁעִים". DSS uses different term for "worthless men".

## 2 Samuel Variants

**2 Samuel 5:8** - MT: "וַיֹּאמֶר דָּוִד בַּיּוֹם הַהוּא" vs DSS: "וַיֹּאמֶר דָּוִד". DSS omits temporal phrase "בַּיּוֹם הַהוּא".

**2 Samuel 7:16** - MT: "וְהָיָה מְכוֹנָנֶת עַד־עוֹלָם" vs DSS: "וְהָיָה מְכוֹנָנָה עַד־עוֹלָם". DSS uses feminine form "מְכוֹנָנָה".

## Format Guidelines

### Variant Format
Each variant follows this pattern:
```
**Book Chapter:Verse** - MT: "masoretic_text" vs DSS: "dss_text". Description of the variant.
```

### Required Elements
- **Biblical Reference**: Must be in format `**Book Chapter:Verse**`
- **MT Text**: Masoretic Text in Hebrew with quotation marks
- **DSS Text**: DSS Text in Hebrew with quotation marks
- **Description**: Explanation of the textual difference

### Optional Elements
- Manuscript source (e.g., 1QIsaa, 4QSama)
- Significance level (high, medium, low)
- Variant type (addition, omission, substitution, etc.)

### Section Headers
- Use `## Book Name Variants` format for each book
- Book names should match standard abbreviations (Isaiah, 1_Samuel, etc.)

### Notes
- All Hebrew text must use proper Unicode characters
- Maintain consistent quotation marks (double quotes recommended)
- Keep descriptions concise but informative
- One variant per line
- Empty lines between variants for readability
