from langchain_openai import ChatOpenAI
from common.config import Config

conf = Config()

# ============ 配置llm区域 ============
my_llm = ChatOpenAI(
    api_key=conf.DEEPSEEK_API_KEY or conf.MODEL_API_KEY,
    base_url=conf.DEEPSEEK_BASE_URL or conf.MODEL_BASE_URL,
    model=conf.DEEPSEEK_MODEL or conf.MODEL_NAME
)

if __name__ == '__main__':
    result = ""

    for chunk in my_llm.stream("介绍一下微观经济学。"):
        print(chunk.content, end="", flush=True)
        result += chunk.content
    print("\n", "*"*100)
    print(result)
