def main(author_data: list) -> dict:
    """
    Extracts the top 5 most important properties for an author from OpenAlex metadata.
    Ensures all values are returned as strings.

    :param author_data: JSON object containing author details.
    :return: A dictionary containing the extracted author information.
    """
    # Extract affiliations as a comma-separated string
    author_data = author_data[0]
    affiliations = [
        aff["institution"]["display_name"]
        for aff in author_data.get("affiliations", [])
        if "institution" in aff and "display_name" in aff["institution"]
    ]
    affiliations_str = ", ".join(affiliations) if affiliations else "No affiliations available"

    extracted_author = {
        "name": str(author_data.get("display_name", "")),
        "id": str(author_data.get("id", "")),
        "works_count": str(author_data.get("works_count", 0)),
        "cited_by_count": str(author_data.get("cited_by_count", 0)),
        "affiliations": affiliations_str
    }

    return {"extracted_author": str(extracted_author)}