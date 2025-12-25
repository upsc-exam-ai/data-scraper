# Simplified Article JSON Schema

## Structure Overview

```json
{
  "title": "string",
  "source": "string",
  "metadata": {
    "prelims": "string",
    "mains": "string",
    "tags": ["array", "of", "strings"]
  },
  "content": [
    {
      "heading": "string",
      "subheading": "string or null",
      "content": "string (can contain \\n for newlines and • for bullets)"
    }
  ],
  "faqs": [
    {
      "question": "string",
      "answer": "string"
    }
  ],
  "images": [
    {
      "url": "string",
      "alt": "string",
      "caption": "string"
    }
  ],
  "extracted_at": "ISO datetime string"
}
```

## Key Simplifications

### ✅ **Flat Content Structure**
- No deep nesting
- Just: `heading` → optional `subheading` → `content` text
- Content is plain text with newlines (`\n`) and bullet points (`•`)

### ✅ **Simple Array**
- `content` is an array of section objects
- Each section is independent
- Subsections = same heading with different subheading

### ✅ **Text Formatting**
- Use `\n\n` for paragraph breaks
- Use `• ` for bullet points
- Use `\n` for line breaks within lists
- Keep it simple and readable

## Example Content Patterns

### 1. Simple Section (No Subheading)
```json
{
  "heading": "Why in News?",
  "subheading": null,
  "content": "The Indian Space Research Organisation (ISRO) will launch..."
}
```

### 2. Section with Bullet Points
```json
{
  "heading": "Key Features",
  "subheading": null,
  "content": "• First feature\n• Second feature\n• Third feature"
}
```

### 3. Section with Subheading
```json
{
  "heading": "Significance of the Mission",
  "subheading": "For India / ISRO",
  "content": "• Strengthens ISRO's credentials\n• Demonstrates operational maturity"
}
```

### 4. Multiple Subsections (Same Heading)
```json
{
  "heading": "Significance",
  "subheading": "For India",
  "content": "..."
},
{
  "heading": "Significance",
  "subheading": "For Global Connectivity",
  "content": "..."
}
```

### 5. Mixed Paragraphs and Lists
```json
{
  "heading": "Background",
  "subheading": null,
  "content": "First paragraph explaining context.\n\nSecond paragraph with more details.\n\nKey points:\n• Point one\n• Point two\n• Point three"
}
```

## Database Mapping

```sql
-- Table structure
ca_articles {
  id: uuid [pk]
  published_date: date [not null]     -- e.g., '2025-12-20'
  source_url: text [not null]         -- Individual article URL
  article: json [not null]            -- THIS JSON SCHEMA
  attachments: json                   -- {images: [...], pdfs: [...]}
  created_at: timestamp
}
```

## Query Examples

```sql
-- Get all articles from a source
SELECT * FROM ca_articles 
WHERE article->>'source' = 'Sanskriti IAS';

-- Search by title
SELECT * FROM ca_articles 
WHERE article->>'title' ILIKE '%ISRO%';

-- Filter by Prelims topic
SELECT * FROM ca_articles 
WHERE article->'metadata'->>'prelims' ILIKE '%Space Technology%';

-- Get articles with FAQs
SELECT id, article->>'title', jsonb_array_length((article->'faqs')::jsonb) as faq_count
FROM ca_articles 
WHERE jsonb_array_length((article->'faqs')::jsonb) > 0;

-- Search within content
SELECT * FROM ca_articles 
WHERE EXISTS (
  SELECT 1 FROM jsonb_array_elements(article->'content') as section
  WHERE section->>'content' ILIKE '%satellite%'
);

-- Get specific section headings
SELECT 
  article->>'title' as title,
  jsonb_array_elements(article->'content')->>'heading' as headings
FROM ca_articles 
LIMIT 5;
```

## Benefits

1. **Simple to Parse**: Flat structure, easy to iterate
2. **Flexible**: Works with or without subheadings
3. **Readable**: Content stored as plain text with simple formatting
4. **Query-Friendly**: Easy to search and filter with PostgreSQL JSON operators
5. **Source-Agnostic**: Works for any source (Sanskriti, Drishti, Vision IAS, etc.)

## Files

- `article_schema.json` - JSON Schema for validation
- `article_example.json` - Complete working example
- `SCHEMA_DOCUMENTATION.md` - Full documentation (to be updated)

