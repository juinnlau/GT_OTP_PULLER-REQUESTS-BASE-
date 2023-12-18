import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
try:
    import imaplib
    import email
    import discord
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    # Install missing modules
    import os
    os.system("pip install imaplib")
    os.system("pip install discord")
    os.system("pip install beautifulsoup4")


intents = discord.Intents.all()
intents.messages = True  

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='aap')
async def aap(ctx, credentials: str):
    # Split the credentials using the specified delimiter
    delimiter_options = ["|", ":"]

    for delimiter in delimiter_options:
        if delimiter in credentials:
            email_user, email_password = credentials.split(delimiter, 1)
            break
    else:
        await ctx.send(f"Invalid format. Please use {delimiter_options} to separate email and password.")
        return

    # Connect to Outlook.com's IMAP server
    await ctx.send("Logging In... Please Wait!")
    mail = imaplib.IMAP4_SSL("outlook.office365.com")

    try:
        mail.login(email_user, email_password)

        mail.select("inbox")
        status, messages = mail.search(None, 'SUBJECT "Growtopia New Account Verification"')

        email_ids = messages[0].split()

        if not email_ids:
            await ctx.send("No emails with the subject 'Growtopia Game' found.")
            raise Exception("No emails with the subject 'Growtopia Game' found.")

        # Assuming you want to retrieve the latest email found
        latest_email_id = email_ids[-1]

        # Fetch the email data
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract the subject and body
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        # Print the email details
        print(f"Subject: {subject}")
        print("From:", msg.get("From"))
        print("To:", msg.get("To"))
        print("Date:", msg.get("Date"))

        user_mention = ctx.author.mention  
        await ctx.send(f"{user_mention} Date%Time: {msg.get('Date')}")

        # Get the email body
        email_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body += part.get_payload(decode=True).decode("utf-8")
        else:
            email_body = msg.get_payload(decode=True).decode("utf-8")


        soup = BeautifulSoup(email_body, "html.parser")


        # Extract href from the <a> tag
        a_tag = soup.find("a", class_="mcnButton")
        if a_tag:
            href = a_tag.get("href")
            print("Href:", href)
            await ctx.send(f"Href: {href}")

        # Extract the number between <strong> tags in <span>
        span_tag = soup.find("span", style="font-size:24px")
        if span_tag:
            number = span_tag.strong.text
            print("Number:", number)
            await ctx.send(f"OTP: {number}")


    except Exception as e:
        print(f"An error occurred: {str(e)}")
        user_mention = ctx.author.mention 
        await ctx.send(f"{user_mention} An error occurred: {str(e)}")
    finally:
        mail.logout()

bot.run('')# Replace this with your Exact token
