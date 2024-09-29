import gradio as gr
from src.config_manager import ConfigManager
from src.scraper import Scraper
from src.postprocessor import Postprocessor
from src.link_extractor import LinkExtractor
import logging

class IntegratedApp:
    """Integrated application combining scraping, postprocessing, and link extraction."""

    def __init__(self):
        """Initialize the IntegratedApp."""
        self.config = ConfigManager('configs/config.yaml')
        self.scraper = Scraper(self.config)
        self.postprocessor = Postprocessor(self.config)
        self.link_extractor = LinkExtractor(self.config)
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the integrated application."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                            filename='logs/integrated_app.log')
        self.logger = logging.getLogger(__name__)

    def create_interface(self):
        """Create the Gradio interface for the integrated application."""
        with gr.Blocks() as demo:
            gr.Markdown("# Web Content Processing Tool")
            
            with gr.Tab("Scrape"):
                scrape_input = gr.File(label="Upload URLs File", file_types=[".txt"], file_count="single")
                scrape_button = gr.Button("Start Scraping")
                scrape_output = gr.DataFrame(label="Scraping Results")
                scrape_info = gr.Markdown()

            with gr.Tab("Extract Links"):
                link_input = gr.Textbox(label="Enter URL")
                link_button = gr.Button("Extract Links")
                link_output = gr.DataFrame(label="Extracted Links")
                link_info = gr.Markdown()

            with gr.Tab("Postprocess"):
                postprocess_input = gr.Textbox(label="Input Directory", value="data/output")
                postprocess_output = gr.Textbox(label="Output Directory", value="data/output")
                postprocess_button = gr.Button("Convert to Markdown")
                postprocess_info = gr.Markdown()

            scrape_button.click(
                self.scraper.run_scraper,
                inputs=[scrape_input],
                outputs=[scrape_output, scrape_info]
            )

            link_button.click(
                self.link_extractor.run_extractor,
                inputs=[link_input],
                outputs=[link_output, link_info]
            )

            postprocess_button.click(
                self.postprocessor.convert_files,
                inputs=[postprocess_input, postprocess_output],
                outputs=[postprocess_info]
            )

        return demo

    def run(self):
        """Run the integrated application."""
        demo = self.create_interface()
        demo.launch()

if __name__ == "__main__":
    app = IntegratedApp()
    app.run()