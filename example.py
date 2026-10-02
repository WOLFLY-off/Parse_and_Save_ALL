from parser import AutoParser

if __name__ == "__main__":
    # We specify the link for parsing.
    url = "https://example.com"
    
    print(f"Parsing the website: {url}...")
    parser = AutoParser(url)
    data = parser.parse_all()

    # Display the found data
    print(f"\n📧 Email found: {len(data['emails'])}")
    print(data['emails'])

    print(f"\n📞 Phones found: {len(data['phones'])}")
    print(data['phones'])

    print(f"\n🔗 Links found: {len(data['links'])}")
    print(f"\n🖼️ Images found: {len(data['images'])}")
