import unittest
from unittest.mock import Mock
from all_functions import *
import os

api_keys = get_api_keys()
path = r"C:\Users\chris\PycharmProjects\fp_tool\functions\kva-lathund-arbetsterapi.pdf"
sapling_client, nlp, llm, pdf_loader, text_splitter, vector_store = create_processing_components(api_keys, path)
input_text = "Det var en gång en pojke från skåne som hette Oscar."
prompt_template = create_prompt_template()
docs = load_pdf(pdf_loader)


class TestFunctions(unittest.TestCase):
    def test_get_api_keys(self):
        self.assertIsInstance(get_api_keys(), tuple)
        self.assertEqual(get_api_keys()[0], os.getenv("SAPLING_API_KEY"))
        self.assertEqual(get_api_keys()[1], os.getenv("OPENAI_API_KEY"))

    def test_create_processing_components(self):
        self.assertIsInstance(create_processing_components(api_keys, path), tuple)
        self.assertEqual(len(create_processing_components(api_keys, path)), 6)
        self.assertRaises(ValueError, create_processing_components, api_keys, "wrong_path.pdf")

    def test_create_prompt_template(self):
        expectation = ChatPromptTemplate
        self.assertIsInstance(create_prompt_template(), expectation)

    def test_preprocess_user_input_text(self):
        self.assertIsInstance(preprocess_user_input_text(input_text, prompt_template, nlp, sapling_client, llm), str)
        mocked_sapling_api_key = Mock(os.getenv("SAPLING_API_KEY"))
        mocked_sapling_api_key.return_value = "abc123"
        mocked_openai_api_key = Mock(os.getenv("OPENAI_API_KEY"))
        mocked_openai_api_key.return_value = "abc123"
        self.assertRaises(Exception, preprocess_user_input_text(input_text, prompt_template, nlp, sapling_client, llm))

    def test_load_pdf(self):
        self.assertIsInstance(load_pdf(pdf_loader), list)

    def test_process_pdf(self):
        self.assertIsInstance(process_pdf(docs, text_splitter, vector_store), list)
        mocked_openai_api_key = Mock(os.getenv("OPENAI_API_KEY"))
        mocked_openai_api_key.return_value = "abc123"
        self.assertRaises(Exception, process_pdf(docs, text_splitter, vector_store))

    def test_process_input_text(self):
        process_input_text(input_text, vector_store, nlp, sapling_client, llm)
        self.assertIsNotNone(VariableStorage.processed_input_text)

    def test_load_and_process_pdf(self):
        variable_storage = VariableStorage()
        load_and_process_pdf(variable_storage, pdf_loader, text_splitter, vector_store)
        self.assertIsNotNone(variable_storage.ids)

    def test_run(self):
        self.assertIsInstance(run(input_text, path), dict)


if __name__ == "__main__":
    unittest.main()
