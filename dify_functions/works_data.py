import json

def extract_author_id(author_url):
    """Extracts only the ID from an OpenAlex author URL."""
    if author_url and isinstance(author_url, str):
        return author_url.split("/")[-1]  # Get last part after '/'
    return ""

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


def extract_graph_metadata(paper_metadata, summary:str):
    """
    Extracts necessary properties for Research_Paper, Source, Concept Nodes, and Topic Nodes.

    :param paper_metadata: Dictionary containing paper details
    :return: Dictionary with extracted metadata
    """
    # Extract Research Paper details
    research_paper = {
        "title": paper_metadata.get("title", ""),
        "id": paper_metadata.get("id", ""),
        "doi": paper_metadata.get("doi", ""),
        "publication_year": paper_metadata.get("publication_year", ""),
        "publication_date": paper_metadata.get("publication_date", ""),
        "language": paper_metadata.get("language", ""),
        "open_access_status": paper_metadata.get("open_access", {}).get("oa_status", ""),
        "cited_by_count": paper_metadata.get("cited_by_count", 0),
        "authors": ", ".join([author["author"]["display_name"] for author in paper_metadata.get("authorships", []) if "author" in author]),
        "summary": summary
    }

    # Extract Source details
    primary_location = paper_metadata.get("primary_location", {})
    source = primary_location.get("source", {})
    source_node = {
        "name": source.get("display_name", ""),
        "id": source.get("id", ""),
        "type": source.get("type", ""),
        "is_oa": source.get("is_oa", False),
        "host_organization": source.get("host_organization_name", ""),
        "landing_page_url": primary_location.get("landing_page_url", "")
    }

    # Extract Concepts
    concepts = [
        {
            "name": concept.get("display_name", ""),
            "id": concept.get("id", ""),
            "wikidata": concept.get("wikidata", ""),
            "level": concept.get("level", ""),
            "score": concept.get("score", 0.0)
        }
        for concept in paper_metadata.get("concepts", [])
    ]

    # Extract Topics
    topics = [
        {
            "name": topic.get("display_name", ""),
            "id": topic.get("id", ""),
            "subfield": topic.get("subfield", {}).get("display_name", ""),
            "field": topic.get("field", {}).get("display_name", ""),
            "domain": topic.get("domain", {}).get("display_name", ""),
            "score": topic.get("score", 0.0)
        }
        for topic in paper_metadata.get("topics", [])
    ]
    # Extract author IDs
    author_ids = [
        extract_author_id(author_entry["author"]["id"])
        for author_entry in paper_metadata.get("authorships", []) 
        if isinstance(author_entry, dict) and isinstance(author_entry.get("author"), dict) and author_entry["author"].get("id")
    ]

    return {
        "Research_Paper": str(research_paper),
        "Source": str(source_node),
        "Concepts": concepts,
        "Topics": topics,
        "Author_IDs": author_ids
    }

def main(api_response: dict, original_title:str, summary:str) -> dict:
    filtered_metadata = extract_correct_paper(api_response[0], original_title)
    paper = {}
    if filtered_metadata or filtered_metadata != {}:
        paper = extract_graph_metadata(filtered_metadata, summary)
    return paper

# Example Usage
if __name__ == "__main__":
    with open("paper_metadata.json", "r") as f:
        paper_data = json.load(f)

    extracted_data = extract_graph_metadata(paper_data)
    print(json.dumps(extracted_data, indent=4))
