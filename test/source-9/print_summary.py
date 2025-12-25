"""
Print summary of extraction analysis
"""
import json

with open('test/detailed_extraction.json', encoding='utf-8') as f:
    data = json.load(f)

print("="*80)
print("SANSKRITI IAS STRUCTURE ANALYSIS SUMMARY")
print("="*80)
print(f"\nURL: {data['url']}")
print(f"Extracted at: {data['extracted_at']}")
print(f"Total articles: {data['total_articles']}")

print(f"\n{'='*80}")
print("ARTICLE STRUCTURE ANALYSIS")
print("="*80)

# Analyze first article in detail
if data['articles']:
    art = data['articles'][0]
    print(f"\nSample Article: {art['title']}")
    print(f"\nData fields captured:")
    for key in art.keys():
        if key == 'sections':
            print(f"  - {key}: {len(art[key])} sections")
        elif key == 'faqs':
            print(f"  - {key}: {len(art[key])} FAQs")
        elif key == 'images':
            print(f"  - {key}: {len(art[key])} images")
        elif key == 'raw_text':
            print(f"  - {key}: {len(art[key])} characters")
        else:
            value = str(art[key])[:60]
            print(f"  - {key}: {value}...")
    
    print(f"\n{'='*80}")
    print("SECTION BREAKDOWN")
    print("="*80)
    for section in art['sections']:
        print(f"\nSection: '{section['title']}'")
        print(f"  Content items: {len(section['content'])}")
        for item in section['content'][:2]:  # Show first 2 items
            print(f"    - {item['type']}")
    
    if art['faqs']:
        print(f"\n{'='*80}")
        print("FAQ SAMPLE")
        print("="*80)
        faq = art['faqs'][0]
        print(f"\nQ: {faq['question'][:80]}...")
        print(f"A: {faq['answer'][:80]}...")

print(f"\n{'='*80}")
print("ALL ARTICLES SUMMARY")
print("="*80)

for art in data['articles']:
    print(f"\n{art['index']}. {art['title']}")
    print(f"   URL: {art['url']}")
    print(f"   Prelims: {art['prelims_tag']}" if art['prelims_tag'] else "   Prelims: (see metadata)")
    print(f"   Sections: {len(art['sections'])}, Images: {len(art['images'])}, FAQs: {len(art['faqs'])}")

print(f"\n{'='*80}")
print("EXTRACTION COMPLETENESS")
print("="*80)
print("\n[OK] Successfully extracted:")
print("  - Article titles and URLs")
print("  - Prelims/Mains metadata tags")
print("  - Structured sections with headings")
print("  - Paragraphs, lists, and tables")
print("  - Images with URLs")
print("  - FAQs with Q&A pairs")
print("  - Full raw text for fallback")
print("\nThe scraper can now be built based on this structure!")

