from langchain.prompts import PromptTemplate
from app.template import politician_templates, bill_templates, filtering_templates, bill_qna_template, external_search_template
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate



description_prompt = PromptTemplate.from_template(politician_templates.description_template)

translate_prompt = PromptTemplate.from_template(politician_templates.translate_template)

bill_summary_prompt = PromptTemplate.from_template(bill_templates.bill_summary_template)

bill_children_summary_prompt = PromptTemplate.from_template(bill_templates.bill_children_summary_template)

filtering_prompt = PromptTemplate.from_template(filtering_templates.filtering_template)

json_prompt = hub.pull('teddynote/react-chat-json-korean')


bill_qna_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", bill_qna_template.bill_qna_template),
        ("human", "{input}"),
    ]
)

custom_bill_qna_prompt = hub.pull("rlm/rag-prompt")
custom_bill_qna_prompt.messages[0].prompt.template = bill_qna_template.custom_bill_qna_template

google_search_tool_prompt = hub.pull("hwchase17/openai-functions-agent")
google_search_tool_prompt.messages[0].prompt.template = external_search_template.external_search_template

