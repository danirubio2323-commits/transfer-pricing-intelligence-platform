"""Generación de entregables a partir de un AnalysisResult."""

from infrastructure.report.pdf_report import build_report, render_report_bytes

__all__ = ["build_report", "render_report_bytes"]
