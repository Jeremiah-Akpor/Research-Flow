import re

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """
    Splits the extracted text into chunks of a specified size with optional overlap.

    Args:
        text (str): The text extracted from the PDF.
        chunk_size (int): The maximum number of characters in each chunk.
        overlap (int): The number of characters to overlap between chunks.

    Returns:
        list: A list of text chunks.
    """
    text = re.sub(r'\n+', '\n', text).strip()  # Normalize newlines
    words = text.split()  # Split text into words
    chunks = []
    
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # Move start forward with overlap

    return chunks

def extract_references(chunks: list) -> str:
    """
    Extracts the reference section from the chunked text, ensuring multiple chunks
    are combined if the references span across them.

    Args:
        chunks (list): A list of text chunks.

    Returns:
        str: The extracted reference section.
    """
    reference_keywords = ["references", "bibliography", "cited works"]
    reference_chunks = []

    # Reverse search for the references section and combine multiple chunks
    for chunk in reversed(chunks):
        if any(keyword.lower() in chunk.lower() for keyword in reference_keywords):
            
            # Split the chunk at the point where the reference section starts
            split_chunk = re.split(r'\b(?:references|bibliography|cited works)\b', chunk, flags=re.IGNORECASE)
            if len(split_chunk) > 1:
                reference_chunks.append("References\n" + split_chunk[1].strip())
            else:
                reference_chunks.append(chunk)
            break  # Stop searching once the references section is found
        else:
            reference_chunks.append(chunk)

    reference_text = "\n".join(reversed(reference_chunks))  # Ensure the order is correct

    # Extract individual references
    references = re.findall(r'\[\d+\].*?(?=\[\d+\]|$)', reference_text, re.DOTALL)
    return references #[:7]   Limit the number of references to less than 30

def extract_main_body(text: str) -> str:
    """
    Extracts the main body of the research paper by identifying the introduction,
    abstract, and stopping before references.

    Args:
        text (str): The full text of the paper.

    Returns:
        str: The extracted main body section.
    """
    # Identify Abstract
    abstract_match = re.search(r'\b(?:Abstract|Summary)\b', text, re.IGNORECASE)
    abstract_end = abstract_match.end() if abstract_match else 0

    # Identify Introduction
    intro_match = re.search(r'\b(?:Introduction|1\.|I\.)\b', text, re.IGNORECASE)
    intro_start = intro_match.start() if intro_match else None

    # Identify References
    reference_match = re.search(r'\b(?:references|bibliography|cited works)\b', text, re.IGNORECASE)
    reference_start = reference_match.start() if reference_match else len(text)

    # Identify the first major section after Abstract (if no Introduction is found)
    section_match = re.search(r'\b(?:Methods|Methodology|Materials|Results|Discussion|Experiment|Analysis|Findings)\b', 
                              text[abstract_end:reference_start], re.IGNORECASE)
    first_section_start = section_match.start() + abstract_end if section_match else abstract_end

    # If Introduction exists, start from there; otherwise, start from first major section
    main_start = intro_start if intro_start else first_section_start

    return text[main_start:reference_start].strip()

def main(pdf_text: str, chunk_size: int = 1000, overlap: int = 200) -> dict:
    """
    Main function to chunk the PDF text, extract references, and extract the main body.

    Args:
        pdf_text (str): The extracted text from the PDF.
        chunk_size (int): The size of each chunk.
        overlap (int): The number of characters to overlap between chunks.

    Returns:
        dict: A dictionary containing the chunks, title chunk, main body, and reference chunk.
    """
    chunks = chunk_text(pdf_text, chunk_size, overlap)
    full_text = " ".join(chunks)  # Reconstruct full text from chunks

    title_chunk = chunks[0] if len(chunks) > 0 else ""  # First chunk is the title
    main_body = extract_main_body(full_text)  # Extract main body
    reference_chunk = extract_references(full_text)  # Extract references section

    return {
        "chunks": chunks,
        "title_chunk": title_chunk,
        "main_body": main_body,
        "reference_chunk": reference_chunk[:7] # Limit the number of references to less than 30
    }

# Example usage with extracted PDF content
pdf_content = """
Portfolio Exam

Engineering with Generative AI  
(Winter Semester 2024/25)

Abstract
This document provides an overview of the research tasks involved in this exam.

Introduction
This paper discusses the usage of Generative AI in research workflows.
The primary objective is to construct a structured graph using DIFY.

Methods
We fine-tuned a model and used Neo4j for structuring the extracted data.

Results
The model improved performance by 10% after fine-tuning.

Discussion
Challenges included handling large context windows.

References
[1] J. Doe et al., "LLM Paper Title," AI Journal, 2021.
[2] A. Smith, "Deep Learning Research," NeurIPS, 2020.
https://arxiv.org/abs/1706.03762
"""

result = main(pdf_content)
print("Title Chunk:", result["title_chunk"])
print("\nMain Body:\n", result["main_body"])
print("\nReference Chunk:\n", result["reference_chunk"])