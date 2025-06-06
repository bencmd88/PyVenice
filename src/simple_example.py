#!/usr/bin/env python3
"""
Simple example showing how to use the pyvenice library.
"""

import os
from pyvenice import VeniceClient, ChatCompletion, Models, ImageGeneration


def multiple_images():
    """Generate multiple images using different styles."""
    client = VeniceClient()
    image_gen = ImageGeneration(client)

    styles = image_gen.list_styles()

    for style in styles:
        response = image_gen.generate(
            prompt="A battle-scarred veteran soldier wearing a suit of nanotech body armour in a desert setting",
            model="flux-dev",
            style_preset=style,
            width=1024,
            height=1024,
        )

        if response.images:
            import base64

            image_data = base64.b64decode(response.images[0])
            with open(f"image_{style}.webp", "wb") as f:
                f.write(image_data)
            print(f"image_{style}.webp generated.")


def main():
    # Check for API key
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("VENICE_API_KEY environment variable not set!")
        print("\nTo use this example:")
        print("1. Get your API key from Venice.ai")
        print("2. Set it as an environment variable:")
        print("   export VENICE_API_KEY='your-api-key-here'")
        print("3. Run this script again")
        print("\nUsing a test key for demonstration (will likely fail)...")
        api_key = "test-api-key-12345"

    print("Initializing Venice.ai client...")

    try:
        # Initialize client
        client = VeniceClient(api_key=api_key)

        # List available models
        print("\nFetching available models...")
        models = Models(client)
        model_list = models.list(type="text")

        print(f"\nFound {len(model_list.data)} text models. Here are the first 5:")
        for model in model_list.data[:5]:
            print(f"  - {model.id}")

        # Simple chat example
        print("\nTesting chat completion...")
        chat = ChatCompletion(client)

        response = chat.create(
            model="venice-uncensored",
            messages=[{"role": "user", "content": "Say 'Hello, World!' in Python"}],
        )

        print("\nChat response:")
        print(response.choices[0].message["content"])

    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}: {e}")
        print(
            "\nMake sure your API key is valid and you have access to the Venice.ai API."
        )
        import traceback

        traceback.print_exc()
    finally:
        if "client" in locals():
            client.close()
            print("\nClient closed.")


if __name__ == "__main__":
    main()
