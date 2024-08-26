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
language = "中文"  # 默认语言 (Default language)

# 语言映射 (Language mapping)
language_mapping = {
    "中文": {
        "menu_title": "请选择一个选项：",
        "option_1": "1. 获取额度",
        "option_2": "2. 获取模型",
        "option_3": "3. 模型测试",
        "option_4": "4. 选择语言",
        "option_0": "0. 退出",
        "enter_api_url": "请输入API URL（例如：https://api.openai.com）：",
        "enter_api_key": "请输入您的API Key：",
        "back_to_menu": "回车返回菜单！！！",
        "invalid_choice": "无效的选择，请重新输入。",
        "current_api_url": "当前API URL：",
        "current_api_key": "当前API Key：",
        "select_language": "请选择语言 (1. 中文, 2. English): ",
        "language_selected": "语言已选择：",
        "test_model_prompt": "请输入测试模型（默认gpt-3.5-turbo）,直接回车则使用默认模型",
        "model_input": "模型：",
        "user_call_model": "用户调用模型：",
        "actual_response_model": "实际响应模型：",
        "response_time": "响应时间：",
        "response_success": "响应成功",
        "response_content": "内容：",
        "request_failed": "请求失败，状态码：",
        "error_occurred": "请求时发生错误：",
        "balance_info": "当前账户余额信息：",
        "total_amount": "总额:",
        "used_amount": "已用:",
        "remaining_amount": "剩余:",
        "get_models_error": "获取模型时出错：",
        "unknown_model": "未知模型",
        "no_content": "无内容",
        "company": "公司",
        "model_list": "模型列表",
        "currency": "美元",
        "input_choice": "请输入选项 (1/2/3/4): ",
    },
    "English": {
        "menu_title": "Please select an option:",
        "option_1": "1. Get balance",
        "option_2": "2. Get models",
        "option_3": "3. Test model",
        "option_4": "4. Select language",
        "option_0": "0. Exit",
        "enter_api_url": "Please enter the API URL (e.g., https://api.openai.com):",
        "enter_api_key": "Please enter your API Key:",
        "back_to_menu": "Press Enter to return to the menu!!!",
        "invalid_choice": "Invalid choice, please re-enter.",
        "current_api_url": "Current API URL:",
        "current_api_key": "Current API Key:",
        "select_language": "Please select language (1. 中文, 2. English): ",
        "language_selected": "Language selected:",
        "test_model_prompt": "Please enter the model to test (default is gpt-3.5-turbo), press Enter to use the default model",
        "model_input": "Model:",
        "user_call_model": "User calls model:",
        "actual_response_model": "Actual response model:",
        "response_time": "Response time:",
        "response_success": "Response successful",
        "response_content": "Content:",
        "request_failed": "Request failed, status code:",
        "error_occurred": "Error occurred while requesting:",
        "balance_info": "Current account balance information:",
        "total_amount": "Total:",
        "used_amount": "Used:",
        "remaining_amount": "Remaining:",
        "get_models_error": "Error getting models:",
        "unknown_model": "Unknown Model",
        "no_content": "No Content",
        "company": "Company",
        "model_list": "Model List",
        "currency": "USD",
        "input_choice": "Please enter your choice (1/2/3/4): ",
    }
}

company_mapping = {
    "anthropic": {"中文": "Anthropic", "English": "Anthropic"},
    "openai": {"中文": "OpenAI", "English": "OpenAI"},
    "deepseek": {"中文": "DeepSeek", "English": "DeepSeek"},
    "doubao": {"中文": "豆包", "English": "Doubao"},
    "google": {"中文": "谷歌", "English": "Google"},
    "zhipu": {"中文": "智谱", "English": "Zhipu"},
    "Zhipu_4v": {"中文": "智谱", "English": "Zhipu"},
    "midjourney": {"中文": "Midjourney", "English": "Midjourney"},
    "moonshot": {"中文": "Moonshot", "English": "Moonshot"},
    "alibaba": {"中文": "阿里巴巴", "English": "Alibaba"},
    "iflytek": {"中文": "讯飞", "English": "iFlytek"},
    "baidu": {"中文": "百度", "English": "Baidu"},
    "tencent": {"中文": "腾讯", "English": "Tencent"},
    "microsoft": {"中文": "微软", "English": "Microsoft"},
    "huggingface": {"中文": "Hugging Face", "English": "Hugging Face"},
    "stabilityai": {"中文": "Stability AI", "English": "Stability AI"},
    "cohere": {"中文": "Cohere", "English": "Cohere"},
    "ai21": {"中文": "AI21 Labs", "English": "AI21 Labs"},
    "nvidia": {"中文": "NVIDIA", "English": "NVIDIA"},
    "apple": {"中文": "苹果", "English": "Apple"},
    "salesforce": {"中文": "Salesforce", "English": "Salesforce"},
    "xiaomi": {"中文": "小米", "English": "Xiaomi"},
    "meituan": {"中文": "美团", "English": "Meituan"},
    "jd": {"中文": "京东", "English": "JD"},
    "bytedance": {"中文": "字节跳动", "English": "ByteDance"},
    "facebook": {"中文": "Facebook", "English": "Facebook"},
    "amazon": {"中文": "亚马逊", "English": "Amazon"},
    "oracle": {"中文": "甲骨文", "English": "Oracle"},
    "intel": {"中文": "英特尔", "English": "Intel"},
    "qualcomm": {"中文": "高通", "English": "Qualcomm"},
    "Custom": {"中文": "其他", "English": "Custom"}
}

def generate_random_colors(num_colors):
    random.shuffle(colors)
    return colors[:num_colors]

def categorize_and_color_models(models):
    categorized_models = {}
    company_names = {company_mapping.get(model['owned_by'].lower(), {"中文": model['owned_by'], "English": model['owned_by']})[language] for model in models}
    company_colors = {company: color for company, color in zip(company_names, generate_random_colors(len(company_names)))}
    
    for model in models:
        model_name = model['id']
        owned_by = model.get('owned_by', 'unknown').lower()
        company_name = company_mapping.get(owned_by, {"中文": owned_by, "English": owned_by})[language]
        
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
    
    print(f"\033[34m{tabulate(table, headers=[language_mapping[language]['company'], language_mapping[language]['model_list']], tablefmt='grid')}{RESET}")

def get_available_models():
    try:
        response = requests.get(url + '/v1/models', headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"})
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}{language_mapping[language]['get_models_error']}{e}{RESET}")
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
    print(f"{colors[1]}{language_mapping[language]['balance_info']}{RESET}")
    print(f"{colors[2]}{language_mapping[language]['total_amount']}\t{total:.4f}{language_mapping[language]['currency']}{RESET}")
    print(f"{colors[3]}{language_mapping[language]['used_amount']}\t{total_usage:.4f}{language_mapping[language]['currency']}{RESET}")
    print(f"{colors[4]}{language_mapping[language]['remaining_amount']}\t{remaining:.4f}{language_mapping[language]['currency']}{RESET}")

def test_model():
    print(f"{colors[2]}{language_mapping[language]['test_model_prompt']}{RESET}")
    model = input(f"{colors[3]}{language_mapping[language]['model_input']}{RESET}").strip() or "gpt-3.5-turbo"
    os.system('cls' if os.name == 'nt' else 'clear')
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "say this is text!"}
        ]
    }
    print(f"{colors[1]}{language_mapping[language]['user_call_model']}{model}{RESET}")
    try:
        start_time = time.time()
        response = requests.post(url + "/v1/chat/completions", headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"}, json=data)
        end_time = time.time()
        response_time = end_time - start_time
        if response.status_code == 200:
            response_json = response.json()
            model_name = response_json.get('model', language_mapping[language]['unknown_model'])
            content = response_json.get('choices', [{}])[0].get('message', {}).get('content', language_mapping[language]['no_content'])
            
            print(f"{colors[1]}{language_mapping[language]['actual_response_model']}{model_name}{RESET}")
            print(f"{colors[1]}{language_mapping[language]['response_time']}{response_time:.2f} 秒{RESET}")
            print(f"{colors[1]}{language_mapping[language]['response_success']}{RESET}")
            print(f"{colors[1]}{language_mapping[language]['response_content']}{content}{RESET}")
        else:
            print(f"{colors[0]}{language_mapping[language]['request_failed']}{response.status_code}{RESET}")
            print(f"{colors[0]}{response.text}{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}{language_mapping[language]['error_occurred']}{e}{RESET}")

def get_user_credentials():
    global url, api_key
    url = input(f"{colors[2]}{language_mapping[language]['enter_api_url']}{RESET}").strip()
    api_key = input(f"{colors[2]}{language_mapping[language]['enter_api_key']}{RESET}").strip()

def select_language():
    global language
    print(f"{colors[2]}{language_mapping[language]['select_language']}{RESET}")
    lang_choice = input().strip()
    if lang_choice == "1":
        language = "中文"
    elif lang_choice == "2":
        language = "English"
    else:
        print(f"{colors[0]}{language_mapping[language]['invalid_choice']}{RESET}")
        select_language()
    print(f"{colors[2]}{language_mapping[language]['language_selected']}{language}{RESET}")

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not api_key or not url:
        get_user_credentials()
        os.system('cls' if os.name == 'nt' else 'clear')

    print(f"{colors[3]}{language_mapping[language]['current_api_url']}{url}{RESET}")
    print(f"{colors[3]}{language_mapping[language]['current_api_key']}{api_key}{RESET}")
    print()
    
    print(f"{colors[5]}{language_mapping[language]['menu_title']}{RESET}")
    print(f"{colors[2]}{language_mapping[language]['option_1']}{RESET}")
    print(f"{colors[3]}{language_mapping[language]['option_2']}{RESET}")
    print(f"{colors[4]}{language_mapping[language]['option_3']}{RESET}")
    print(f"{colors[4]}{language_mapping[language]['option_4']}{RESET}")
    print(f"{colors[0]}{language_mapping[language]['option_0']}{RESET}")
    
    choice = input(f"{colors[3]}{language_mapping[language]['input_choice']}{RESET}")
    
    if choice == '1':
        os.system('cls' if os.name == 'nt' else 'clear')
        get_balance()
        print()
        input(f"{colors[4]}{language_mapping[language]['back_to_menu']}{RESET}")
        menu()
    elif choice == '2':
        os.system('cls' if os.name == 'nt' else 'clear')
        models = get_available_models()
        categorized_models = categorize_and_color_models(models)
        print_categorized_models(categorized_models)
        print()
        input(f"{colors[4]}{language_mapping[language]['back_to_menu']}{RESET}")
        menu()
    elif choice == '3':
        os.system('cls' if os.name == 'nt' else 'clear')
        test_model()
        print()
        input(f"{colors[4]}{language_mapping[language]['back_to_menu']}{RESET}")
        menu()
    elif choice == '4':
        os.system('cls' if os.name == 'nt' else 'clear')
        select_language()
        menu()
    elif choice == '0':
        os.system('cls' if os.name == 'nt' else 'clear')
        exit()
    else:
        print(f"{colors[0]}{language_mapping[language]['invalid_choice']}{RESET}")
        menu()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    select_language()
    menu()