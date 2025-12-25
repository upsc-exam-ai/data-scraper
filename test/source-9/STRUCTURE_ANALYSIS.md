# Sanskriti IAS Scraper - Structure Analysis Report

**Date:** December 25, 2025  
**URL Analyzed:** https://www.sanskritiias.com/current-affairs/date/20-December-2025

## Summary

Successfully analyzed the Sanskriti IAS current affairs page structure. The page contains **5 articles** on the sample date, with a consistent and well-structured HTML format.

## Page Structure

### Overall Layout
- **Container:** `<div class="blog position-relative overflow-hidden shadow rounded mb-3">`
- **Content wrapper:** `<div class="content p-4">`
- Each page contains multiple article containers

### Article Components

Each article contains the following structured elements:

#### 1. Title & URL
- **HTML:** `<h4><a class="text-danger" href="...">`
- Links to individual article pages
- Example: "ISRO to Launch AST BlueBird-2 Satellite"

#### 2. Metadata Table (Prelims/Mains Tags)
- **HTML:** `<table class="table table-bordered">` with gray background (`#ecf0f1`)
- Contains exam relevance tags
- Format: `Prelims: (topics)` and `Mains: (GS papers + topics)`
- Example: `Prelims: (Space and Technology +CA)` | `Mains: (GS 2 - International Relations; GS 3 - Space Technology)`

#### 3. Sections (H2 Headers)
Common sections found:
- **Why in News?** - Initial context/trigger
- **Background and Context** - Historical/contextual info
- **About [Topic]** - Main content sections
- **Significance** - Importance and implications
- **Key Features** - Technical details
- **Challenges** - Issues and concerns
- **Way Forward** - Solutions and recommendations
- **FAQs** - Question & Answer pairs

#### 4. Content Types Within Sections
- **Paragraphs:** `<p>` tags with text
- **Lists:** `<ul>` or `<ol>` with `<li>` items (bullet points)
- **Subsections:** `<h3>` tags for sub-topics
- **Tables:** Data tables (not metadata tables)

#### 5. Images
- **HTML:** `<img class="img-fluid" src="https://www.sanskritiias.com/uploaded_files/images/..."/>`
- Usually wrapped in `<a>` tags
- One image per article (typically)
- High-quality relevant images

#### 6. FAQs (Optional)
- Section header: `<h2>FAQs</h2>`
- Questions: `<p><strong>Q1. Question text?</strong></p>`
- Answers: Following `<p>` tags with answer text
- Not all articles have FAQs (3 out of 5 in sample)

## Extraction Statistics

From the test extraction:
- **Total articles:** 5
- **Total sections:** 33 (avg 6-7 per article)
- **Total images:** 5 (1 per article)
- **Total FAQs:** 14 (varies: 0-5 per article)

## Data Structure for Scraper

```
Article {
  - index: int
  - title: string
  - url: string (full article URL)
  - metadata: string (combined prelims/mains)
  - prelims_tag: string
  - mains_tag: string
  - sections: [
      {
        title: string (H2 text),
        content: [
          {type: 'paragraph', content: string},
          {type: 'list', list_type: 'ul/ol', items: [string]},
          {type: 'subsection', title: string},
          {type: 'table', rows: [[string]]}
        ]
      }
    ]
  - images: [
      {
        src: string,
        alt: string,
        width: string,
        height: string,
        link: string (optional),
        title: string (optional)
      }
    ]
  - faqs: [
      {
        question: string,
        answer: string
      }
    ]
  - raw_text: string (full text for search/fallback)
}
```

## Key Findings

### What We Captured ✓
1. ✓ Article titles and individual URLs
2. ✓ Prelims/Mains examination metadata
3. ✓ All section headings (H2) and subsections (H3)
4. ✓ Paragraphs with full text content
5. ✓ Bulleted and numbered lists
6. ✓ Images with URLs and metadata
7. ✓ FAQ sections with Q&A pairs
8. ✓ Full raw text for each article
9. ✓ Structured content by type (paragraph/list/table/subsection)

### Date URL Pattern
- Format: `https://www.sanskritiias.com/current-affairs/date/DD-Month-YYYY`
- Example: `.../date/20-December-2025`
- Can iterate through dates to fetch historical data

## Next Steps

1. **Build Sanskriti IAS Source Class**
   - Inherit from `NewsSource` base class
   - Implement `fetch_articles()` method
   - Implement `parse_article()` method
   - Handle date iteration

2. **Content Processing**
   - Clean HTML formatting
   - Extract structured sections
   - Handle special characters
   - Preserve list formatting

3. **Testing**
   - Test with multiple dates
   - Verify data consistency
   - Handle edge cases (missing FAQs, different formats)

## Files Generated

- `test/raw_response.html` - Full HTML for manual inspection
- `test/analysis_results.json` - Basic structure analysis
- `test/detailed_extraction.json` - Complete structured extraction
- `test/test_sanskriti_fetch.py` - Basic fetch and analysis script
- `test/test_detailed_extraction.py` - Comprehensive extraction script
- `test/print_summary.py` - Summary display script

## Notes

- The page structure is consistent and well-formed
- Content is rich and detailed (suitable for UPSC preparation)
- Articles are self-contained with clear sections
- No pagination on daily pages (all articles loaded at once)
- Good semantic HTML structure makes parsing reliable

