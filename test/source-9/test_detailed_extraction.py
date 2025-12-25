"""
Detailed extraction test for Sanskriti IAS current affairs page.
This script extracts ALL components of each article including:
- Title
- URL
- Metadata (Prelims/Mains tags)
- All H2 sections (Why in News, Background, etc.)
- Content (paragraphs, lists)
- Images
- FAQs
- Tables
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def extract_article_details(article_div):
    """
    Extract all details from a single article div.
    
    Args:
        article_div: BeautifulSoup element containing the article
        
    Returns:
        Dictionary with all article details
    """
    article_data = {}
    
    # 1. Extract Title and URL
    h4 = article_div.find('h4')
    if h4:
        title_link = h4.find('a', class_='text-danger')
        if title_link:
            article_data['title'] = title_link.text.strip()
            article_data['url'] = title_link.get('href', '')
        else:
            article_data['title'] = h4.text.strip()
            article_data['url'] = None
    
    # 2. Extract Metadata Table (Prelims/Mains tags)
    metadata_table = article_div.find('table', class_='table-bordered')
    if metadata_table:
        metadata_text = metadata_table.get_text(separator=' ', strip=True)
        article_data['metadata'] = metadata_text
        
        # Parse Prelims and Mains separately if possible
        prelims = None
        mains = None
        td = metadata_table.find('td')
        if td:
            text = td.get_text(separator='\n', strip=True)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                if line.startswith('Prelims:'):
                    prelims = line.replace('Prelims:', '').strip()
                elif line.startswith('Mains:') or line.startswith('Mains,'):
                    mains = line.replace('Mains:', '').replace('Mains,', '').strip()
        
        article_data['prelims_tag'] = prelims
        article_data['mains_tag'] = mains
    else:
        article_data['metadata'] = None
        article_data['prelims_tag'] = None
        article_data['mains_tag'] = None
    
    # 3. Extract all H2 sections (these are the main section headers)
    sections = []
    h2_tags = article_div.find_all('h2')
    
    for h2 in h2_tags:
        section_title = h2.get_text(strip=True)
        
        # Skip if it's FAQs (we'll handle that separately)
        if section_title.upper() == 'FAQS':
            continue
            
        section_content = []
        
        # Get all content until the next h2 or h3
        current = h2.find_next_sibling()
        while current and current.name not in ['h2', 'h4']:
            if current.name == 'p':
                text = current.get_text(strip=True)
                if text:
                    section_content.append({
                        'type': 'paragraph',
                        'content': text
                    })
            elif current.name in ['ul', 'ol']:
                items = []
                for li in current.find_all('li', recursive=False):
                    items.append(li.get_text(strip=True))
                if items:
                    section_content.append({
                        'type': 'list',
                        'list_type': current.name,
                        'items': items
                    })
            elif current.name == 'h3':
                # Sub-section header
                subsection_title = current.get_text(strip=True)
                section_content.append({
                    'type': 'subsection',
                    'title': subsection_title
                })
            elif current.name == 'table' and 'table-bordered' not in current.get('class', []):
                # Regular content table (not metadata table)
                # Extract table data
                rows = []
                for tr in current.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                if rows:
                    section_content.append({
                        'type': 'table',
                        'rows': rows
                    })
            
            current = current.find_next_sibling()
        
        if section_content:
            sections.append({
                'title': section_title,
                'content': section_content
            })
    
    article_data['sections'] = sections
    
    # 4. Extract Images
    images = []
    img_tags = article_div.find_all('img', class_='img-fluid')
    for img in img_tags:
        img_src = img.get('src', '')
        # Skip header/footer images
        if 'uploaded_files/images' in img_src:
            img_data = {
                'src': img_src,
                'alt': img.get('alt', ''),
                'width': img.get('width'),
                'height': img.get('height')
            }
            # Try to get the parent link if exists
            parent_link = img.find_parent('a')
            if parent_link:
                img_data['link'] = parent_link.get('href', '')
                img_data['title'] = parent_link.get('title', '')
            images.append(img_data)
    
    article_data['images'] = images
    
    # 5. Extract FAQs
    faqs = []
    faq_h2 = None
    for h2 in h2_tags:
        if h2.get_text(strip=True).upper() == 'FAQS':
            faq_h2 = h2
            break
    
    if faq_h2:
        current = faq_h2.find_next_sibling()
        current_question = None
        current_answer = []
        
        while current and current.name not in ['h2', 'h4']:
            if current.name == 'p':
                text = current.get_text(strip=True)
                # Check if it's a question (usually starts with Q1, Q2, etc. or has strong tag)
                strong = current.find('strong')
                if strong and ('Q' in strong.get_text()[:3] or 'Q.' in text[:5]):
                    # Save previous Q&A if exists
                    if current_question:
                        faqs.append({
                            'question': current_question,
                            'answer': ' '.join(current_answer)
                        })
                    current_question = text
                    current_answer = []
                else:
                    # It's an answer
                    if text:
                        current_answer.append(text)
            elif current.name in ['ul', 'ol']:
                # Answer might be in list format
                items = [li.get_text(strip=True) for li in current.find_all('li', recursive=False)]
                current_answer.extend(items)
            
            current = current.find_next_sibling()
        
        # Don't forget the last Q&A
        if current_question:
            faqs.append({
                'question': current_question,
                'answer': ' '.join(current_answer)
            })
    
    article_data['faqs'] = faqs
    
    # 6. Extract full raw text (for fallback/search)
    article_data['raw_text'] = article_div.get_text(separator='\n', strip=True)
    
    return article_data


def fetch_and_extract_all_articles(url: str):
    """
    Fetch the page and extract all articles with full details.
    
    Args:
        url: URL of the Sanskriti IAS current affairs page
        
    Returns:
        List of article dictionaries
    """
    print(f"\n{'='*80}")
    print(f"DETAILED EXTRACTION TEST")
    print(f"{'='*80}\n")
    print(f"Fetching: {url}\n")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"[OK] Response: {response.status_code}\n")
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all article divs
        # Structure: <div class="blog position-relative overflow-hidden shadow rounded mb-3">
        article_divs = soup.find_all('div', class_='blog')
        print(f"[OK] Found {len(article_divs)} article containers\n")
        
        articles = []
        for idx, article_div in enumerate(article_divs, 1):
            print(f"Extracting article {idx}...")
            article_data = extract_article_details(article_div)
            article_data['index'] = idx
            articles.append(article_data)
            
            # Print summary
            print(f"  Title: {article_data.get('title', 'N/A')}")
            print(f"  URL: {article_data.get('url', 'N/A')}")
            print(f"  Sections: {len(article_data.get('sections', []))}")
            print(f"  Images: {len(article_data.get('images', []))}")
            print(f"  FAQs: {len(article_data.get('faqs', []))}")
            print()
        
        # Save to JSON
        output_data = {
            'url': url,
            'extracted_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'articles': articles
        }
        
        with open('test/detailed_extraction.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"{'='*80}")
        print(f"[OK] Detailed extraction saved to: test/detailed_extraction.json")
        print(f"{'='*80}\n")
        
        # Print summary statistics
        print(f"SUMMARY:")
        print(f"  Total articles extracted: {len(articles)}")
        total_sections = sum(len(a.get('sections', [])) for a in articles)
        total_images = sum(len(a.get('images', [])) for a in articles)
        total_faqs = sum(len(a.get('faqs', [])) for a in articles)
        print(f"  Total sections: {total_sections}")
        print(f"  Total images: {total_images}")
        print(f"  Total FAQs: {total_faqs}")
        
        return articles
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_url = "https://www.sanskritiias.com/current-affairs/date/20-December-2025"
    results = fetch_and_extract_all_articles(test_url)
    
    if results:
        print("\n[OK] Detailed extraction completed successfully!")
        print("\nYou can now review:")
        print("  1. test/detailed_extraction.json - Full structured data")
        print("  2. Each article has: title, URL, metadata, sections, images, FAQs")
    else:
        print("\n[ERROR] Extraction failed!")

