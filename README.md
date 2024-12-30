## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ganarkf/solana-wallet-checker.git
   ```
   ```bash
   cd solana-wallet-checker
   ```

3. **Add Wallet Addresses**

   Open `list.txt` and add your Solana wallet addresses, with each wallet address on a new line.
   Make sure there are no spaces after each wallet address.

4. **Set Up Chrome Version**

   Ensure your Chrome version matches the version specified in the script. Update the `TARGET_VERSION` in `main.py` if needed.

5. **Create and Activate Virtual Environment**

   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv\Scripts\activate
   ```

6. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Note

You can explore the response from the GMGN API to process the wallet further

Also check my other repo : 
<br />["Solana Wallet Generator"](https://github.com/ganarkf/sol-wallet-generator)
<br />["DS Top Traders"](https://github.com/ganarkf/ds-top-traders)

