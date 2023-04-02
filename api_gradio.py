import gradio as gr
import os
import re
from steamship import check_environment, RuntimeEnvironments, Steamship
from steamship.invocable import post, PackageService


class LemonToFeature(PackageService):
    @post("convert")
    def convert(self, input_text: str) -> str:
        """Convert criticism or roast into potential feature, test, or use case."""
        prompt = f"System: Convert the following criticism or roast into potential features, tests, or use cases: {input_text}. Reply with a list of potential features, tests, or use cases. Enclose your answer with __begin__ and __end__ tag."

        # Generate text
        task = self.client.use_plugin('gpt-4').generate(text=prompt)

        # Wait for completion of the task.
        task.wait()

        # Get the response from the GPT4 plugin
        response_match = re.search(r"__begin__([\s\S]*)__end__", task.output.blocks[0].text)

        if response_match:
            # Save response to file
            with open("gpt4_response.txt", "w") as f:
                f.write(task.output.blocks[0].text)

            # Return the potential features, tests, or use cases
            return response_match.group(1).strip()
        else:
            return "No potential features, tests, or use cases found in the response."


def convert(input_msg):
    with Steamship.temporary_workspace() as client:
         lemon_converter = LemonToFeature(client)
         return lemon_converter.convert(input_text=input_msg)


demo = gr.Interface(fn=convert, inputs="text", outputs="text")
demo.launch()