from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

try:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[
            {
                "role": "user",
                "content": "Say hello"
            }
        ]
    )

    print(response.content[0].text)

except Exception as e:
    print(e)