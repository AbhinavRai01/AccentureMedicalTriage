import re

with open('patienttriage/ui/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Emoji removal using the emoji library, or a regex for standard emojis.
# Actually, since there are greek letters like α, β, and ° in the text:
# st.success(" Geriatric Agent (65+): α = 23.0")
# "Body Temperature (°C)"

import emoji
content_no_emoji = emoji.replace_emoji(content, replace='')

# clean up some extra spaces left by emoji removal
content_no_emoji = content_no_emoji.replace('  ', ' ')
content_no_emoji = content_no_emoji.replace(' )', ')')
content_no_emoji = content_no_emoji.replace('[ ', '[')

with open('patienttriage/ui/app.py', 'w', encoding='utf-8') as f:
    f.write(content_no_emoji)
