"""
Unit tests for the LLMOutputProcessor class.
"""

from unittest.mock import MagicMock, patch

import pytest

from tablet2latex.llm_output import LLMOutputProcessor


class TestProcessMethod:
    """Tests for LLMOutputProcessor.process method."""

    def test_process_plain_latex(self):
        """Test processing plain LaTeX without markdown."""
        input_text = r"\frac{a}{b} + c = d"
        result = LLMOutputProcessor.process(input_text)
        assert result == input_text

    def test_process_latex_with_code_block(self):
        """Test extracting LaTeX from markdown code block."""
        input_text = "Here is your LaTeX:\n```latex\n\\frac{a}{b}\n```\n"
        result = LLMOutputProcessor.process(input_text)
        assert result.strip() == "\\frac{a}{b}"

    def test_process_latex_with_tex_code_block(self):
        """Test extracting LaTeX from tex code block."""
        input_text = "```tex\n\\begin{equation}\nx = y\n\\end{equation}\n```"
        result = LLMOutputProcessor.process(input_text)
        assert "\\begin{equation}" in result
        assert "```" not in result

    def test_process_latex_with_generic_code_block(self):
        """Test extracting content from generic code block."""
        input_text = "```\n\\sum_{i=0}^{n} i\n```"
        result = LLMOutputProcessor.process(input_text)
        assert result.strip() == "\\sum_{i=0}^{n} i"

    def test_process_removes_thinking_phrases(self):
        """Test that thinking phrases are removed."""
        input_text = "Let me convert this for you.\nHere is the result:\n\\frac{a}{b}"
        result = LLMOutputProcessor.process(input_text)
        assert "Let me" not in result
        assert "Here is" not in result
        assert "\\frac{a}{b}" in result

    def test_process_removes_i_will_phrases(self):
        """Test that 'I will' phrases are removed."""
        input_text = "I will convert this.\n\\int_0^1 x dx"
        result = LLMOutputProcessor.process(input_text)
        assert "I will" not in result
        assert "\\int_0^1 x dx" in result

    def test_process_removes_the_latex_phrases(self):
        """Test that 'the latex' phrases are removed."""
        input_text = "The LaTeX code is:\n\\\\alpha + \\\\beta"
        result = LLMOutputProcessor.process(input_text)
        assert "the latex" not in result.lower()

    def test_process_handles_empty_input(self):
        """Test processing empty string."""
        result = LLMOutputProcessor.process("")
        assert result == ""

    def test_process_handles_whitespace_only(self):
        """Test processing whitespace-only input."""
        result = LLMOutputProcessor.process("   \n\t  ")
        assert result == ""

    def test_process_preserves_latex_structure(self):
        """Test that LaTeX structure is preserved."""
        input_text = (
            "```latex\n\\\\begin{align}\na &= b \\\\\nc &= d\n\\\\end{align}\n```"
        )
        result = LLMOutputProcessor.process(input_text)
        assert r"\begin{align}" in result
        assert r"\\" in result  # Line breaks preserved
        assert r"\end{align}" in result

    def test_process_multiple_code_blocks(self):
        """Test that first code block is used when multiple exist."""
        input_text = (
            "```latex\nfirst_block\n```\nSome text\n```latex\nsecond_block\n```"
        )
        result = LLMOutputProcessor.process(input_text)
        assert "first_block" in result

    def test_process_no_code_blocks_no_thinking(self):
        """Test processing text without code blocks or thinking phrases."""
        input_text = r"\alpha \beta \gamma"
        result = LLMOutputProcessor.process(input_text)
        assert result == input_text


class TestExtractFromCodeBlocks:
    """Tests for _extract_from_code_blocks method."""

    def test_extract_basic_latex_block(self):
        """Test extracting from basic latex block."""
        input_text = "```latex\nx = y\n```"
        result = LLMOutputProcessor._extract_from_code_blocks(input_text)
        assert result == "x = y"

    def test_extract_with_language_identifier(self):
        """Test extracting when language identifier is present."""
        input_text = "```latex\n\\frac{a}{b}\n```"
        result = LLMOutputProcessor._extract_from_code_blocks(input_text)
        assert result == "\\frac{a}{b}"

    def test_extract_with_tex_identifier(self):
        """Test extracting when tex identifier is present."""
        input_text = "```tex\n\\int x dx\n```"
        result = LLMOutputProcessor._extract_from_code_blocks(input_text)
        assert result == "\\int x dx"

    def test_extract_multiline_content(self):
        """Test extracting multiline content."""
        input_text = "```latex\nline1\nline2\nline3\n```"
        result = LLMOutputProcessor._extract_from_code_blocks(input_text)
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_extract_returns_original_when_no_blocks(self):
        """Test that original text is returned when no code blocks."""
        input_text = "plain text without code blocks"
        result = LLMOutputProcessor._extract_from_code_blocks(input_text)
        assert result == input_text.strip()


class TestRemoveThinking:
    """Tests for _remove_thinking method."""

    def test_remove_let_me(self):
        """Test removing 'let me' phrases."""
        input_text = "Let me help you.\n\\\\alpha"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "Let me" not in result

    def test_remove_i_will(self):
        """Test removing 'i will' phrases."""
        input_text = "I will convert this.\n\\\\beta"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "I will" not in result.lower()

    def test_remove_here_is(self):
        """Test removing 'here is' phrases."""
        input_text = "Here is the result.\n\\gamma"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "Here is" not in result

    def test_remove_the_latex(self):
        """Test removing 'the latex' phrases when other content exists."""
        # When there's other content, the line should be filtered
        input_text = "The LaTeX code: \\delta\n\\alpha"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "the latex" not in result.lower()
        # The LaTeX content should be preserved
        assert "\\alpha" in result

    def test_remove_this_gives(self):
        """Test removing 'this gives' phrases."""
        input_text = "This gives us the answer.\n\\epsilon"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "This gives" not in result

    def test_preserve_latex_content(self):
        """Test that LaTeX content is preserved after removing thinking."""
        input_text = "Let me convert this.\nHere is your LaTeX:\n\\int_{0}^{\\infty} e^{-x} dx\nThis gives the result."
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert "\\int_{0}^{\\infty} e^{-x} dx" in result

    def test_remove_leading_empty_lines(self):
        """Test that leading empty lines are removed."""
        input_text = "\n\n\nactual content"
        result = LLMOutputProcessor._remove_thinking(input_text)
        assert result.startswith("actual")

    def test_return_original_when_no_content(self):
        """Test returning original when all content is filtered."""
        input_text = "Let me think about this."
        result = LLMOutputProcessor._remove_thinking(input_text)
        # Should return stripped original if all content is filtered
        assert result is not None


class TestCopyToClipboard:
    """Tests for copy_to_clipboard method."""

    @patch("tablet2latex.llm_output.pyperclip")
    def test_copy_text(self, mock_pyperclip):
        """Test that text is copied to clipboard."""
        test_text = "\\frac{a}{b}"
        LLMOutputProcessor.copy_to_clipboard(test_text)
        mock_pyperclip.copy.assert_called_once_with(test_text)

    @patch("tablet2latex.llm_output.pyperclip")
    def test_copy_empty_string(self, mock_pyperclip):
        """Test copying empty string."""
        LLMOutputProcessor.copy_to_clipboard("")
        mock_pyperclip.copy.assert_called_once_with("")

    @patch("tablet2latex.llm_output.pyperclip")
    def test_copy_multiline_text(self, mock_pyperclip):
        """Test copying multiline text."""
        test_text = "line1\nline2\nline3"
        LLMOutputProcessor.copy_to_clipboard(test_text)
        mock_pyperclip.copy.assert_called_once_with(test_text)

    @patch("tablet2latex.llm_output.pyperclip")
    def test_copy_special_characters(self, mock_pyperclip):
        """Test copying text with special characters."""
        test_text = "\\alpha \\beta \\gamma $%^&"
        LLMOutputProcessor.copy_to_clipboard(test_text)
        mock_pyperclip.copy.assert_called_once_with(test_text)


class TestIntegrationScenarios:
    """Integration tests for common LLM output scenarios."""

    def test_chatgpt_style_output(self):
        """Test processing typical ChatGPT-style output."""
        input_text = (
            "Here's the LaTeX code for your handwritten equation:\n\n"
            "```latex\n"
            "\\int_{0}^{1} x^2 \\cdot dx = \\frac{1}{3}\n"
            "```\n\n"
            "This represents the integral of x squared from 0 to 1."
        )
        result = LLMOutputProcessor.process(input_text)
        assert "\\int_{0}^{1} x^2 \\cdot dx = \\frac{1}{3}" in result
        assert "Here's" not in result
        assert "```" not in result

    def test_claude_style_output(self):
        """Test processing typical Claude-style output."""
        input_text = (
            "I will convert this mathematical expression to LaTeX for you.\n\n"
            "\\begin{equation}\n"
            "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}\n"
            "\\end{equation}\n\n"
            "This is the formula for the sum of the first n integers."
        )
        result = LLMOutputProcessor.process(input_text)
        assert "\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}" in result
        assert "I will" not in result

    def test_ollama_style_output(self):
        """Test processing typical Ollama-style output."""
        input_text = "```\n\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\n```"
        result = LLMOutputProcessor.process(input_text)
        assert "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}" in result
        assert "```" not in result

    def test_complex_math_output(self):
        """Test processing complex mathematical output."""
        input_text = (
            "Let me help you with this.\n\n"
            "```latex\n"
            "\\begin{align}\n"
            "\\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\epsilon_0} \\\\\n"
            "\\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t}\n"
            "\\end{align}\n"
            "```\n\n"
            "These are Maxwell's equations."
        )
        result = LLMOutputProcessor.process(input_text)
        assert "\\nabla \\cdot \\mathbf{E}" in result
        assert "\\begin{align}" in result
        assert "Let me" not in result

    def test_inline_math_output(self):
        """Test processing inline math."""
        input_text = "```latex\n$E = mc^2$\n```"
        result = LLMOutputProcessor.process(input_text)
        assert "$E = mc^2$" in result
