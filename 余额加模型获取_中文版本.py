import requests
import random
import os
from tabulate import tabulate
import datetime
import time

# ANSI字体颜色代码 (仅前景色)
colors = [
    '\033[31m',  # 红色 (Red)
    '\033[32m',  # 绿色 (Green)
    '\033[33m',  # 黄色 (Yellow)
    '\033[34m',  # 蓝色 (Blue)
    '\033[35m',  # 紫色 (Magenta)
    '\033[36m',  # 青色 (Cyan)
    '\033[37m',  # 白色 (White)
    '\033[90m',  # 灰色 (Grey)
]

RESET = '\033[0m'

api_key = None
url = None

company_mapping = {
    "anthropic": {"中文": "Anthropic"},
    "openai": {"中文": "OpenAI"},
    "deepseek": {"中文": "DeepSeek"},
    "doubao": {"中文": "豆包"},
    "google": {"中文": "谷歌"},
    "zhipu": {"中文": "智谱"},
    "Zhipu_4v": {"中文": "智谱"},
    "midjourney": {"中文": "Midjourney"},
    "moonshot": {"中文": "Moonshot"},
    "alibaba": {"中文": "阿里巴巴"},
    "iflytek": {"中文": "讯飞"},
    "baidu": {"中文": "百度"},
    "tencent": {"中文": "腾讯"},
    "microsoft": {"中文": "微软"},
    "huggingface": {"中文": "Hugging Face"},
    "stabilityai": {"中文": "Stability AI"},
    "cohere": {"中文": "Cohere"},
    "ai21": {"中文": "AI21 Labs"},
    "nvidia": {"中文": "NVIDIA"},
    "apple": {"中文": "苹果"},
    "salesforce": {"中文": "Salesforce"},
    "xiaomi": {"中文": "小米"},
    "meituan": {"中文": "美团"},
    "jd": {"中文": "京东"},
    "bytedance": {"中文": "字节跳动"},
    "facebook": {"中文": "Facebook"},
    "amazon": {"中文": "亚马逊"},
    "oracle": {"中文": "甲骨文"},
    "intel": {"中文": "英特尔"},
    "qualcomm": {"中文": "高通"},
    "Custom": {"中文": "其他"}
}

def generate_random_colors(num_colors):
    random.shuffle(colors)
    return colors[:num_colors]

def categorize_and_color_models(models):
    categorized_models = {}
    company_names = {company_mapping.get(model['owned_by'].lower(), {"中文": model['owned_by']})["中文"] for model in models}
    company_colors = {company: color for company, color in zip(company_names, generate_random_colors(len(company_names)))}
    
    for model in models:
        model_name = model['id']
        owned_by = model.get('owned_by', 'unknown').lower()
        company_name = company_mapping.get(owned_by, {"中文": owned_by})["中文"]
        
        color = company_colors.get(company_name, RESET)
        colored_model = f"{color}{model_name}{RESET}"
        
        if company_name not in categorized_models:
            categorized_models[company_name] = []
        categorized_models[company_name].append(colored_model)
    
    return categorized_models

def print_categorized_models(categorized_models):
    table = []
    for company, models in categorized_models.items():
        table.append([f"\033[1m{company.capitalize()}\033[0m", "\n".join(models)])
    
    print(f"\033[34m{tabulate(table, headers=['公司', '模型列表'], tablefmt='grid')}{RESET}")

def get_available_models():
    try:
        response = requests.get(url + '/v1/models', headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"})
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}获取模型时出错：{e}{RESET}")
        return []

def get_balance():
    headers = {'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"}

    subscription_url = "/v1/dashboard/billing/subscription"
    subscription_response = requests.get(url + subscription_url, headers=headers)
    if subscription_response.status_code == 200:
        data = subscription_response.json()
        total = data.get("hard_limit_usd")
    else:
        print(f"{colors[0]}{subscription_response.text}{RESET}")
        total = 0

    start_date = (datetime.datetime.now() - datetime.timedelta(days=99)).strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    billing_url = f"{url}/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    billing_response = requests.get(billing_url, headers=headers)
    if billing_response.status_code == 200:
        data = billing_response.json()
        total_usage = data.get("total_usage") / 100
    else:
        print(f"{colors[0]}{billing_response.text}{RESET}")
        total_usage = 0

    remaining = total - total_usage
    print(f"{colors[1]}当前账户余额信息：{RESET}")
    print(f"{colors[2]}总额:\t{total:.4f}美元{RESET}")
    print(f"{colors[3]}已用:\t{total_usage:.4f}美元{RESET}")
    print(f"{colors[4]}剩余:\t{remaining:.4f}美元{RESET}")

def test_model():
    print(f"{colors[2]}请输入测试模型（默认gpt-3.5-turbo）,直接回车则使用默认模型{RESET}")
    model = input(f"{colors[3]}模型：{RESET}").strip() or "gpt-3.5-turbo"
    os.system('cls' if os.name == 'nt' else 'clear')
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "say this is text!"}
        ]
    }
    print(f"{colors[1]}用户调用模型：{model}{RESET}")
    try:
        start_time = time.time()
        response = requests.post(url + "/v1/chat/completions", headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"}, json=data)
        end_time = time.time()
        response_time = end_time - start_time
        if response.status_code == 200:
            response_json = response.json()
            model_name = response_json.get('model', '未知模型')
            content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '无内容')
            
            print(f"{colors[1]}实际响应模型：{model_name}{RESET}")
            print(f"{colors[1]}响应时间：{response_time:.2f} 秒{RESET}")
            print(f"{colors[1]}响应成功{RESET}")
            print(f"{colors[1]}内容：{content}{RESET}")
        else:
            print(f"{colors[0]}请求失败，状态码：{response.status_code}{RESET}")
            print(f"{colors[0]}{response.text}{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}请求时发生错误：{e}{RESET}")

def get_user_credentials():
    global url, api_key
    url = input(f"{colors[2]}请输入API URL（例如：https://api.openai.com）：{RESET}").strip()
    api_key = input(f"{colors[2]}请输入您的API Key：{RESET}").strip()

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not api_key or not url:
        get_user_credentials()
        os.system('cls' if os.name == 'nt' else 'clear')

    print(f"{colors[3]}当前API URL：{url}{RESET}")
    print(f"{colors[3]}当前API Key：{api_key}{RESET}")
    print()
    
    print(f"{colors[5]}请选择一个选项：{RESET}")
    print(f"{colors[2]}1. 获取额度{RESET}")
    print(f"{colors[3]}2. 获取模型{RESET}")
    print(f"{colors[4]}3. 模型测试{RESET}")
    print(f"{colors[0]}0. 退出{RESET}")
    
    choice = input(f"{colors[3]}请输入选项 (1/2/3/0): {RESET}")
    
    if choice == '1':
        os.system('cls' if os.name == 'nt' else 'clear')
        get_balance()
        print()
        input(f"{colors[4]}回车返回菜单！！！{RESET}")
        menu()
    elif choice == '2':
        os.system('cls' if os.name == 'nt' else 'clear')
        models = get_available_models()
        categorized_models = categorize_and_color_models(models)
        print_categorized_models(categorized_models)
        print()
        input(f"{colors[4]}回车返回菜单！！！{RESET}")
        menu()
    elif choice == '3':
        os.system('cls' if os.name == 'nt' else 'clear')
        test_model()
        print()
        input(f"{colors[4]}回车返回菜单！！！{RESET}")
        menu()
    elif choice == '0':
        os.system('cls' if os.name == 'nt' else 'clear')
        exit()
    else:
        print(f"{colors[0]}无效的选择，请重新输入。{RESET}")
        menu()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    menu()