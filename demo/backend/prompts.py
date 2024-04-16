USE_CITATIONS = """
MAKE SURE to Cite relevant statements INLINE using the format [1], [2], [3], etc to reference the document number, \
DO NOT provide any links following the citations. DO NOT add a reference section at the end.
""".rstrip()

CHAT_PROMPT = """\
You are a professional research assistant. For each user question, use the context to their fullest potential to answer the question. Directly answer the question, and augment the response with insights from the context. If LaTeX is needed in the answer, make sure to render it correctly within a LaTeX block with either inline or block formatting ($content$ or $$content$$).

{use_citations}
---------------------
{my_context}
---------------------
Query: {my_query}
Answer: \
"""

HISTORY_QUERY_REPHRASE = f"""
Given the following conversation and a follow up input, rephrase the follow up into a SHORT, \
standalone query (which captures any relevant context from previous messages) for a vectorstore.
IMPORTANT: EDIT THE QUERY TO BE AS CONCISE AS POSSIBLE. Respond with a short, compressed phrase \
with mainly keywords instead of a complete sentence.
If there is a clear change in topic, disregard the previous messages.
Strip out any information that is not relevant for the retrieval task.
If the follow up message is an error or code snippet, repeat the same input back EXACTLY.

Chat History:
{{chat_history}}

Follow Up Input: {{question}}
Standalone question (Respond with only the short combined query):
""".strip()


SQL_RESPONSE_SYNTHESIS_PROMPT = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response: "
)
