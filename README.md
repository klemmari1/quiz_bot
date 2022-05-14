# quiz_bot

## How to use

1. Create a virtual environment.

2. Install requirements with `pip install -r requirements.txt`

3. Add your emails with: `python add_email.py`

    - Emails can be remoed with `python remove_latest_email.py` or `python remove_all_emails.py`

4. Start the bot: `python quiz_bot.py`

    - Use VPN with `python quiz_bot.py 1`

5. To collect the prize codes from your emails run `python claim_codes.py`. The codes will be saved in `new_codes_<datetime>.txt`
