import requests
import time
import random


# PASTE YOUR FULL LIST BELOW

raw_data = """
1,"1Q3rjGgAXrYqnPXJVN48L24nmtkCSC5vNV","KyaUiiQksYuu1NmpFPBpR2AqxfxMaCJsMF3EFpYvDfR9TPp5rARh"
2,"198cagRaPCYNWyECgmtkUNZcghV7rzNoH9","L24bbr6sK3c37MNkYCadD9PzdcQRyX5gpj886t6Swf7SVyE3ErBV"
3,"1P6WsrACb621G1p5aRhPBeYE9Cidp3Zx41","L4Q3KgU4diWycqUcFvRWuJyfTeQqj7temwrZnSLhcNufUyohFZT2"
4,"14NHdY3CqnoMDeXSsU6UgRH5XVbMpvRocr","KyD9yCiCJmEsmk3tccHN7Fdan6JgbXY8qn1Txrc6TDAHXpLbs7wg"
5,"1LbtQp86WTRpuo7XgHCiZNPTG2WT7wwMVL","Kzy2pLuEnmxZkKapvJkUj1dGadHAT29uwapDoct75B7DjxnM4yBY"
6,"1CDRxfGgkyaYX9Ven5aCRkaqzADSdnenT4","Kz5QS3EUzftbvyATA7QsC9QUgDYs2W6VKKWfYzdELrRL4hUsthbT"
7,"15BUcWARSeoUM4bv8WSApCtWMZgKtVLhEL","L14Yuc3koNoKTvnWygmJweX3YkKqhZkt7QvYQ5izBMefQzqvhsCw"
8,"1MrCaSpEvDoHniTA2M3MxqbiRCKNnuy8b5","KzTmsiywYhqoWArPFnz8dmiCzXRqpCvQszgRtNMWtbucWpkATzy1"
9,"1L5nkv55Bz71WwEpoj2aiMRRUfZH2Gpofu","L34Exin9gYFFAon52ah6jV3RbLhJfsfcBsBLrMbZBTYJSfCipnbU"
10,"1Eg9N4PofVxFcsy7zbCEdiqusAf5QMP33G","L2XaWAvJWcFjAYvaDBzqhimM9cYLXW9fzcHAhbH6XQjcwwg7vYry"
"""

# u can add more entries to raw_data as needed
class HydraChecker:
    def __init__(self):
        self.api_sources = [
            "mempool",      
            "blockstream",  
            "blockchain"    
        ]

    def get_btc_balance(self, address):
        random.shuffle(self.api_sources) 
        for source in self.api_sources:
            try:
                if source == "mempool":
                    url = f"https://mempool.space/api/address/{address}"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        return (data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']) / 100_000_000
                elif source == "blockstream":
                    url = f"https://blockstream.info/api/address/{address}"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        return (data['chain_stats']['funded_txo_sum'] - data['chain_stats']['spent_txo_sum']) / 100_000_000
                elif source == "blockchain":
                    url = f"https://blockchain.info/q/addressbalance/{address}"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        return int(r.text) / 100_000_000
            except:
                continue
        return 0.0

    def check_bch_balance(self, address):
        try:
            url = f"https://api.blockchair.com/bitcoin-cash/dashboards/address/{address}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return data['data'][address]['address']['balance'] / 100_000_000
        except:
            return 0.0
        return 0.0

def run_ultimate_scan(data):
    checker = HydraChecker()
    lines = data.strip().split('\n')
    
    # This list will store the IDs of any wallet with money
    flagged_wallets = []

    print(f"\n{'ID':<4} | {'Address':<35} | {'BTC':<12} | {'BCH':<10}")
    print("=" * 75)
    
    for line in lines:
        if not line.strip(): continue
        try:
            parts = line.split(',')
            w_id = parts[0]
            public_addr = parts[1].replace('"', '').strip()
            
            # Check Balances
            btc_bal = checker.get_btc_balance(public_addr)
            bch_bal = checker.check_bch_balance(public_addr)
            
            if btc_bal > 0 or bch_bal > 0:
                print(f"💰 i like moneu! {w_id:<4} | {public_addr:<35} | {btc_bal:.6f} | {bch_bal:.6f} there u go be ricj")
                
                flagged_wallets.append(f"ID #{w_id} (BTC: {btc_bal}, BCH: {bch_bal})")
                
                with open("found_money.txt", "a") as f:
                    f.write(f"ID: {w_id} | {public_addr} | BTC:{btc_bal} | BCH:{bch_bal}\n")
            else:
                print(f"{w_id:<4} | {public_addr:<35} | {btc_bal:.6f} BTC | {bch_bal:.6f} BCH")
            
            time.sleep(0.3) # Fast rotation
            
        except Exception as e:
            print(f"Skipping line: {e}")

    print("\n" + "="*40)
    print("            RESULTS           ")
    print("="*40)
    
    if len(flagged_wallets) > 0:
        print(f"TOTAL WALLETS WITH FUNDS: {len(flagged_wallets)}")
        print("Here are the IDs you need to check:")
        for wallet_info in flagged_wallets:
            print(f" -> {wallet_info}")
    else:
        print("Scan Complete. ur still broke")
        
    print("="*40)

if __name__ == "__main__":
    run_ultimate_scan(raw_data)