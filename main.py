from ui.gradio_app import interface, custom_css
import gradio as gr

if __name__ == "__main__":
    print("[Starting EvoHive...]")
    print("Check: Ollama must be running.")
    
    # Use 0.0.0.0 to allow access from local network/docker
    interface.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        share=True,
        css=custom_css,
        theme=gr.themes.Default()
    )