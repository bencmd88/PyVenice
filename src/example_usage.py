"""
Example usage of the pyvenice Venice.ai API client library.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path to find the pyvenice package
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyvenice import VeniceClient, ChatCompletion, ImageGeneration, Models

# Initialize client - requires VENICE_API_KEY environment variable
client = VeniceClient()

def example_chat():
    """Example of using chat completions."""
    chat = ChatCompletion(client)
    
    # Simple chat
    response = chat.create(
        model="venice-uncensored",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    
    print("Chat Response:", response.choices[0].message['content'])
    
    # Chat with web search
    response = chat.create_with_web_search(
        model="venice-uncensored",
        messages=[{"role": "user", "content": "What's the latest news about AI?"}],
        search_mode="auto"
    )
    
    print("\nChat with Web Search:", response.choices[0].message['content'])


def example_models():
    """Example of listing models and checking capabilities."""
    models = Models(client)
    
    # List all text models
    text_models = models.list(type="text")
    print("\nAvailable Text Models:")
    for model in text_models.data[:5]:  # Show first 5
        print(f"- {model.id}: {model.model_spec.description}")
    
    # Check model capabilities
    model_id = "venice-uncensored"
    capabilities = models.get_capabilities(model_id)
    if capabilities:
        print(f"\n{model_id} capabilities:")
        print(f"- Supports function calling: {capabilities.supportsFunctionCalling}")
        print(f"- Supports web search: {capabilities.supportsWebSearch}")
        print(f"- Supports vision: {capabilities.supportsVision}")


def example_image_generation():
    """Example of generating images."""
    image_gen = ImageGeneration(client)
    
    # List available styles
    styles = image_gen.list_styles()
    print("\nAvailable Image Styles:", styles[:5])  # Show first 5
    
    # Generate an image
    response = image_gen.generate(
        prompt="A serene mountain landscape at sunset",
        model="venice-sd35",
        style_preset="Cinematic",
        width=1024,
        height=1024
    )
    
    print(f"\nGenerated image ID: {response.id}")
    print(f"Number of images: {len(response.images)}")
    
    # Save image to file (base64 decoded)
    if response.images:
        import base64
        image_data = base64.b64decode(response.images[0])
        with open("generated_image.webp", "wb") as f:
            f.write(image_data)
        print("Image saved as generated_image.webp")

def multiple_images():
    image_gen = ImageGeneration(client)
    
    styles = image_gen.list_styles()
    
    for style in styles:
        response = image_gen.generate(
            prompt="A battle-scarred veteran soldier wearing a suit of nanotech body armour in a desert setting",
            model="flux-dev",
            style_preset=style,
            width=1024,
            height=1024
        )
    
        if response.images:
            import base64
            image_data = base64.b64decode(response.images[0])
            with open(f"image_{style}.webp", "wb") as f:
                f.write(image_data)
            print(f"image_{style}.webp generated.")

def example_streaming():
    """Example of streaming chat responses."""
    chat = ChatCompletion(client)
    
    print("\nStreaming response:")
    stream = chat.create(
        model="venice-uncensored",
        messages=[{"role": "user", "content": "Write a short poem about coding"}],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices and chunk.choices[0].get('delta', {}).get('content'):
            print(chunk.choices[0]['delta']['content'], end='', flush=True)
    print()  # New line at end

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("VENICE_API_KEY"):
        print("Please set VENICE_API_KEY environment variable")
        exit(1)
    
    print("=== Venice.ai API Examples ===\n")
    
    try:
        multiple_images()
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Clean up
        client.close()