"""
Configuration settings for MD Preprocess library.
"""

# Default configuration values
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_OUTPUT_DIR = "temp_preprocess"
DEFAULT_LLM = "claude"

# Prompt templates for LLM
CORRECTION_PROMPT = """
You are an expert editor and Markdown document corrector. Please review the following .md content and correct it to produce a clean, human-readable, and semantically accurate Markdown file. In particular:
    Correct heading hierarchy:
    Ensure that all section, subsection, and sub-subsection headings are properly marked using #, ##, ###, etc., according to the logical structure of the content. Fix any lines that are mistakenly interpreted as headings or vice versa.
    Fix character-level extraction errors:
    Restore any missing initial characters (e.g., braham Iincon --> Abraham Lincoln).
        Correct garbled text from OCR or PDF extraction, including misplaced symbols, mis-capitalizations, and misplaced mathematical expressions.
    Preserve and clarify structure:
        Ensure proper paragraph separation.
        Keep figure captions, equations, and citation markers readable and consistent.
        If an image tag or equation block appears mid-paragraph incorrectly, relocate it appropriately.
    Keep the content unchanged except for fixes:
    Do not rephrase or summarize the content. Maintain all original information, figures, and citations.
    Ensure that all Markdown syntax is correct and renders properly (especially for images, equations, and code blocks).
Now instead of directly writing back the md file, I would like you to write a simple python code that would make all the changes that you wish to make. Assume the the input file is {input_file} and the output from the Python code is {output_file}.
Write the code to correct inaccuracies or shortcomings of only this specific file. Reply only with the Python code without any additional text or explanation.
This code shall be executed using the exec() function in the Python interpreter so write the code in a way that doesn't use __main__.
"""

ERROR_RETRY_PROMPT = """
The Python code you provided encountered an error:

Error: {error_message}
At line {line_number}: {error_line}

Full code:
{code}

Please fix the error and provide corrected code that performs the same preprocessing task.
Remember the input and output file paths remain the same.
"""

# List of common PDF extraction issues to address
PDF_EXTRACTION_ISSUES = [
    "Page numbers appearing within content",
    "Headers and footers mixed with text",
    "Hyphenated words split across lines",
    "Columns being read out of order",
    "Tables formatted inconsistently",
    "Code blocks missing formatting",
    "Lists with broken indentation",
    "Footnotes and citations mixed into text",
    "Paragraph breaks lost",
    "Special characters like bullets incorrectly represented"
]

