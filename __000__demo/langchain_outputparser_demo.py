from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Literal

from common.llm import my_llm


# --------- LLM 全局初始化（只创建一次）-------

# --------- 结构化数据模型 ---------
class WordPair(BaseModel):
    word: str = Field(description="英文单词")
    translate: str = Field(description="中文翻译")
    part_of_speech: Literal["动词", "名词", "形容词", "副词"] = Field(description="单词词性")

class WordListOutput(BaseModel):
    word_list: List[WordPair] = Field(description="单词翻译列表")

parser = JsonOutputParser(pydantic_object=WordListOutput)
"""
{
    "word_list":[{"word":"apple", "translate":"苹果"}, {},...]
}

"""


def translate_words_stream(text: str) -> WordListOutput:
    prompt = f"""
请将以下英文单词翻译成中文，并以 JSON 格式返回。
请只输出 JSON，不要包含任何解释性文字。
用户输入单词：{text}
返回格式要求如下：
{parser.get_format_instructions()}

"""
    str_result = my_llm.invoke(prompt).content
    result_dict = parser.parse(str_result)
    return result_dict

    # full_content = ""
    #
    # for chunk in my_llm.stream(prompt):
    #     if chunk.content:
    #         print(chunk.content, end="", flush=True)
    #         full_content += chunk.content
    #
    # print()
    # return parser.parse(full_content)


if __name__ == '__main__':
    result = translate_words_stream("hello, work，apple, handsome, alone, lonely, quickly")
    print("*" * 100)
    print(result)
