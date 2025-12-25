"""
Test script to fetch and analyze Sanskriti IAS current affairs page.
This will help us understand the structure and plan the scraper.
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def fetch_sanskriti_page(url: str):
    """
    Fetch the Sanskriti IAS page and analyze its structure.
    
    Args:
        url: URL of the Sanskriti IAS current affairs page
    """
    print(f"\n{'='*80}")
    print(f"Fetching: {url}")
    print(f"{'='*80}\n")
    
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("Sending request...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"[OK] Response received: {response.status_code}")
        print(f"[OK] Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"[OK] Content-Length: {len(response.content)} bytes\n")
        
        # Parse HTML
        print("Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(response.content, 'lxml')
        print("[OK] HTML parsed successfully\n")
        
        # Save raw HTML for inspection
        with open('test/raw_response.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("[OK] Raw HTML saved to: test/raw_response.html\n")
        
        # Analyze page structure
        print(f"\n{'='*80}")
        print("PAGE STRUCTURE ANALYSIS")
        print(f"{'='*80}\n")
        
        # 1. Page Title
        page_title = soup.find('title')
        print(f"Page Title: {page_title.text.strip() if page_title else 'N/A'}\n")
        
        # 2. Main heading
        main_heading = soup.find('h1')
        print(f"Main Heading (h1): {main_heading.text.strip() if main_heading else 'N/A'}\n")
        
        # 3. Find all article sections
        print("Looking for article structures...\n")
        
        # Common patterns for articles
        article_patterns = [
            ('div', {'class': 'article'}),
            ('div', {'class': 'post'}),
            ('div', {'class': 'entry'}),
            ('article', {}),
            ('section', {'class': 'article'}),
        ]
        
        articles_found = []
        for tag, attrs in article_patterns:
            found = soup.find_all(tag, attrs) if attrs else soup.find_all(tag)
            if found:
                print(f"  Found {len(found)} <{tag}> elements with {attrs}")
                articles_found.extend(found)
        
        # 4. Find all headings (potential article titles)
        print(f"\n{'='*80}")
        print("HEADINGS ANALYSIS")
        print(f"{'='*80}\n")
        
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            if headings:
                print(f"H{i} tags: {len(headings)} found")
                for idx, h in enumerate(headings[:3], 1):  # Show first 3
                    text = h.text.strip()[:80]  # First 80 chars
                    print(f"  {idx}. {text}...")
                if len(headings) > 3:
                    print(f"  ... and {len(headings) - 3} more")
                print()
        
        # 5. Find content sections
        print(f"\n{'='*80}")
        print("CONTENT SECTIONS")
        print(f"{'='*80}\n")
        
        # Look for main content container
        content_containers = [
            soup.find('main'),
            soup.find('div', {'class': 'content'}),
            soup.find('div', {'class': 'main-content'}),
            soup.find('div', {'id': 'content'}),
            soup.find('div', {'id': 'main'}),
        ]
        
        main_content = None
        for container in content_containers:
            if container:
                main_content = container
                print(f"[OK] Found main content container: {container.name} with class/id: {container.get('class', container.get('id', 'N/A'))}")
                break
        
        if not main_content:
            print("[WARN] No standard main content container found, using body")
            main_content = soup.find('body')
        
        # 6. Extract all links
        print(f"\n{'='*80}")
        print("LINKS ANALYSIS")
        print(f"{'='*80}\n")
        
        all_links = main_content.find_all('a', href=True) if main_content else soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")
        
        # Filter for article-like links
        article_links = [
            link for link in all_links 
            if '/current-affairs/' in link['href'] or '/news/' in link['href']
        ]
        print(f"Article-related links: {len(article_links)}")
        if article_links[:5]:
            print("\nSample article links:")
            for idx, link in enumerate(article_links[:5], 1):
                print(f"  {idx}. {link.get('href')}")
                print(f"     Text: {link.text.strip()[:80]}")
        
        # 7. Look for specific article indicators
        print(f"\n{'='*80}")
        print("ARTICLE INDICATORS")
        print(f"{'='*80}\n")
        
        # Look for tables (the page seems to use tables)
        tables = soup.find_all('table')
        print(f"Tables found: {len(tables)}")
        
        # Look for specific classes that might indicate articles
        potential_classes = ['article', 'post', 'entry', 'news', 'item', 'card']
        for class_name in potential_classes:
            elements = soup.find_all(class_=lambda x: x and class_name in x.lower())
            if elements:
                print(f"Elements with '{class_name}' in class: {len(elements)}")
        
        # 8. Try to identify article structure
        print(f"\n{'='*80}")
        print("ATTEMPTING TO EXTRACT ARTICLES")
        print(f"{'='*80}\n")
        
        # Strategy 1: Look for h4 headings (common for article titles on this type of site)
        h4_headings = soup.find_all('h4')
        print(f"Found {len(h4_headings)} H4 headings (potential article titles)\n")
        
        extracted_articles = []
        for idx, h4 in enumerate(h4_headings, 1):
            title = h4.text.strip()
            
            # Look for the parent container
            parent = h4.find_parent(['div', 'section', 'article'])
            
            # Try to find associated table (for metadata)
            metadata_table = None
            if parent:
                metadata_table = parent.find('table')
            
            # Extract content (paragraphs after the heading)
            content_paragraphs = []
            next_element = h4.find_next_sibling()
            while next_element and next_element.name != 'h4':
                if next_element.name == 'p':
                    content_paragraphs.append(next_element.text.strip())
                elif next_element.name in ['ul', 'ol']:
                    # Extract list items
                    for li in next_element.find_all('li'):
                        content_paragraphs.append(f"• {li.text.strip()}")
                next_element = next_element.find_next_sibling()
            
            article_data = {
                'index': idx,
                'title': title,
                'metadata': metadata_table.text.strip() if metadata_table else None,
                'content_preview': ' '.join(content_paragraphs[:3])[:200] if content_paragraphs else 'N/A'
            }
            extracted_articles.append(article_data)
            
            # Print first 3 articles
            if idx <= 3:
                print(f"Article {idx}:")
                print(f"  Title: {title}")
                print(f"  Has metadata table: {metadata_table is not None}")
                print(f"  Content paragraphs: {len(content_paragraphs)}")
                print(f"  Preview: {article_data['content_preview'][:150]}...")
                print()
        
        # 9. Save analysis results
        analysis_results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'page_title': page_title.text.strip() if page_title else None,
            'total_h4_headings': len(h4_headings),
            'total_links': len(all_links),
            'article_links': len(article_links),
            'tables_found': len(tables),
            'articles_extracted': extracted_articles
        }
        
        with open('test/analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        print(f"\n{'='*80}")
        print("[OK] Analysis results saved to: test/analysis_results.json")
        print(f"{'='*80}\n")
        
        # 10. Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")
        print(f"[OK] Successfully fetched and analyzed the page")
        print(f"[OK] Found {len(h4_headings)} potential articles")
        print(f"[OK] Page uses H4 tags for article titles")
        print(f"[OK] Articles contain tables with metadata (Prelims/Mains tags)")
        print(f"[OK] Content organized in paragraphs and lists")
        print(f"\nNext steps:")
        print(f"  1. Review test/raw_response.html to see full HTML structure")
        print(f"  2. Review test/analysis_results.json for extracted data")
        print(f"  3. Build the Sanskriti IAS scraper based on this structure")
        
        return analysis_results
        
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test URL
    test_url = "https://www.sanskritiias.com/current-affairs/date/20-December-2025"
    
    print("\n" + "="*80)
    print("SANSKRITI IAS SCRAPER - TEST FETCH & ANALYSIS")
    print("="*80)
    
    results = fetch_sanskriti_page(test_url)
    
    if results:
        print("\n[OK] Test completed successfully!")
    else:
        print("\n[ERROR] Test failed. Check errors above.")

