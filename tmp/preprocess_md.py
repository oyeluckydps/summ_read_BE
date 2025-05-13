import re

def fix_heading_levels(text):
    # Convert numbered section headings to proper Markdown headings
    text = re.sub(r"^##\s*([0-9]+)\.", r"### \1.", text, flags=re.MULTILINE)  # Demote second-level numbered to third
    text = re.sub(r"^# Learning in the machine", "# Learning in the Machine", text)  # Capitalize consistent title
    text = re.sub(r"^### 1\.", "## 1.", text, flags=re.MULTILINE)  # Promote first section to level 2
    return text

def fix_character_spacing(text):
    # Fix % spacing like \(9 9 \%\) -> \(99\%\)
    text = re.sub(r'\\\((\d)\s+(\d)\s*\\%\)', r'\\(\1\2\\%\)', text)
    # Fix similar with more digits
    text = re.sub(r'\\\((\d)\s+(\d)\s+(\d)\s*\\%\)', lambda m: f"\\({''.join(m.groups())}\\%\\)", text)
    # Remove excess spaces around percent signs
    text = re.sub(r'\(\s*(\d+)\s*\\%\s*\)', r'(\1\\%)', text)
    return text

def fix_equations_and_math(text):
    # Remove unnecessary LaTeX math mode for plain numbers like \(10\%\)
    text = re.sub(r'\\\((\d+)\s*\\%\)', r'\1%', text)
    text = re.sub(r'\\\((\d+)\^ \{ - (\d+) \}\\\)', r'1e-\2', text)  # e.g., \(10^{ - 3}\) -> 1e-3
    return text

def fix_tables_and_html(text):
    # Remove HTML tables, leave placeholder comment
    text = re.sub(r'<html>.*?</html>', '[Table omitted: See original document for structure]', text, flags=re.DOTALL)
    return text

def fix_inline_formatting(text):
    # Remove unwanted double spaces
    text = re.sub(r'(?<!\n)  +', ' ', text)
    # Remove repeated linebreaks but keep paragraph spacing
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def process_markdown_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    text = fix_heading_levels(text)
    text = fix_character_spacing(text)
    text = fix_equations_and_math(text)
    text = fix_tables_and_html(text)
    text = fix_inline_formatting(text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == '__main__':
    process_markdown_file('./to_correct.md', './corrected.md')
