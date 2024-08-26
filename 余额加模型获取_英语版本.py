import requests
import random
import os
from tabulate import tabulate
import datetime
import time

# ANSI font color codes (foreground only)
colors = [
    '\033[31m',  # Red
    '\033[32m',  # Green
    '\033[33m',  # Yellow
    '\033[34m',  # Blue
    '\033[35m',  # Magenta
    '\033[36m',  # Cyan
    '\033[37m',  # White
    '\033[90m',  # Grey
]

RESET = '\033[0m'

api_key = None
url = None

company_mapping = {
    "anthropic": {"English": "Anthropic"},
    "openai": {"English": "OpenAI"},
    "deepseek": {"English": "DeepSeek"},
    "doubao": {"English": "Doubao"},
    "google": {"English": "Google"},
    "zhipu": {"English": "Zhipu"},
    "Zhipu_4v": {"English": "Zhipu"},
    "midjourney": {"English": "Midjourney"},
    "moonshot": {"English": "Moonshot"},
    "alibaba": {"English": "Alibaba"},
    "iflytek": {"English": "iFlytek"},
    "baidu": {"English": "Baidu"},
    "tencent": {"English": "Tencent"},
    "microsoft": {"English": "Microsoft"},
    "huggingface": {"English": "Hugging Face"},
    "stabilityai": {"English": "Stability AI"},
    "cohere": {"English": "Cohere"},
    "ai21": {"English": "AI21 Labs"},
    "nvidia": {"English": "NVIDIA"},
    "apple": {"English": "Apple"},
    "salesforce": {"English": "Salesforce"},
    "xiaomi": {"English": "Xiaomi"},
    "meituan": {"English": "Meituan"},
    "jd": {"English": "JD"},
    "bytedance": {"English": "ByteDance"},
    "facebook": {"English": "Facebook"},
    "amazon": {"English": "Amazon"},
    "oracle": {"English": "Oracle"},
    "intel": {"English": "Intel"},
    "qualcomm": {"English": "Qualcomm"},
    "Custom": {"English": "Custom"}
}

def generate_random_colors(num_colors):
    random.shuffle(colors)
    return colors[:num_colors]

def categorize_and_color_models(models):
    categorized_models = {}
    company_names = {company_mapping.get(model['owned_by'].lower(), {"English": model['owned_by']})["English"] for model in models}
    company_colors = {company: color for company, color in zip(company_names, generate_random_colors(len(company_names)))}
    
    for model in models:
        model_name = model['id']
        owned_by = model.get('owned_by', 'unknown').lower()
        company_name = company_mapping.get(owned_by, {"English": owned_by})["English"]
        
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
    
    print(f"\033[34m{tabulate(table, headers=['Company', 'Model List'], tablefmt='grid')}{RESET}")

def get_available_models():
    try:
        response = requests.get(url + '/v1/models', headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"})
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}Error getting models: {e}{RESET}")
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
    print(f"{colors[1]}Current account balance information:{RESET}")
    print(f"{colors[2]}Total:\t{total:.4f} USD{RESET}")
    print(f"{colors[3]}Used:\t{total_usage:.4f} USD{RESET}")
    print(f"{colors[4]}Remaining:\t{remaining:.4f} USD{RESET}")

def test_model():
    print(f"{colors[2]}Please enter the model to test (default is gpt-3.5-turbo), press Enter to use the default model{RESET}")
    model = input(f"{colors[3]}Model:{RESET}").strip() or "gpt-3.5-turbo"
    os.system('cls' if os.name == 'nt' else 'clear')
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "say this is text!"}
        ]
    }
    print(f"{colors[1]}User calls model: {model}{RESET}")
    try:
        start_time = time.time()
        response = requests.post(url + "/v1/chat/completions", headers={'Authorization': f'Bearer {api_key}', "Content-Type": "application/json"}, json=data)
        end_time = time.time()
        response_time = end_time - start_time
        if response.status_code == 200:
            response_json = response.json()
            model_name = response_json.get('model', 'Unknown Model')
            content = response_json.get('choices', [{}])[0].get('message', {}).get('content', 'No Content')
            
            print(f"{colors[1]}Actual response model: {model_name}{RESET}")
            print(f"{colors[1]}Response time: {response_time:.2f} seconds{RESET}")
            print(f"{colors[1]}Response successful{RESET}")
            print(f"{colors[1]}Content: {content}{RESET}")
        else:
            print(f"{colors[0]}Request failed, status code: {response.status_code}{RESET}")
            print(f"{colors[0]}{response.text}{RESET}")

    except requests.exceptions.RequestException as e:
        print(f"{colors[0]}Error occurred while requesting: {e}{RESET}")

def get_user_credentials():
    global url, api_key
    url = input(f"{colors[2]}Please enter the API URL (e.g., https://api.openai.com):{RESET}").strip()
    api_key = input(f"{colors[2]}Please enter your API Key:{RESET}").strip()

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not api_key or not url:
        get_user_credentials()
        os.system('cls' if os.name == 'nt' else 'clear')

    print(f"{colors[3]}Current API URL: {url}{RESET}")
    print(f"{colors[3]}Current API Key: {api_key}{RESET}")
    print()
    
    print(f"{colors[5]}Please select an option:{RESET}")
    print(f"{colors[2]}1. Get balance{RESET}")
    print(f"{colors[3]}2. Get models{RESET}")
    print(f"{colors[4]}3. Test model{RESET}")
    print(f"{colors[0]}0. Exit{RESET}")
    
    choice = input(f"{colors[3]}Please enter your choice (1/2/3/0): {RESET}")
    
    if choice == '1':
        os.system('cls' if os.name == 'nt' else 'clear')
        get_balance()
        print()
        input(f"{colors[4]}Press Enter to return to the menu!!!{RESET}")
        menu()
    elif choice == '2':
        os.system('cls' if os.name == 'nt' else 'clear')
        models = get_available_models()
        categorized_models = categorize_and_color_models(models)
        print_categorized_models(categorized_models)
        print()
        input(f"{colors[4]}Press Enter to return to the menu!!!{RESET}")
        menu()
    elif choice == '3':
        os.system('cls' if os.name == 'nt' else 'clear')
        test_model()
        print()
        input(f"{colors[4]}Press Enter to return to the menu!!!{RESET}")
        menu()
    elif choice == '0':
        os.system('cls' if os.name == 'nt' else 'clear')
        exit()
    else:
        print(f"{colors[0]}Invalid choice, please re-enter.{RESET}")
        menu()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    menu()