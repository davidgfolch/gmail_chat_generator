
import os

# Scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Credentials configuration
CREDENTIALS_DIR = 'credentials'
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, 'gmail-api-credentials.json')
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, 'token.json')

# Output directories
OUTPUT_DIR = 'md'
CACHE_DIR = 'api-response'

# Reply separators regex patterns
SEPARATORS = [
    r"On .* wrote:",  # English
    r"El .* escribió:", # Spanish
    r"Le .* a écrit :", # French
    r"Em .* escreveu:", # Portuguese
    r"Op .* schreef:", # Dutch
    r"Am .* schrieb:", # German
    r"-----Original Message-----",
    r"Sent from my iPhone",
    r"Enviado desde mi iPhone",
    r"________________________________", # Outlook and others
]

# Formatting Colors
COLOR_DATE = "#8888FF"
COLOR_SENDER = "green"
COLOR_SUBJECT = "#9370DB"
