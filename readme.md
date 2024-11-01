## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/gnrkfz/solana-wallet-checker.git
   ```
   ```bash
   cd solana-wallet-checker
   ```

2. **Add Wallet Addresses**:
   Open `list.txt` and add your Solana wallet addresses, with each wallet address on a new line.
   Make sure there are no spaces after each wallet address.

3. **Set Up Chrome Version**:
   Ensure your Chrome version matches the version specified in the script. Update the `TARGET_VERSION` in `main.py` if needed.

4. **Create and Activate Virtual Environment**
   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv\Scripts\activate
   ```

5. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
