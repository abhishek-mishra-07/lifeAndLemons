import gradio as gr
import os
import re
from steamship import check_environment, RuntimeEnvironments, Steamship
from steamship.invocable import post, PackageService


class MermaidGenerator(PackageService):
    @post("generate")
    def generate(self, input_text: str) -> str:
        """Generate Diagrams from plain English."""
        prompt = f"System: Using mermaid.js, create a diagram that shows the entities involved, the transactions between them, and the events that occur during the process of {input_text}. Please provide a high-level overview of the process and highlight any important decision points or outcomes. Reply only with mermaid.js code and brief description or explanation. However, you can think step-by-step. Enclose your answer with __begin__ and __end__ tag. The diagram type should be automatically selected based on the task."

        # Generate text
        task = self.client.use_plugin('gpt-4').generate(text=prompt)

        # Wait for completion of the task.
        task.wait()

        # Get the mermaid code from the response
        mermaid_code_match = re.search(r"```mermaid([\s\S]*)```", task.output.blocks[0].text)

        if mermaid_code_match:
            # Save response to file
            with open("gpt4_response.txt", "w") as f:
                f.write(task.output.blocks[0].text)

            # Generate diagram.html file from mermaid code
            mermaid_code = mermaid_code_match.group(1).strip().strip('`')
            diagram_html = f"""
                <html>
                    <head>
                        <style>
                            .mermaid {{
                                /* Remove animation */
                                /* mermaidActive 1s ease-in-out infinite */
                            }}
                        </style>
                        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                        <script>mermaid.initialize({{startOnLoad:true}});</script>
                    </head>
                    <body>
                        <div class="mermaid">
                            """ + mermaid_code + """
                        </div>
                    </body>
                </html>
                """
            with open("diagram.html", "w") as f:
                f.write(diagram_html)


            return diagram_html
        else:
            return "No diagram found in the response."

def message(input_msg):
    with Steamship.temporary_workspace() as client:
         mermaid_generator = MermaidGenerator(client)
         return mermaid_generator.generate(input_text=input_msg)


demo = gr.Interface(fn=message, inputs="text", outputs="html")
demo.launch()