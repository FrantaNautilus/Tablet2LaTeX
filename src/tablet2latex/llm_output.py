"""
LLM output processing for Tablet2LaTeX.
"""

import pyperclip


class LLMOutputProcessor:
    """Process LLM output to extract LaTeX code."""

    @staticmethod
    def process(text: str) -> str:
        """Process the LLM output to extract only the LaTeX code.

        Args:
            text: Raw text from LLM response.

        Returns:
            Cleaned LaTeX code.
        """
        if not text or not isinstance(text, str):
            return ""
        # Remove markdown code blocks if present
        if "```" in text:
            return LLMOutputProcessor._extract_from_code_blocks(text)

        # Remove common thinking/explanation patterns
        return LLMOutputProcessor._remove_thinking(text)

    @staticmethod
    def _extract_from_code_blocks(text: str) -> str:
        """Extract content between markdown code blocks.

        Args:
            text: Raw text possibly containing markdown code blocks.

        Returns:
            Extracted content from code blocks.
        """
        parts = text.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Odd indices are inside code blocks
                # Remove language identifier if present
                stripped = part.strip()
                if not stripped:
                    return ""
                lines = stripped.split("\n")
                if lines and lines[0].lower() in ["latex", "tex"]:
                    return "\n".join(lines[1:])
                return stripped

        return text.strip()

    @staticmethod
    def _remove_thinking(text: str) -> str:
        """Remove thinking/explanation text from LLM response.

        Args:
            text: Raw text possibly containing thinking/explanation.

        Returns:
            Cleaned LaTeX code.
        """
        lines = text.split("\n")
        latex_lines: list[str] = []

        for line in lines:
            lower_line = line.lower().strip()
            # Skip lines that look like thinking or explanation
            if any(
                phrase in lower_line
                for phrase in ["let me", "i will", "here is", "the latex", "this gives"]
            ):
                continue
            # Skip empty lines at the start
            if not latex_lines and not line.strip():
                continue
            latex_lines.append(line)

        result = "\n".join(latex_lines).strip()
        return result if result else (text.strip() if text else "")

    @staticmethod
    def copy_to_clipboard(text: str):
        """Copy text to system clipboard.

        Args:
            text: Text to copy.
        """
        pyperclip.copy(text)
