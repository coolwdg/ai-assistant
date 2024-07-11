import re
import subprocess
import requests
import json
from gradio_client import Client
import speech_recognition as sr

secretKey = "xxx"
appKey = "xxx"
apiAddress = "xxx"

def voice_input():
    # 创建 SpeechRecognition 对象
    r = sr.Recognizer()
    # 读取音频文件
    with sr.Microphone() as source:
        print("speak:")
        audio = r.listen(source)
    # 识别音频文件
    try:
        speekContent = json.loads(r.recognize_vosk(audio, language='zh-CN'))
        # speekContent = {
        #     "text": "你好 请问 你 是 谁"
        # }
        speekContent = speekContent["text"].replace(" ", "")
        return speekContent
    except sr.UnknownValueError:
        raise 'Google Speech Recognition could not understand audio'
    except sr.RequestError as e:
        raise 'Could not request results from Google Speech Recognition Service'

def prompt_optimzer(prompt:str):
    try:
        client = Client(apiAddress)
        result = client.predict(
            input='你是一名资深的提示词工程师和软件工程师，你的任务是优化并补充用户给出的提示词，使其描述更加清晰和准确。你仅需要给出优化后的提示词，不用其他的解释。下面是你要优化的提示词：' + prompt,
            chatbot=[],
            max_length=2048,
            top_p=0.7,
            temperature=0.95,
            api_name="/predict"
        )
        # 访问内部列表的元素（注意：这里我们假设列表只包含一个内部列表）
        text = result[0][1]

        # 使用split方法找到<br>之后的内容，并取第一个结果（因为<br>之后可能还有多个部分）
        # 注意：这里我们假设"<br>"之后紧接着就是我们要找的提示词
        # 但实际上，可能需要更复杂的逻辑来处理多个<br>标签或不同格式的情况
        parts = text.split('<br>')
        if len(parts) > 1:
            # 移除引号（如果提示词被引号包围）
            optimized_hint = parts[1].strip().strip('"')
            return optimized_hint
        else:
            return prompt
    except Exception as e:
        print(e)
        return prompt


def extract_code_block(response):
    # 使用正则表达式从响应中提取代码块
    code_block_pattern = r'```python(.*?)```'
    match = re.search(code_block_pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """

    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id="+appKey+"&client_secret="+secretKey

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


require = []
headers = {
    'Content-Type': 'application/json'
}


def main():
    global require
    require = []
    isSuccess = False
    requireTimes = 0
    while not isSuccess and requireTimes < 5:
        isSuccess = corePredict(requireTimes != 0)
        requireTimes += 1


def corePredict(isRepeat):
    if not isRepeat:
        # user_input = input("请输入您想要与大模型交互的内容：")
        user_input = prompt_optimzer(voice_input())

        newContent = {
            "role": "user",
            "content": user_input + "\n###只需给出代码，不用解释。同时需要满足如下规则\n1.关于曲线绘制的至少光滑一点\n2.如果使用np，请在代码中加入import numpy as np\n3.如果画图请加上plt.rcParams['font.sans-serif'] = ['SimHei']\n4.如果涉及到负号请使用plt.rcParams['axes.unicode_minus'] = False"
        }
        require.append(newContent)

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + get_access_token()

    payload = json.dumps({
        "messages": require
    })

    response = requests.post(url, headers=headers, data=payload)
    response_data = response.json()

    # 检查响应是否包含我们期望的字段
    if 'result' in response_data:
        model_response = response_data['result']
        model_code = extract_code_block(model_response)
        # 生成并写入Python文件
        with open('new_script.py', 'w', encoding='utf-8') as file:
            file.write(model_code)
        try:
            subprocess.run([r'D:\Program Files\python\venv\huawei\Scripts\python.exe', 'new_script.py'])
            return True
        except Exception as e:
            newContent = [
                {
                    "role": "assistant",
                    "content": model_code
                }, {
                    "role": "user",
                    "content": "报错:" + str(e)
                }]
            require.append(newContent[0])
            require.append(newContent[1])
            return False

    else:
        print("未收到预期的回复")
        return True



if __name__ == '__main__':
    while True:
        main()
