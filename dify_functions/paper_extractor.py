import json

def extract_author_id(author_url):
    """Extracts only the ID from an OpenAlex author URL."""
    if author_url and isinstance(author_url, str):
        return author_url.split("/")[-1]  # Get last part after '/'
    return ""

def main(paper: dict, validator: str) -> dict:
    """
    Extracts relevant details from a single paper retrieved from OpenAlex API,
    and returns the paper's metadata along with author IDs and primary topic.

    :param paper: Dictionary containing paper details.
    :param validator: String flag determining whether to extract paper details.
    :return: A formatted dictionary with extracted paper metadata.
    """

    # If the validator says "false", return an empty object
    if not validator or "false" in validator.lower().strip():
        return {"extracted_paper": {}}

    # Ensure paper is a valid dictionary
    if not isinstance(paper, dict):
        return {"error": "Invalid paper data provided."}

    # Extract author IDs
    author_ids = [
        extract_author_id(author_entry["author"]["id"])
        for author_entry in paper.get("authorships", []) 
        if isinstance(author_entry, dict) and isinstance(author_entry.get("author"), dict) and author_entry["author"].get("id")
    ]

    # Extract primary topic name only

    primary_topic = paper.get("primary_topic", {})
    extracted_topic = {
        "display_name": primary_topic.get("display_name", ""),
        "subfield": primary_topic.get("subfield", {}).get("display_name", ""),
        "field": primary_topic.get("field", {}).get("display_name", ""),
        "domain": primary_topic.get("domain", {}).get("display_name", ""),
        "id": primary_topic.get("id", "")
    } if isinstance(primary_topic, dict) else {}

    # Extract paper metadata
    extracted_paper = {
        "title": paper.get("title", ""),
        "id": paper.get("id", ""),
        "doi": paper.get("doi", ""),
        "publication_year": paper.get("publication_year", ""),
        "publication_date": paper.get("publication_date", ""),
        "language": paper.get("language", ""),
        "type": paper.get("type", ""),
        "is_oa": paper.get("open_access", {}).get("is_oa", False) if isinstance(paper.get("open_access"), dict) else False,
        "oa_url": paper.get("open_access", {}).get("oa_url", "") if isinstance(paper.get("open_access"), dict) else "",
        "has_fulltext": paper.get("has_fulltext", False),
        "cited_by_count": paper.get("cited_by_count", 0),
        "citation_normalized_percentile": paper.get("citation_normalized_percentile", {}).get("value", 0) if isinstance(paper.get("citation_normalized_percentile"), dict) else 0,
        "cited_by_api_url": paper.get("cited_by_api_url", ""),
        # "authorships": [
        #     {
        #         "author_id": extract_author_id(author_entry["author"]["id"]),
        #         "author_name": author_entry["author"]["display_name"],
        #         "institutions": [
        #             {
        #                 "id": inst["id"],
        #                 "name": inst["display_name"]
        #             } for inst in author_entry.get("institutions", []) if isinstance(inst, dict) and inst.get("id")
        #         ]
        #     } for author_entry in paper.get("authorships", []) if isinstance(author_entry, dict) and isinstance(author_entry.get("author"), dict)
        # ],
        # "primary_topic": paper.get("primary_topic", {}).get("display_name", "") if isinstance(paper.get("primary_topic"), dict) else "",  # Replace with just display_name
        # "topics": [topic["display_name"] for topic in paper.get("topics", []) if isinstance(topic, dict) and topic.get("display_name")],
        # "concepts": [concept["display_name"] for concept in paper.get("concepts", []) if isinstance(concept, dict) and concept.get("display_name")],
        # "referenced_papers_count": len(paper.get("referenced_works", []) or []),
        # "referenced_papers": paper.get("referenced_works", []) if isinstance(paper.get("referenced_works"), list) else [],
        # "related_papers": paper.get("related_works", []) if isinstance(paper.get("related_works"), list) else [],
        "updated_date": paper.get("updated_date", ""),
        "created_date": paper.get("created_date", "")
    }

    # Final formatted output
    final_paper = {
        "paper_metadata": extracted_paper,
        "authors": author_ids,
        "topics": extracted_topic,
        "abstract_index": paper.get("abstract_inverted_index", "")
    }

    return {"extracted_paper": final_paper}

def extract_abstract(abstract_index: dict) -> str:
    """
    Reconstructs the abstract from OpenAlex's abstract_inverted_index.
    
    :param work_data: JSON object containing OpenAlex work details.
    :return: Reconstructed abstract as a string.
    """

    # abstract_index = work_data.get("abstract_inverted_index", {})


    if not abstract_index:
        return "Abstract not available."

    # Create a list to store words in correct order
    max_position = max(pos for positions in abstract_index.values() for pos in positions)
    abstract_words = [""] * (max_position + 1)

    for word, positions in abstract_index.items():
        for pos in positions:
            abstract_words[pos] = word

    return " ".join(abstract_words)


def main8(papers: list, Type_of_Paper: str, Paper_summary: str) -> dict:
    filter_paper = {
        "paper_metadata": "{}",
        "authors": [],
        "topics": "{}"
    }
    for paper in papers:
        if len(paper) > 0:
            paper_metadata  = paper.get("paper_metadata", "")
            if Type_of_Paper == "Research_Paper":
                paper_metadata["summary"] = f""" Summary. \n {Paper_summary}"""
            else:
                abstract = extract_abstract(paper.get("abstract_index", {}))
                paper_metadata["summary"] = f""" Abstract. \n {abstract}"""

            filter_paper = {
               "paper_metadata": str(paper.get("paper_metadata", "")),
                "authors": paper.get("authors", ""),
                "topics": str(paper.get("topics", ""))
            }
            break
    return filter_paper
    