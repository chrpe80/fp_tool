from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from sapling import SaplingClient
import spacy
from dotenv import load_dotenv
import os
import threading

# Load environment variables
load_dotenv()


class VariableStorage:
    """I am using the threading library, and this class is to provide access to the variables that are being updated"""

    def __init__(self):
        self._processed_input_text = None
        self._ids = None

    @property
    def processed_input_text(self):
        return self._processed_input_text

    @processed_input_text.setter
    def processed_input_text(self, value):
        self._processed_input_text = value

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, value):
        self._ids = value


def get_api_keys():
    sapling_api_key = os.getenv("SAPLING_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return sapling_api_key, openai_api_key


def create_processing_components(api_keys: tuple, path: str):
    path_exists = os.path.exists(path)
    match path_exists:
        case True:
            sapling_api_key, openai_api_key = api_keys
            sapling_client = SaplingClient(api_key=sapling_api_key)
            nlp = spacy.load(name="sv_core_news_lg")
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=openai_api_key)
            pdf_loader = PyPDFLoader(path)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            vector_store = InMemoryVectorStore(embedding=embeddings)
            return sapling_client, nlp, llm, pdf_loader, text_splitter, vector_store
        case False:
            raise ValueError("The path does not point to the expected endpoint")


def create_prompt_template():
    system_msg = "Du är ett datorprogram som: rättar {errors} i texten och delar in den i stycken."
    user_msg = "Bearbeta denna text: {text}"
    prompt_template = ChatPromptTemplate([("system", system_msg), ("user", user_msg)])
    return prompt_template


def preprocess_user_input_text(input_text, prompt_template, nlp, sapling_client, llm):
    try:
        doc = nlp(input_text)
        sentences = (str(sentence).lower().capitalize() for sentence in doc.sents)
        spellchecked = (sapling_client.spellcheck(sentence, lang="sv", auto_apply=True)["applied_text"] for sentence in sentences)
        spellchecked_text = " ".join(spellchecked)
        errors = ("grammatiska fel", "genus fel", "syntax fel")
        prompt = prompt_template.invoke({"text": spellchecked_text, "errors": errors})
        ai_response = llm.invoke(prompt)
        return ai_response.content
    except Exception as e:
        print(e)


def load_pdf(pdf_loader):
    docs = pdf_loader.load()
    return docs


def process_pdf(docs, text_splitter, vector_store):
    try:
        all_splits = text_splitter.split_documents(documents=docs)
        ids = vector_store.add_documents(documents=all_splits)
        return ids
    except Exception as e:
        print(e)


def process_input_text(input_text, variable_storage, nlp, sapling_client, llm):
    prompt_template = create_prompt_template()
    processed_input_text = preprocess_user_input_text(input_text, prompt_template, nlp, sapling_client, llm)
    variable_storage.processed_input_text = processed_input_text


def load_and_process_pdf(variable_storage, pdf_loader, text_splitter, vector_store):
    docs = load_pdf(pdf_loader=pdf_loader)
    ids = process_pdf(docs=docs, text_splitter=text_splitter, vector_store=vector_store)
    variable_storage.ids = ids


def run(input_text, path):
    try:
        variable_storage = VariableStorage()
        api_keys = get_api_keys()
        sapling_client, nlp, llm, pdf_loader, text_splitter, vector_store = create_processing_components(api_keys=api_keys, path=path)
        thread1 = threading.Thread(target=process_input_text, args=(input_text, variable_storage, nlp, sapling_client, llm))
        thread2 = threading.Thread(target=load_and_process_pdf, args=(variable_storage, pdf_loader, text_splitter, vector_store))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        question = f"Vilken KVÅ kod passar till denna journalanteckning? {variable_storage.processed_input_text}"
        retrieved_docs = vector_store.similarity_search(question)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        template = ChatPromptTemplate([
            ("system", "Du är ett datorprogram som svarar på frågor utifrån detta material: {docs_content}"),
            ("human", "Rekommendera max tre KVÅ koder till denna anteckning: {processed_input_text}"),
            ("human", "svara i formatet: (namn på kod, kod, motivering), (namn på kod, kod, motivering)"),
            ("human", "Vet du inte svaret så säg det"),
        ])
        prompt_value = template.invoke({"docs_content": docs_content, "processed_input_text": variable_storage.processed_input_text})
        recommendation = llm.invoke(prompt_value)
        return {"text": variable_storage.processed_input_text, "recommendation": recommendation}
    except Exception as e:
        print(e)


if __name__ == "__main__":
    try:
        text = """Jag har provat ut patientens nya rullstol. Vi har även tränat förflyttning till och från för att patienten ska bli självständig
        """
        path = r"C:\Users\chris\PycharmProjects\fp_tool\functions\kva-lathund-arbetsterapi.pdf"
        response = run(text, path)
        print(response["text"])
        print(response["recommendation"].content)
    except TypeError as e:
        print(e)
