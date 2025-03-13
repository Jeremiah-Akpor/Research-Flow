import json



# def extract_title_authors(paper: dict) -> dict:
#     title = ""
#     Authors = set()


        
#     title = paper.get("title", "")
#     # Extract the list of authors for this work safely
#     for author_entry in paper.get("authorships", []) or []:
#         author = author_entry.get("author")
#         if isinstance(author, dict):
#             author_name = author.get("display_name")
#             if author_name:
#                 Authors.add(author_name)
                


#     return {
#         "Extracted_title": title,
#         "Extracted_Authors": str(Authors)
#     }

# def main(papers: list) -> dict:
#     result = {}
#     titles = []
#     authors = []
#     papers = papers[0].get("results", [])
#     papers = papers[:4]
#     for i, paper in enumerate(papers):
#         title_authors = extract_title_authors(paper)
#         titles.append(title_authors["Extracted_title"])
#         authors.append(title_authors["Extracted_Authors"])
#         result[f"paper_{i+1}"] = paper
#         result[f"paper_{i+1}_title"] = titles[i]
#         result[f"paper_{i+1}_authors"] = authors[i]

#     return result

# Example Usage

# with open("dify_functions/ref_data.json", "r") as file:
#     data = json.load(file)
#     papers = data.get("papers", [])
#     papers = papers[:5]
# if __name__ == "__main__":
#     extracted_data = main(papers)
#     print(json.dumps(extracted_data, indent=4))

import json
def extract_correct_paper(api_response, original_title):
    
    

    # Check if the response contains results
    if "results" not in api_response or not api_response["results"]:
        return {}

    # Normalize the original title for case-insensitive comparison
    normalized_title = original_title.strip().lower()

    # List to store matched papers
    matched_papers = []

    # Loop through results to find the exact title match
    for paper in api_response["results"]:
        if "title" in paper and paper["title"].strip().lower() == normalized_title:
            matched_papers.append(paper)

    # If multiple matches exist, choose the one with the highest relevance_score
    if matched_papers:
        best_match = max(matched_papers, key=lambda x: x.get("relevance_score", 0))
        return  best_match

    # If no exact match is found, return an empty dictionary
    return {}

def extract_abstract(abstract_index: dict) -> str:
    """
    Reconstructs the abstract from OpenAlex's abstract_inverted_index.
    
    :param abstract_index: JSON object containing OpenAlex work details.
    :return: Reconstructed abstract as a string.
    """
    if not abstract_index:
        return "Abstract not available."

    # Create a list to store words in correct order
    max_position = max(pos for positions in abstract_index.values() for pos in positions)
    abstract_words = [""] * (max_position + 1)

    for word, positions in abstract_index.items():
        for pos in positions:
            abstract_words[pos] = word

    return " ".join(abstract_words)



def extract_graph_metadata(paper_metadata):
    """
    Extracts necessary properties for Research_Paper, Source, Concept Nodes, and Topic Nodes.

    :param paper_metadata: Dictionary containing paper details
    :return: Dictionary with extracted metadata
    """
    # Extract Research Paper details
    research_paper = {
        "id": paper_metadata.get("id", ""),
        "doi": paper_metadata.get("doi", ""),
        "title": paper_metadata.get("title", ""),
        "publication_year": paper_metadata.get("publication_year", ""),
        "publication_date": paper_metadata.get("publication_date", ""),
        "language": paper_metadata.get("language", ""),
        "open_access_status": paper_metadata.get("open_access", {}).get("oa_status", ""),
        "cited_by_count": paper_metadata.get("cited_by_count", 0),
        "authors": ", ".join([author["author"]["display_name"] for author in paper_metadata.get("authorships", []) if "author" in author]),
        "summary": extract_abstract(paper_metadata.get("abstract_inverted_index", {}))
    }

    
    return str(research_paper)


def main(api_response: dict) -> dict:
    paper = {
        "Reference_Paper": "{}"
    }
    paper["Reference_Paper"] = extract_graph_metadata(api_response)
    return paper



