import re
from bs4 import BeautifulSoup

def fix_title_and_authors(text):
    # Replace the title with proper heading
    text = text.replace("# Learning in the machine: To share or not to share?  ", 
                        "# Learning in the Machine: To share or not to share?")
    
    # Format author information
    author_section = "Jordan Ott a,b, Erik Linstead a,∗, Nicholas LaHaye a, Pierre Baldi b  "
    formatted_authors = "**Jordan Ott**<sup>a,b</sup>, **Erik Linstead**<sup>a,∗</sup>, **Nicholas LaHaye**<sup>a</sup>, **Pierre Baldi**<sup>b</sup>"
    text = text.replace(author_section, formatted_authors + "\n\n")
    
    return text

def fix_affiliations(text):
    # Add affiliation information after authors
    affiliation_text = """
<sup>a</sup> Fowler School of Engineering, Chapman University, United States of America  
<sup>b</sup> Department of Computer Science, Bren School of Information and Computer Sciences, University of California, Irvine, United States of America  
<sup>∗</sup> Corresponding author
"""
    
    # Find position to insert (after author list, before article info)
    author_pattern = r"\*\*Jordan Ott\*\*<sup>a,b</sup>.+?Pierre Baldi\*\*<sup>b</sup>\n\n"
    match = re.search(author_pattern, text)
    
    if match:
        end_pos = match.end()
        text = text[:end_pos] + affiliation_text + "\n\n" + text[end_pos:]
    
    return text

def fix_article_info(text):
    # Find and replace the article info section
    article_info_pattern = r"a r t i c l e i n f o\s+Article history:[\s\S]+?Available online 25 March 2020"
    replacement = """## Article Information

**Article history:**  
Received 24 April 2019  
Received in revised form 15 March 2020  
Accepted 16 March 2020  
Available online 25 March 2020"""
    
    return re.sub(article_info_pattern, replacement, text)

def fix_keywords(text):
    # Find and replace the keywords section
    keywords_pattern = r"Keywords:[\s\S]+?Biologically plausible architectures"
    replacement = """**Keywords:**  
Deep learning  
Convolutional neural networks  
Weight-sharing  
Biologically plausible architectures"""
    
    return re.sub(keywords_pattern, replacement, text)

def fix_abstract(text):
    # Find and replace the abstract section
    abstract_pattern = r"a b s t r a c t\s+Weight-sharing[\s\S]+?by-nc-nd/4.0/"
    replacement = """## Abstract

Weight-sharing is one of the pillars behind Convolutional Neural Networks and their successes. However, in physical neural systems such as the brain, weight-sharing is implausible. This discrepancy raises the fundamental question of whether weight-sharing is necessary. If so, to which degree of precision? If not, what are the alternatives? The goal of this study is to investigate these questions, primarily through simulations where the weight-sharing assumption is relaxed. Taking inspiration from neural circuitry, we explore the use of Free Convolutional Networks and neurons with variable connection patterns. Using Free Convolutional Networks, we show that while weight-sharing is a pragmatic optimization approach, it is not a necessity in computer vision applications. Furthermore, Free Convolutional Networks match the performance observed in standard architectures when trained using properly translated data (akin to video). Under the assumption of translationally augmented data, Free Convolutional Networks learn translationally invariant representations that yield an approximate form of weight-sharing."""
    
    return re.sub(abstract_pattern, replacement, text)

def fix_copyright(text):
    copyright_text = """
*© 2020 The Author(s). Published by Elsevier Ltd. This is an open access article under the CC BY-NC-ND license (http://creativecommons.org/licenses/by-nc-nd/4.0/).*
"""
    
    # Add after abstract
    abstract_pattern = r"## Abstract\n\n.+?weight-sharing\."
    match = re.search(abstract_pattern, text)
    
    if match:
        end_pos = match.end()
        text = text[:end_pos] + "\n\n" + copyright_text + "\n\n" + text[end_pos+1:]
    
    return text

def fix_section_headings(text):
    # Fix section headings
    # Pattern to match section headings like "## 1. Introduction"
    pattern = r"## (\d+)\. (.+)"
    # Replace with proper heading format
    text = re.sub(pattern, r"## \1. \2", text)
    
    # Fix subsection headings
    subsection_pattern = r"### (\d+)\.(\d+)\. (.+)"
    text = re.sub(subsection_pattern, r"### \1.\2 \3", text)
    
    return text

def fix_math_expressions(text):
    # Replace \( and \) with $ for inline math
    text = re.sub(r"\\[(]([^)]+)\\[)]", r"$\1$", text)
    
    # Fix specific math expressions
    text = text.replace("\\(\\mathfrak { C }\\)", "$\\mathfrak{C}$")
    text = text.replace("\\(\\mathsf { V C P \\% }\\)", "$\\mathsf{VCP\\%}$")
    
    return text

def fix_lists(text):
    # Find the research questions section
    pattern = r"In particular, we consider the following research questions:\s+(\d+\. .+?)\s+(\d+\. .+?)\s+(\d+\. .+?)\s+(\d+\. .+?)\s+"
    
    def replace_with_list(match):
        questions = []
        for i in range(1, 5):
            questions.append(f"{i}. {match.group(i).strip()}")
        return "In particular, we consider the following research questions:\n\n" + "\n".join(questions) + "\n\n"
    
    return re.sub(pattern, replace_with_list, text)

def fix_paragraph_spacing(text):
    # Add blank line between paragraphs (sentences ending with period followed by capital letter)
    text = re.sub(r"\.  ([A-Z])", r".\n\n\1", text)
    
    return text

def fix_equation_numbering(text):
    # Find equations with numbers like (1), (2.1), etc.
    equation_pattern = r"\$([^$]+)\$ \((\d+(?:\.\d+)?)\)"
    
    # Replace with standardized format
    text = re.sub(equation_pattern, r"$$\1$$ *(\2)*", text)
    
    return text

def convert_html_tables_to_markdown(text):
    def html_table_to_markdown(html_table):
        soup = BeautifulSoup(html_table, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        
        markdown_table = []
        
        # Process header row
        header_row = rows[0]
        headers = header_row.find_all(['th', 'td'])
        header_texts = [header.get_text().strip() for header in headers]
        markdown_table.append('| ' + ' | '.join(header_texts) + ' |')
        
        # Add separator row
        markdown_table.append('| ' + ' | '.join(['---'] * len(header_texts)) + ' |')
        
        # Process data rows
        for row in rows[1:]:
            cells = row.find_all(['th', 'td'])
            cell_texts = [cell.get_text().strip() for cell in cells]
            markdown_table.append('| ' + ' | '.join(cell_texts) + ' |')
        
        return '\n'.join(markdown_table)
    
    # Find all HTML tables in the text
    html_table_pattern = r"<html><body><table>[\s\S]+?</table></body></html>"
    html_tables = re.findall(html_table_pattern, text)
    
    # Replace each HTML table with its Markdown equivalent
    for html_table in html_tables:
        markdown_table = html_table_to_markdown(html_table)
        text = text.replace(html_table, '\n' + markdown_table + '\n')
    
    return text

def fix_image_references(text):
    # Pattern to match image references like "![](images/filename.jpg)"
    pattern = r"!\[\]\((images/[^)]+)\)"
    
    # Find all instances
    matches = re.findall(pattern, text)
    
    for img_path in matches:
        original = f"![](${img_path})"
        replacement = f"\n\n![Figure](${img_path})\n\n"
        # Fix the original pattern if it doesn't match exactly
        if original not in text:
            original = f"![]({img_path})"
            replacement = f"\n\n![Figure]({img_path})\n\n"
        text = text.replace(original, replacement)
    
    return text

def fix_figure_captions(text):
    # Pattern to match figure captions like "Fig. 1. Free convolutional layers..."
    pattern = r"(!\[.+?\]\(.+?\))\s+Fig\. (\d+)\. (.+?)\s+"
    replacement = r"\1\n\n**Figure \2:** \3\n\n"
    
    return re.sub(pattern, replacement, text)

def fix_references(text):
    # Find the references section
    refs_pattern = r"## References\s+([\s\S]+)$"
    refs_match = re.search(refs_pattern, text)
    
    if refs_match:
        refs_text = refs_match.group(1)
        # Split references by double spaces or line breaks
        refs_list = re.split(r"\s{2,}|\n+", refs_text)
        # Filter out empty strings
        refs_list = [ref.strip() for ref in refs_list if ref.strip()]
        
        # Join formatted references
        formatted_refs_text = "\n\n".join(refs_list)
        
        # Replace references section
        new_refs_section = f"## References\n\n{formatted_refs_text}"
        text = re.sub(refs_pattern, new_refs_section, text)
    
    return text

def main():
    # Read original markdown file
    with open('./to_correct.md', 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Apply all fixes
    text = fix_title_and_authors(text)
    text = fix_affiliations(text)
    text = fix_article_info(text)
    text = fix_keywords(text)
    text = fix_abstract(text)
    text = fix_copyright(text)
    text = fix_section_headings(text)
    text = fix_math_expressions(text)
    text = fix_lists(text)
    text = fix_paragraph_spacing(text)
    text = fix_equation_numbering(text)
    text = convert_html_tables_to_markdown(text)
    text = fix_image_references(text)
    text = fix_figure_captions(text)
    text = fix_references(text)
    
    # Write the corrected markdown file
    with open('./corrected.md', 'w', encoding='utf-8') as file:
        file.write(text)

if __name__ == "__main__":
    main()