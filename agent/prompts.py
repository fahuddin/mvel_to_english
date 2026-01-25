from langchain_core.prompts import ChatPromptTemplate

EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a rules analyst."),
    ("user",
     "Given this extracted rule structure:\n{extraction}\n\n"
     "Do not add new logic. Confirm structure is correct.")
])

ENGLISH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You write for non-technical stakeholders."),
    ("user",
     "Convert this rule structure into clear English.\n\n"
     "Rules:\n"
     "- Start with a short summary\n"
     "- Then list decision logic as bullets\n"
     "- Use 'Otherwise' for DEFAULT\n\n"
     "{extraction}")
])
