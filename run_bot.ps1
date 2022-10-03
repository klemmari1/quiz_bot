Scripts/activate
$emails = python show_unused_emails_today.py
while($emails -ne "[]"){
  python quiz_bot.py
  $emails = python show_unused_emails_today.py
}
