from app import llms, prompt
from langchain_core.output_parsers import StrOutputParser


output_parser = StrOutputParser()

description_chain = prompt.description_prompt | llms.gpt | output_parser

tranlate_chain = prompt.translate_prompt | llms.eeve | output_parser

bill_summary_chain = prompt.bill_summary_prompt | llms.gpt | output_parser

bill_children_summary_chain = prompt.bill_children_summary_prompt | llms.gpt | output_parser

filtering_chain = prompt.filtering_prompt | llms.gpt | output_parser

# qna_chain = prompt.qna_prompt | llms.gpt | output_parser

