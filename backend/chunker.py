from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def chunk_pages(pages: list[dict]) -> list[dict]:
    chunks = []

    for page in pages:
        splits = splitter.split_text(page["text"])

        for split in splits:
            chunks.append({
                "text": split,
                "page": page["page"]
            })

    return chunks