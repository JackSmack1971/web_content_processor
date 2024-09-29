import os
import re
from typing import List, Iterator, Dict, Optional, Tuple, Callable, Any
from pathlib import Path
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import gradio as gr
from src.config_manager import ConfigManager

class Postprocessor:
    """Handles postprocessing of scraped content."""

    def __init__(self, config: ConfigManager):
        """
        Initialize the Postprocessor.

        Args:
            config (ConfigManager): Configuration manager instance.
        """
        self.config = config
        self.setup_logging()
        self.reporter = ConversionReporter()

    def setup_logging(self):
        """Set up logging for the postprocessor."""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                            filename='logs/postprocessor.log')
        self.logger = logging.getLogger(__name__)

    def document_to_markdown(self, input_text: str, progress_callback: Callable[[int, int], None]) -> str:
        """Convert a text document to markdown format."""
        markdown_content = []
        bullet_point_pattern = re.compile(r"^\s*[-*+]\s+.*")
        numbered_list_pattern = re.compile(r"^\s*\d+\.\s+.*")
        code_block_pattern = re.compile(r"^\s*\$.*")

        lines = input_text.splitlines()
        total_lines = len(lines)
        inside_code_block = False
        current_indentation_level = 0

        for idx, line in enumerate(lines):
            if not line.strip():
                markdown_content.append("\n")
                continue

            if self.detect_existing_markdown(line):
                markdown_content.append(self.preserve_markdown(line))
                continue

            if code_block_pattern.match(line):
                if not inside_code_block:
                    markdown_content.append("```\n")
                    inside_code_block = True
                markdown_content.append(f"{line.strip()}\n")
            elif inside_code_block:
                markdown_content.append("```\n\n")
                inside_code_block = False
            elif bullet_point_pattern.match(line):
                current_indentation_level = len(line) - len(line.lstrip())
                markdown_content.append(self.format_bullet_point(line, current_indentation_level // 2))
            elif numbered_list_pattern.match(line):
                current_indentation_level = len(line) - len(line.lstrip())
                markdown_content.append(self.format_bullet_point(line, current_indentation_level // 2, is_numbered=True))
            else:
                markdown_content.append(f"{line.strip()}\n\n")

            if idx % self.config.get('PROGRESS_UPDATE_FREQUENCY', 10) == 0:
                progress_callback(idx + 1, total_lines)

        return ''.join(markdown_content)

    @staticmethod
    def detect_existing_markdown(line: str) -> bool:
        """Detect if a line is already a valid markdown element."""
        markdown_patterns = [
            r"^\s*#+\s+.*",  # Headings
            r"^\s*[-*+]\s+.*",  # Bullet points
            r"^\s*\d+\.\s+.*",  # Numbered lists
            r"^\s*>.*",  # Blockquotes
            r"^\s*```",  # Code block start/end
            r"^\s*`[^`]+`",  # Inline code
            r"^\s*\[.*\]\(.*\)",  # Links
            r"^\s*\*\*[^*]+\*\*",  # Bold
            r"^\s*\*[^*]+\*",  # Italic
        ]
        return any(re.match(pattern, line) for pattern in markdown_patterns)

    @staticmethod
    def preserve_markdown(line: str) -> str:
        """Preserve existing markdown formatting."""
        return line + "\n"

    @staticmethod
    def format_bullet_point(line: str, indent_level: int, is_numbered: bool = False) -> str:
        """Format a bullet point or numbered list item with proper indentation."""
        indent = "  " * indent_level
        if is_numbered:
            return f"{indent}{line.strip()}\n"
        return f"{indent}- {line.strip()[1:]}\n"

    def process_file(self, text_file: Path, output_directory: Path, progress_callback: Callable[[int, int], None]) -> Tuple[Path, Optional[str]]:
        """Process a single text file and convert it to markdown."""
        try:
            if text_file.stat().st_size > self.config.get('MAX_FILE_SIZE', 10 * 1024 * 1024):
                self.logger.warning(f"Skipping {text_file} due to file size.")
                return text_file, f"File too large (>{self.config.get('MAX_FILE_SIZE')} bytes)"

            self.logger.info(f"Processing file: {text_file}")
            with open(text_file, "r", encoding="utf-8") as file:
                input_text = file.read()

            markdown_output = self.document_to_markdown(input_text, progress_callback)

            output_file = output_directory / text_file.with_suffix('.md').name
            with open(output_file, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_output)

            self.logger.info(f"Markdown file '{output_file}' created successfully.")
            return text_file, None
        except Exception as e:
            self.logger.error(f"Error processing file {text_file}: {str(e)}")
            return text_file, str(e)

    def convert_files(self, input_directory: str, output_directory: str, progress=gr.Progress()) -> str:
        """Convert multiple files from text to markdown."""
        input_path = Path(input_directory)
        output_path = Path(output_directory)
        
        if not input_path.is_dir():
            return "Error: Input directory does not exist."
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        supported_files = [f for f in input_path.rglob('*') if f.suffix in self.config.get('SUPPORTED_FILE_TYPES', ['.txt'])]
        
        if not supported_files:
            return "No supported files found in the input directory."
        
        total_files = len(supported_files)
        progress(0, desc="Initializing...")
        
        with ThreadPoolExecutor(max_workers=self.config.get('MAX_WORKERS', 4)) as executor:
            futures = [executor.submit(self.process_file, text_file, output_path, 
                                       lambda current, total, file=text_file: progress((current / total) / total_files + (supported_files.index(file) / total_files), 
                                                                                      desc=f"Processing {file.name}")) 
                       for text_file in supported_files]
            
            for future in as_completed(futures):
                result = future.result()
                if result[1] is None:
                    self.reporter.log_success(result[0])
                else:
                    self.reporter.log_failure(result[0], result[1])
        
        report = self.reporter.generate_report(self.config.get('report_format', 'markdown'))
        report_path = output_path / "conversion_report.md"
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(report)
        
        return f"Conversion completed. Report saved to {report_path}"

class ConversionReporter:
    """Handles reporting for the conversion process."""

    def __init__(self):
        """Initialize the ConversionReporter."""
        self.processed_files: List[str] = []
        self.failed_files: Dict[str, str] = {}
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None

    def log_success(self, file_path: Path) -> None:
        """Log a successfully processed file."""
        self.processed_files.append(str(file_path))

    def log_failure(self, file_path: Path, error: str) -> None:
        """Log a file that failed to process."""
        self.failed_files[str(file_path)] = error

    def generate_report(self, format: str = 'markdown') -> str:
        """Generate a conversion report in the specified format."""
        self.end_time = datetime.now()
        total_files = len(self.processed_files) + len(self.failed_files)
        duration = self.end_time - self.start_time

        if format.lower() == 'html':
            return self._generate_html_report(total_files, duration)
        return self._generate_markdown_report(total_files, duration)

    def _generate_report_common(self, total_files: int, duration: datetime) -> Dict[str, str]:
        """Generate common report data for both Markdown and HTML formats."""
        return {
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "duration": str(duration),
            "total_files": str(total_files),
            "successful_conversions": str(len(self.processed_files)),
            "failed_conversions": str(len(self.failed_files)),
        }

    def _generate_markdown_report(self, total_files: int, duration: datetime) -> str:
        """Generate a markdown report."""
        common_data = self._generate_report_common(total_files, duration)
        report = [
            f"# Conversion Report\n",
            f"**Start Time:** {common_data['start_time']}\n",
            f"**End Time:** {common_data['end_time']}\n",
            f"**Duration:** {common_data['duration']}\n",
            f"**Total Files Processed:** {common_data['total_files']}\n",
            f"**Successful Conversions:** {common_data['successful_conversions']}\n",
            f"**Failed Conversions:** {common_data['failed_conversions']}\n",
        ]

        if self.processed_files:
            report.append("\n## Successfully Converted Files\n")
            for file in self.processed_files:
                report.append(f"- {file}\n")

        if self.failed_files:
            report.append("\n## Failed Files\n")
            for file, error in self.failed_files.items():
                report.append(f"- {file}: {error}\n")

        return ''.join(report)

    def _generate_html_report(self, total_files: int, duration: datetime) -> str:
        """Generate an HTML report."""
        common_data = self._generate_report_common(total_files, duration)
        report = [
            f"<h1>Conversion Report</h1>",
            f"<p><strong>Start Time:</strong> {common_data['start_time']}</p>",
            f"<p><strong>End Time:</strong> {common_data['end_time']}</p>",
            f"<p><strong>Duration:</strong> {common_data['duration']}</p>",
            f"<p><strong>Total Files Processed:</strong> {common_data['total_files']}</p>",
            f"<p><strong>Successful Conversions:</strong> {common_data['successful_conversions']}</p>",
            f"<p><strong>Failed Conversions:</strong> {common_data['failed_conversions']}</p>",
        ]

        if self.processed_files:
            report.append("<h2>Successfully Converted Files</h2><ul>")
            for file in self.processed_files:
                report.append(f"<li>{file}</li>")
            report.append("</ul>")

        if self.failed_files:
            report.append("<h2>Failed Files</h2><ul>")
            for file, error in self.failed_files.items():
                report.append(f"<li>{file}: {error}</li>")
            report.append("</ul>")

        return ''.join(report)