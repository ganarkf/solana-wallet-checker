import undetected_chromedriver as uc
import json
import time
import random
from colorama import Fore
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from tabulate import tabulate

from colorama import init
init(autoreset=True)

API_URL = 'https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/'

def setup_driver():
    options = {
        'disable_extensions': True,
        'disable_gpu': True,
        'no_sandbox': True,
        'disable_setuid_sandbox': True,
        'disable_dev_shm_usage': True,
        'headless': False,
        'ignore_certificate_errors': True,
    }
    driver = webdriver.Chrome(seleniumwire_options=options)
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
        driver.header_overrides = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            'Referer': 'https://gmgn.ai/',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        driver.get(url)
        time.sleep(random.uniform(3, 7))
        
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
            all_pnl = data['data']['all_pnl'] if data['data']['all_pnl'] is not None else 0
            total_profit_pnl = data['data']['total_profit_pnl'] if data['data']['total_profit_pnl'] is not None else 0
            winrate = data['data']['winrate'] if data['data']['winrate'] is not None else 0
            realized_profit_key = 'realized_profit_30d' if period == '30d' else 'realized_profit_7d'
            realized_profit = data['data'][realized_profit_key] if data['data'][realized_profit_key] is not None else 0
            unrealized_profit = data['data']['unrealized_profit'] if data['data']['unrealized_profit'] is not None else 0
            unr_pnl = data['data']['unrealized_pnl'] if data['data']['unrealized_pnl'] is not None else 0
            buy = data['data']['buy'] if data['data']['buy'] is not None else 0
            sell = data['data']['sell'] if data['data']['sell'] is not None else 0
            ltmin50 = data['data']['pnl_lt_minus_dot5_num'] if data['data']['pnl_lt_minus_dot5_num'] is not None else 0
            min50_0 = data['data']['pnl_minus_dot5_0x_num'] if data['data']['pnl_minus_dot5_0x_num'] is not None else 0
            lt100 = data['data']['pnl_lt_2x_num'] if data['data']['pnl_lt_2x_num'] is not None else 0
            b100_400 = data['data']['pnl_2x_5x_num'] if data['data']['pnl_2x_5x_num'] is not None else 0
            gt400 = data['data']['pnl_gt_5x_num'] if data['data']['pnl_gt_5x_num'] is not None else 0
            last_active_timestamp = data['data'].get('last_active_timestamp', 0)
            last_pnl = pnl * 100
            ovrall_pnl = all_pnl * 100
            profit_pnl = total_profit_pnl * 100
            last_winrate = winrate * 100
            unrealized_pnl = unr_pnl * 100
            jp_rate = (
                ((b100_400 + gt400) / data['data']['token_num'] * 100)
                if data['data']['token_num'] not in [None, 0]
                else 0.00
            )
            minus_rate = (
                ((min50_0 + ltmin50) / data['data']['token_num'] * 100)
                if data['data']['token_num'] not in [None, 0]
                else 0.00
            )

            result = {
                'Wallet Address': wallet_address,
                'Winrate': f'{round(last_winrate, 2)}%',
                'All PnL' : f'{round(ovrall_pnl, 2)}%',
                'Profit PnL': f'{round(profit_pnl, 2)}%',
                'Rlzd PnL': f'{round(last_pnl, 2)}%',
                'Unrlzd PnL': f'{round(unrealized_pnl, 2)}%',
                'SOL': f'{float(sol_balance):.2f}',
                'Buy | Sell': f'{buy} | {sell}',
                '<0.5': f'{ltmin50}',
                '0.5-1': f'{min50_0}',
                '1-2': f'{lt100}',
                '2-5': f'{b100_400}',
                '>5': f'{gt400}',
                'JP Rate': f'{jp_rate:.2f}%',
                'Loss Rate': f'{minus_rate:.2f}%',
                'Last Active Timestamp': datetime.fromtimestamp(last_active_timestamp).strftime('%d-%m-%Y %H:%M:%S'),
                'SolScan': f'https://solscan.io/account/{wallet_address}#defiactivities',
            }
            return result
        except KeyError as e:
            print(f'ERROR: Wallet {wallet_address} not found.')
    return None

def main():
    period = get_period()
    driver = setup_driver()
    # three_days_ago = datetime.now() - timedelta(days=3)
    seven_days_ago = datetime.now() - timedelta(days=7)
    output_txt = '30d_results.txt' if period == '30d' else '7d_results.txt'
    output_json = '30d_results.json' if period == '30d' else '7d_results.json'
    walletlist = 'list.txt'
    min_winrate = 50
    min_pnl = 75
    min_buy_sell = 20 if period == '30d' else 5
    results = []

    try:
        with open(walletlist, 'r') as file:
            wallet_addresses = file.read().strip().split('\n')
        for wallet_address in wallet_addresses:
            if wallet_address.strip():
                data = fetch_wallet_data(driver, wallet_address, period)
                result = process_data(data, wallet_address, period)
                
                if datetime.fromtimestamp(data['data'].get('last_active_timestamp', 0)) < seven_days_ago:
                    print(Fore.RED + f"❌ Wallet inactive since 7 days ago ({wallet_address})")
                
                if float(result['Winrate'].replace('%', '')) < min_winrate :
                    print(Fore.YELLOW + f"Wallet has low Winrate ({wallet_address}) : {result['Winrate']}")
                else:
                    print(Fore.GREEN + f"Wallet has high Winrate ({wallet_address}) : {result['Winrate']}")
                
                if float(result['Rlzd PnL'].replace('%', '')) < min_pnl :
                    print(Fore.YELLOW + f"Wallet has low RlzdPnL ({wallet_address}) : {result['Rlzd PnL']}")
                else:
                    print(Fore.GREEN + f"Wallet has high RlzdPnL ({wallet_address}) : {result['Rlzd PnL']}")
                
                if float(result['All PnL'].replace('%', '')) < min_pnl :
                    print(Fore.YELLOW + f"Wallet has low All PnL ({wallet_address}) : {result['All PnL']}")
                else:
                    print(Fore.GREEN + f"Wallet has high All PnL ({wallet_address}) : {result['All PnL']}")
                
                if (
                    result 
                    and float(result['Winrate'].replace('%', '')) > min_winrate
                    and float(result['All PnL'].replace('%', '')) > min_pnl
                    and float(result['Rlzd PnL'].replace('%', '')) > min_pnl
                    # and float(result['Unrealized PnL'].replace('%', '')) >= 0
                    and sum(map(int, result['Buy | Sell'].split(' | '))) > min_buy_sell
                    and datetime.fromtimestamp(data['data'].get('last_active_timestamp', 0)) > seven_days_ago
                    ):
                    results.append(result)
                    print_fields = {
                        'Wallet Address': result['Wallet Address'],
                        'Winrate': result['Winrate'],
                        'All PnL': result['All PnL']
                    }
                    print(tabulate([print_fields], headers="keys", tablefmt="grid"))
                    
                    with open(output_txt, 'a') as file:
                        result_to_save = {k: v for k, v in result.items()}
                        file.write(json.dumps(result_to_save, indent=4) + '\n')
        results.sort(key=lambda x: float(x['All PnL'].replace('%', '')), reverse=True)
        with open(output_json, 'a') as json_file:
            json.dump(results, json_file)

    except FileNotFoundError:
        print("The wallet list file was not found.")
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
