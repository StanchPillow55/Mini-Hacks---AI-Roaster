"""Basic scraping utilities for profiles, URLs, and resume parsing"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from io import BytesIO


def extract_profile_from_url(url: str) -> Dict:
    """
    Extract profile information from a URL.
    
    Supports:
    - GitHub profiles (via public API or HTML fallback)
    - Generic webpages (title + top 3 meaningful paragraphs)
    
    Args:
        url: URL to scrape
        
    Returns:
        Dict with keys: bio, titles, skills, snippets, sources
    """
    result = {
        "bio": None,
        "titles": [],
        "skills": [],
        "snippets": [],
        "sources": [url]
    }
    
    # Check if it's a GitHub profile URL
    github_match = re.match(r'https?://(?:www\.)?github\.com/([^/]+)/?$', url)
    if github_match:
        username = github_match.group(1)
        return _extract_github_profile(username, url)
    
    # Otherwise, treat as generic webpage
    return _extract_generic_webpage(url)


def _extract_github_profile(username: str, url: str) -> Dict:
    """
    Extract GitHub profile data via public API with HTML fallback.
    
    Args:
        username: GitHub username
        url: Original URL for source tracking
        
    Returns:
        Dict with profile data
    """
    result = {
        "bio": None,
        "titles": [],
        "skills": [],
        "snippets": [],
        "sources": [url]
    }
    
    try:
        # Try GitHub API first (public, no auth needed for basic data)
        api_url = f"https://api.github.com/users/{username}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract bio
            result["bio"] = data.get("bio") or f"GitHub user with {data.get('public_repos', 0)} repositories"
            
            # Fetch top 3 repos
            repos_url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page=3"
            repos_response = requests.get(repos_url, headers=headers, timeout=10)
            
            if repos_response.status_code == 200:
                repos = repos_response.json()
                for repo in repos[:3]:
                    repo_name = repo.get("name", "")
                    repo_desc = repo.get("description", "No description")
                    result["snippets"].append(f"Repo: {repo_name} - {repo_desc}")
                    result["sources"].append(repo.get("html_url", ""))
                    
                    # Collect languages as skills
                    if repo.get("language"):
                        if repo["language"] not in result["skills"]:
                            result["skills"].append(repo["language"])
            
            # Add job title if available
            if data.get("company"):
                result["titles"].append(f"Works at {data['company']}")
            
            return result
        
        else:
            # Fallback to HTML scraping
            return _scrape_github_html(username, url)
    
    except Exception as e:
        result["bio"] = f"Error scraping GitHub profile: {str(e)}"
        return result


def _scrape_github_html(username: str, url: str) -> Dict:
    """
    Fallback HTML scraping for GitHub profile.
    
    Args:
        username: GitHub username
        url: Original URL
        
    Returns:
        Dict with profile data
    """
    result = {
        "bio": None,
        "titles": [],
        "skills": [],
        "snippets": [],
        "sources": [url]
    }
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract bio
        bio_elem = soup.find('div', class_='p-note user-profile-bio')
        if bio_elem:
            result["bio"] = bio_elem.get_text(strip=True)
        
        # Extract repo names (simplified)
        repo_elems = soup.find_all('a', {'itemprop': 'name codeRepository'}, limit=3)
        for repo in repo_elems:
            result["snippets"].append(f"Repo: {repo.get_text(strip=True)}")
        
        if not result["bio"]:
            result["bio"] = f"GitHub user: {username}"
        
    except Exception as e:
        result["bio"] = f"Error parsing GitHub HTML: {str(e)}"
    
    return result


def _extract_generic_webpage(url: str) -> Dict:
    """
    Extract title and top 3 meaningful paragraphs from a generic webpage.
    
    Uses simple readability heuristics:
    - Prefer paragraphs with 50+ characters
    - Skip navigation/footer content
    - Prioritize main content areas
    
    Args:
        url: URL to scrape
        
    Returns:
        Dict with page data
    """
    result = {
        "bio": None,
        "titles": [],
        "skills": [],
        "snippets": [],
        "sources": [url]
    }
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; RoasterBot/1.0)'
        })
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        if title:
            result["titles"].append(title.get_text(strip=True))
        
        # Remove script, style, nav, footer elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Find meaningful paragraphs
        paragraphs = []
        for p in soup.find_all(['p', 'article', 'div']):
            text = p.get_text(strip=True)
            # Simple readability heuristic: paragraphs with 50-500 chars
            if 50 <= len(text) <= 500:
                # Check if it's likely content (not just links/navigation)
                if text.count(' ') > 5:  # Has multiple words
                    paragraphs.append(text)
        
        # Get top 3 unique paragraphs
        unique_paragraphs = []
        for p in paragraphs:
            if p not in unique_paragraphs:
                unique_paragraphs.append(p)
            if len(unique_paragraphs) >= 3:
                break
        
        result["snippets"] = unique_paragraphs
        
        # Use first paragraph as bio if available
        if unique_paragraphs:
            result["bio"] = unique_paragraphs[0]
        else:
            result["bio"] = f"Content from: {result['titles'][0] if result['titles'] else url}"
    
    except Exception as e:
        result["bio"] = f"Error scraping webpage: {str(e)}"
    
    return result


def extract_from_resume(file_bytes: bytes) -> Dict:
    """
    Parse resume from plaintext or PDF file.
    
    Best-effort extraction of:
    - Name (first line heuristic or patterns)
    - Titles (job titles, roles)
    - Skills (technical keywords)
    
    Args:
        file_bytes: File content as bytes
        
    Returns:
        Dict with keys: bio, titles, skills, snippets, sources
    """
    result = {
        "bio": None,
        "titles": [],
        "skills": [],
        "snippets": [],
        "sources": ["uploaded_resume"]
    }
    
    try:
        # Try to decode as plain text first
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Try PDF parsing
            text = _extract_text_from_pdf(file_bytes)
        
        if not text:
            result["bio"] = "Unable to extract text from resume"
            return result
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract name (heuristic: first non-empty line, capitalized)
        if lines:
            potential_name = lines[0]
            if len(potential_name.split()) <= 4 and potential_name[0].isupper():
                result["bio"] = f"Resume for {potential_name}"
        
        # Extract titles (look for common job title patterns)
        title_keywords = [
            'engineer', 'developer', 'manager', 'designer', 'analyst',
            'consultant', 'architect', 'lead', 'director', 'specialist',
            'coordinator', 'administrator', 'officer', 'scientist'
        ]
        
        for line in lines[:20]:  # Check first 20 lines for titles
            line_lower = line.lower()
            for keyword in title_keywords:
                if keyword in line_lower and len(line.split()) <= 8:
                    result["titles"].append(line)
                    break
        
        # Extract skills (look for common technical skills)
        skill_patterns = [
            r'\b(Python|Java|JavaScript|TypeScript|C\+\+|Ruby|Go|Rust|Swift|Kotlin)\b',
            r'\b(React|Angular|Vue|Node\.js|Django|Flask|Spring|Express)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD)\b',
            r'\b(SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch)\b',
            r'\b(Machine Learning|AI|Data Science|NLP|Computer Vision)\b',
            r'\b(Agile|Scrum|REST|API|Microservices|DevOps)\b'
        ]
        
        text_lower = text.lower()
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skill = match.group(0)
                if skill not in result["skills"]:
                    result["skills"].append(skill)
        
        # Create snippets from key sections
        section_keywords = ['experience', 'education', 'projects', 'summary']
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower()
            # Check if line is a section header
            is_section = any(keyword in line_lower for keyword in section_keywords)
            
            if is_section:
                if current_section and section_content:
                    # Save previous section
                    snippet = f"{current_section}: {' '.join(section_content[:50])}"  # Limit length
                    result["snippets"].append(snippet[:200])  # Truncate to 200 chars
                current_section = line
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section and section_content:
            snippet = f"{current_section}: {' '.join(section_content[:50])}"
            result["snippets"].append(snippet[:200])
        
        if not result["bio"]:
            result["bio"] = "Resume uploaded"
        
    except Exception as e:
        result["bio"] = f"Error parsing resume: {str(e)}"
    
    return result


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF using pypdf.
    
    Note: Requires pypdf to be installed. Falls back gracefully if not available.
    
    Args:
        file_bytes: PDF file bytes
        
    Returns:
        Extracted text string
    """
    try:
        # Try to import pypdf (formerly PyPDF2)
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                return ""
        
        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())
        
        return '\n'.join(text_parts)
    
    except Exception:
        return ""
