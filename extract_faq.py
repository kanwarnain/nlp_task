from pathlib import Path

from bs4 import BeautifulSoup


def extract_faq_content(html_file_path):
  """
  Extract FAQ title and content from Shell support HTML files
  """
  with open(html_file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

  soup = BeautifulSoup(html_content, "html.parser")

  # Extract title
  title_element = soup.find("h1", class_="article-title")
  title = title_element.get_text().strip() if title_element else "No title found"

  # Extract main content
  content_element = soup.find("div", class_="article-body")

  if not content_element:
    return {"title": title, "content": "No content found"}

  # Convert content to clean text while preserving structure
  content_text = ""

  for element in content_element.descendants:
    if element.name is None:  # Text node
      text = str(element).strip()
      if text:
        content_text += text
    elif element.name == "p":
      content_text += "\n\n"
    elif element.name == "br":
      content_text += "\n"
    elif element.name == "li":
      content_text += "\n• "
    elif element.name == "a":
      href = element.get("href", "")
      link_text = element.get_text().strip()
      content_text += f"[{link_text}]({href})"
    elif element.name in ["strong", "b"]:
      content_text += "**"
    elif element.name in ["em", "i"]:
      content_text += "*"

  # Clean up extra whitespace and newlines
  content_text = "\n".join(line.strip() for line in content_text.split("\n") if line.strip())

  return {"title": title, "content": content_text}


def extract_all_faqs(faq_directory):
  """
  Extract FAQs from all HTML files in the directory
  """
  faq_path = Path(faq_directory)
  faqs = []

  for html_file in faq_path.glob("*.html"):
    try:
      faq_data = extract_faq_content(html_file)
      faq_data["filename"] = html_file.name
      faqs.append(faq_data)
      print(f"✓ Processed: {html_file.name}")
    except Exception as e:
      print(f"✗ Error processing {html_file.name}: {e}")

  return faqs


# Usage examples:
if __name__ == "__main__":
  # Extract single FAQ
  single_faq = extract_faq_content(
    "shell-retail/faq/115002743932-How-can-I-find-the-opening-times-of-Shell-Service-Stations-.html"
  )
  print("Title:", single_faq["title"])
  print("Content:", single_faq["content"][:200] + "...")

  print("\n" + "=" * 50 + "\n")

  # Extract all FAQs
  all_faqs = extract_all_faqs("shell-retail/faq/")
  print(f"\nExtracted {len(all_faqs)} FAQs total")

  # Show first few FAQs
  for i, faq in enumerate(all_faqs[:3]):
    print(f"\n--- FAQ {i + 1} ---")
    print(f"File: {faq['filename']}")
    print(f"Title: {faq['title']}")
    print(f"Content: {faq['content'][:150]}...")
