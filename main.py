import undetected_chromedriver as uc
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from tabulate import tabulate

API_URL = 'https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/'

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    
    uc.TARGET_VERSION = 130

    driver = uc.Chrome(options=options, version_main=130)
    return driver

def get_period():
    print('Welcome to Solana Wallet Checker!')
    period = input('Select period : 7d/30d\n> ').strip()
    if period not in ['7d', '30d']:
        print("Invalid input. Please enter '7d' or '30d'.")
        exit()
    return period

def fetch_wallet_data(driver, wallet_address, period):
    url = f'{API_URL}{wallet_address}?period={period}'
    try:
        driver.get(url)
        time.sleep(2)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        
        page_source = driver.page_source
        start_index = page_source.find("<pre>") + 5
        end_index = page_source.find("</pre>")
        json_data = page_source[start_index:end_index]
        
        return json.loads(json_data)
    except Exception as e:
        print(f'Error fetching data for wallet {wallet_address}: {e}')
        return None

def process_data(data, wallet_address, period):
    if data:
        try:
            sol_balance = data['data']['sol_balance'] if data['data']['sol_balance'] is not None else 0
            pnl_key = 'pnl_30d' if period == '30d' else 'pnl_7d'
            pnl = data['data'][pnl_key] if data['data'][pnl_key] is not None else 0
            winrate = data['data']['winrate'] if data['data']['winrate'] is not None else 0
            realized_profit_key = 'realized_profit_30d' if period == '30d' else 'realized_profit_7d'
            realized_profit = data['data'][realized_profit_key] if data['data'][realized_profit_key] is not None else 0
            last_active_timestamp = data['data'].get('last_active_timestamp', 0)
            last_pnl = pnl * 100
            last_winrate = winrate * 100

            result = {
                'Wallet Address': wallet_address,
                'SOL Balance': f'{float(sol_balance):.2f}',
                'Winrate': f'{round(last_winrate, 2)}%',
                'AVG PnL': f'{round(last_pnl, 2)}%',
                'Realized Profit': f'{realized_profit}$',
                'Last Active Timestamp': datetime.fromtimestamp(last_active_timestamp).strftime('%d-%m-%Y %H:%M:%S'),
                'Last Active Timestamp Raw': last_active_timestamp
            }
            return result
        except KeyError as e:
            print(f'ERROR: Wallet {wallet_address} not found.')
    return None

def main():
    period = get_period()
    driver = setup_driver()
    three_days_ago = datetime.now() - timedelta(days=3)
    seven_days_ago = datetime.now() - timedelta(days=7)
    output_txt = '30d_results.txt' if period == '30d' else '7d_results.txt'
    output_json = '30d_results.json' if period == '30d' else '7d_results.json'
    results = []

    try:
        with open('list.txt', 'r') as file:
            wallet_addresses = file.read().strip().split('\n')
        for wallet_address in wallet_addresses:
            if wallet_address.strip():
                data = fetch_wallet_data(driver, wallet_address, period)
                result = process_data(data, wallet_address, period)
                
                if datetime.fromtimestamp(result['Last Active Timestamp Raw']) < seven_days_ago:
                    print(f"❌ Wallet has been inactive since 7 days ago ({wallet_address}) ❌")
                
                if float(result['Winrate'].replace('%', '')) < 25 :
                    print(f"🔴 Wallet has low Winrate ({wallet_address}) : {result['Winrate']} 🔴")
                
                if float(result['AVG PnL'].replace('%', '')) < 25 :
                    print(f"🟠 Wallet has low PnL ({wallet_address}) : {result['AVG PnL']} 🟠")
                
                if (
                    result 
                    and float(result['Winrate'].replace('%', '')) > 50 
                    and float(result['AVG PnL'].replace('%', '')) > 50
                    and datetime.fromtimestamp(result['Last Active Timestamp Raw']) > three_days_ago
                    ):
                    results.append(result)
                    print_fields = {
                        'Wallet Address': result['Wallet Address'],
                        'Winrate': result['Winrate'],
                        'AVG PnL': result['AVG PnL']
                    }
                    print(tabulate([print_fields], headers="keys", tablefmt="grid"))
                    
                    with open(output_txt, 'a') as file:
                        result_to_save = {k: v for k, v in result.items() if k != 'Last Active Timestamp Raw'}
                        file.write(json.dumps(result_to_save, indent=4) + '\n')
        with open(output_json, 'a') as json_file:
            json.dump(results, json_file)

    except FileNotFoundError:
        print("The file 'list.txt' was not found.")
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
