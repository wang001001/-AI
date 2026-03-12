from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os
import dashscope

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

prompt = "生成一个 动漫简约阴郁风格的雨伞"
api_key = ""


def generate_image():
    print('----同步调用，请等待任务执行----')
    rsp = ImageSynthesis.call(
        api_key=api_key,
        model="qwen-image-plus",
        prompt=prompt,
        negative_prompt=" ",
        n=1,
        size='1664*928',
        prompt_extend=True,
        watermark=False,
    )
    print(f'response: {rsp}')
    if rsp.status_code == HTTPStatus.OK:
        # 在当前目录下保存图像
        for result in rsp.output.results:
            file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
            with open(f'./{file_name}', 'wb+') as f:
                f.write(requests.get(result.url).content)
    else:
        print(f'同步调用失败, status_code: {rsp.status_code}, code: {rsp.code}, message: {rsp.message}')


if __name__ == "__main__":
    generate_image()
