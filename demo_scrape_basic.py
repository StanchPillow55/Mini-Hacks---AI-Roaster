#!/usr/bin/env python3
"""Demo script for scrape_basic module"""

import sys
import json
from src.scrape_basic import extract_profile_from_url, extract_from_resume

def demo_github():
    """Demo GitHub profile scraping"""
    print("=" * 60)
    print("DEMO: GitHub Profile Scraping")
    print("=" * 60)
    
    url = "https://github.com/torvalds"
    print(f"\nScraping: {url}\n")
    
    result = extract_profile_from_url(url)
    print(json.dumps(result, indent=2))

def demo_generic_webpage():
    """Demo generic webpage scraping"""
    print("\n" + "=" * 60)
    print("DEMO: Generic Webpage Scraping")
    print("=" * 60)
    
    url = "https://example.com"
    print(f"\nScraping: {url}\n")
    
    result = extract_profile_from_url(url)
    print(json.dumps(result, indent=2))

def demo_resume():
    """Demo resume parsing"""
    print("\n" + "=" * 60)
    print("DEMO: Resume Parsing (Mock Text)")
    print("=" * 60)
    
    mock_resume = """
John Doe
Senior Software Engineer

EXPERIENCE
Software Engineer at Tech Corp
- Built scalable systems using Python and AWS
- Led team of 5 engineers

SKILLS
Python, JavaScript, React, Docker, Kubernetes, AWS, PostgreSQL

EDUCATION
BS Computer Science
""".encode('utf-8')
    
    print("\nParsing mock resume...\n")
    result = extract_from_resume(mock_resume)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "github":
            demo_github()
        elif sys.argv[1] == "webpage":
            demo_generic_webpage()
        elif sys.argv[1] == "resume":
            demo_resume()
        else:
            print("Usage: python demo_scrape_basic.py [github|webpage|resume]")
    else:
        # Run all demos
        demo_github()
        demo_generic_webpage()
        demo_resume()
