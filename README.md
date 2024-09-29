# Web Content Processor

Web Content Processor is an integrated tool for web scraping, link extraction, and content postprocessing. It provides a user-friendly interface for various web content management tasks.

## Features

- **Web Scraping**: Extract content from websites with advanced scrolling and JavaScript handling.
- **Link Extraction**: Retrieve internal links from web pages.
- **Content Postprocessing**: Convert scraped content to Markdown format.
- **User-friendly Interface**: Easy-to-use Gradio-based web interface.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/web_content_processor.git
   cd web_content_processor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Install the project in editable mode:
   ```
   pip install -e .
   ```

## Usage

To start the Web Content Processor, run:

```
python main.py
```

This will launch the Gradio interface in your default web browser. The interface consists of three main tabs:

1. **Scrape**: Upload a file containing URLs to scrape content from multiple web pages.
2. **Extract Links**: Enter a URL to extract all internal links from that web page.
3. **Postprocess**: Convert scraped content from text format to Markdown.

## Configuration

You can customize the behavior of the Web Content Processor by modifying the configuration files:

- `configs/config.yaml`: YAML format configuration
- `configs/config.json`: JSON format configuration

These files allow you to adjust settings such as:

- Maximum number of worker threads
- User agent string for web requests
- Scrolling behavior for web scraping
- Supported file types for postprocessing
- And more...

## Project Structure

```
web_content_processor/
│
├── src/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── scraper.py
│   ├── postprocessor.py
│   ├── link_extractor.py
│   └── integrated_app.py
│
├── tests/
│   ├── __init__.py
│   ├── test_config_manager.py
│   ├── test_scraper.py
│   ├── test_postprocessor.py
│   ├── test_link_extractor.py
│   └── test_integrated_app.py
│
├── configs/
│   ├── config.yaml
│   └── config.json
│
├── data/
│   ├── input/
│   └── output/
│
├── logs/
│   └── app.log
│
├── docs/
│   └── README.md
│
├── requirements.txt
├── setup.py
└── main.py
```

## Development

To contribute to the Web Content Processor, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Write your code and tests.
4. Run the tests to ensure everything is working:
   ```
   python -m unittest discover tests
   ```
5. Submit a pull request with your changes.

## Testing

To run the test suite, execute:

```
python -m unittest discover tests
```

## Logging

Logs are stored in the `logs/` directory. The main application log file is `app.log`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Gradio](https://www.gradio.app/) for the web interface framework.
- [Playwright](https://playwright.dev/) for web automation and scraping.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing.

## Contact

For any queries or suggestions, please open an issue on the GitHub repository or contact the maintainers directly.

---

Happy web content processing!
