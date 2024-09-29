# Changelog

# Changelog: v10 to v10.1

## Major Changes

1. **Default Directory Structure**
   - Implemented default input and output directories at `\data\input` and `\data\output` respectively.
   - Updated the Postprocess tab to reflect these default directories.

2. **Link Extractor Enhancement**
   - Modified the Link Extractor to save extracted links to a text file in the `\data\input` directory.
   - Enabled automatic loading of the most recent link file in the Scrape tab.

## Detailed Changes

### Link Extractor (`src/link_extractor.py`)
- Added functionality to save extracted links to a text file in `\data\input`.
- Updated the `run_extractor` method to return information about the saved file.

### Integrated App (`src/integrated_app.py`)
- Updated the Gradio interface to reflect new default directories.
- Modified the Postprocess tab to use `data/output` as both default input and output directories.

### Scraper (`src/scraper.py`)
- Enhanced the `run_scraper` method to handle cases where no file is uploaded.
- Implemented logic to use the most recent file in `\data\input` if no file is explicitly provided.
- Updated file handling to work with the new directory structure.

## User Experience Improvements

1. **Streamlined Workflow**
   - Users can now seamlessly move from link extraction to scraping without manual file handling.
   - Postprocessing now uses a consistent directory for input and output, simplifying the user workflow.

2. **Increased Automation**
   - Automatic selection of the most recent input file reduces manual intervention.
   - Direct saving of extracted links provides a more integrated experience between link extraction and scraping.

## Backend Enhancements

1. **Improved Error Handling**
   - Added more descriptive error messages for file not found and empty URL list scenarios.

2. **Logging Enhancements**
   - Expanded logging to cover new file operations and automatic file selection processes.

## Documentation Updates

- Updated README to reflect new default directory structure and enhanced workflow.
- Added explanations for the automatic file selection in the Scrape tab.

## Bug Fixes

- Resolved potential issues with file path handling across different operating systems.
- Fixed edge cases where empty input directories could cause errors.

---

This update focuses on improving the user experience by implementing a more intuitive directory structure and enhancing the integration between different components of the application. The changes make the tool more user-friendly and reduce the need for manual intervention between steps.

# Changelog: v9 to v10

## Major Changes

1. **Integrated Application Structure**
   - Created a new `IntegratedApp` class that combines Scraper, Postprocessor, and LinkExtractor functionalities.
   - Implemented a unified Gradio interface for all features.

2. **Modular Architecture**
   - Refactored the codebase into separate class-based modules for improved organization and maintainability.

3. **Configuration Management**
   - Introduced a new `ConfigManager` class to centralize configuration handling across all modules.

## New Features

1. **Link Extraction**
   - Added a new `LinkExtractor` class for extracting internal links from web pages.
   - Integrated link extraction functionality into the main application interface.

2. **Enhanced Postprocessing**
   - Improved markdown conversion with better handling of existing markdown elements.
   - Added support for generating both markdown and HTML reports.

3. **Progress Reporting**
   - Implemented a `ConversionReporter` class for detailed conversion reporting.
   - Added progress bars and status updates in the Gradio interface.

## Improvements

1. **Scraper Enhancements**
   - Refactored the scraper into a class-based structure for better organization.
   - Improved error handling and logging in the scraping process.

2. **Asynchronous Operations**
   - Enhanced asynchronous handling in both Scraper and LinkExtractor classes.
   - Implemented proper async context management for browser instances.

3. **Configuration Flexibility**
   - Added support for both YAML and JSON configuration files.
   - Implemented fallback options for configuration parameters.

4. **User Interface**
   - Created a tabbed interface in Gradio for easy access to all functionalities.
   - Improved input and output displays for each feature.

5. **Error Handling**
   - Implemented comprehensive error catching and reporting across all modules.
   - Added user-friendly error messages in the Gradio interface.

## Code Quality and Documentation

1. **Type Hinting**
   - Added type hints throughout the codebase for improved code readability and maintainability.

2. **Docstrings**
   - Added detailed docstrings to all classes and methods.

3. **Logging**
   - Implemented consistent logging across all modules.

4. **Code Style**
   - Adhered to PEP 8 style guidelines throughout the refactoring process.

## Dependencies

1. **Updated Requirements**
   - Revised `requirements.txt` to include all necessary dependencies for the integrated application.

2. **Compatibility**
   - Ensured compatibility with the latest versions of key libraries (Gradio, Playwright, BeautifulSoup, etc.).

## Testing and Debugging

1. **Module Testing**
   - Added examples for independent testing of Scraper, Postprocessor, and LinkExtractor modules.

2. **Error Scenarios**
   - Implemented handling for various error scenarios and edge cases.

## Miscellaneous

1. **File Organization**
   - Restructured the project files for better organization and modularity.

2. **Performance Optimization**
   - Implemented multi-threading in the Postprocessor for improved performance on bulk conversions.

This changelog represents a significant evolution of the project, transforming it from a collection of scripts into a cohesive, modular application with enhanced features and improved user experience.

## **v9.0.0**
- **Playwright Integration Finalized**: Completely replaced Selenium with Playwright for faster and more reliable JavaScript handling during web scraping.
- **Dynamic Content Support**: Improved handling of dynamic content such as infinite scroll and cookie banners to ensure more comprehensive content extraction.
- **Gradio Interface Enhancements**: Added a real-time progress bar and success/failure statistics in the Gradio UI, improving user experience and monitoring capabilities.
- **Data Processing with Pandas**: Incorporated Pandas to process and display scraping results, providing a summary of successes and failures.

## **v8.0.0**
- **Playwright Introduction**: Introduced Playwright as an alternative to Selenium for better performance when handling JavaScript-heavy pages.
- **Enhanced File Handling**: Improved file-saving methods, ensuring unique filenames for dynamic URLs and better handling of query parameters.
- **User Feedback Improvements**: Further enhancements to the Gradio interface, allowing better real-time feedback and monitoring during scraping tasks.
- **JavaScript Detection**: Added functionality to log and handle pages requiring JavaScript, skipping them when necessary.

## **v7.0.0**
- **Selenium Improvements**: Enhanced Selenium’s ability to interact with pages requiring JavaScript, including handling infinite scroll to ensure all content is fully loaded.
- **Clean HTML Extraction**: Improved the `clean_html()` function by including removal of non-essential HTML elements like headers, footers, and navigation menus.
- **Gradio UI Introduced**: Integrated Gradio to provide a graphical interface for starting the scraper and viewing results, with options for user uploads.

## **v6.0.0**
- **Selenium with Threading**: Implemented multi-threaded execution using `ThreadPoolExecutor` alongside Selenium for faster scraping of JavaScript-heavy websites.
- **Optimized Gradio Interface**: Further refined the Gradio interface with better scraping options for users.
- **Performance Upgrades**: Added random delays between requests to reduce server load and mimic human browsing patterns.

## **v5.0.0**
- **Selenium Integration**: Initial integration of Selenium for scraping JavaScript-rendered pages, providing a foundation for scraping modern web pages.
- **Rate Limiting with AsyncLimiter**: Introduced rate limiting to ensure requests are spaced out properly, preventing overload on target websites.
- **Retry Logic with Backoff**: Implemented retry logic using exponential backoff to handle transient network errors more gracefully.
- **Gradio Interface**: Added the first version of the Gradio web interface to launch scraping tasks through a browser-based interface.

## **v4.0.0**
- **HTML Content Cleaning**: Introduced a more sophisticated `clean_html()` function, which removes unnecessary HTML elements (e.g., scripts, styles) from the scraped content.
- **Filename Generation Improvements**: Enhanced the `generate_filename()` function to handle complex URL paths and query parameters, using hashing for uniqueness.
- **Improved Error Handling**: Better error reporting and retry mechanisms for handling request failures more effectively.

## **v3.0.0**
- **Logging and Output**: Reduced logging verbosity to `INFO` to focus on key events like progress and errors.
- **Rich Library Integration**: Introduced the use of the `rich` library for better logging and output formatting, providing clearer progress updates and summaries.
- **Retry Mechanism**: Added retry logic with exponential backoff to handle network issues and transient failures.

## **v2.0.0**
- **Basic Scraper Implementation**: Initial release of the scraper with asynchronous URL fetching using `aiohttp` and basic HTML cleaning.
- **Concurrency and Rate Limiting**: Added basic concurrency control and rate limiting with `AsyncLimiter` to prevent overwhelming servers.
- **File Saving Mechanism**: Implemented functionality to save cleaned text content into files, ensuring the filenames are sanitized based on URL paths.