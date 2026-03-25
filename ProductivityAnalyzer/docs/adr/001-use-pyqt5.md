# ADR-001: Use PyQt5 for Desktop UI

## Status
Accepted

## Context
We needed a cross-platform desktop GUI framework for a productivity tracking application.

## Decision
We chose PyQt5 over alternatives (Tkinter, PyQt6, PySide6, Electron).

## Rationale
- **Mature & stable**: PyQt5 has years of production use
- **Rich widget set**: Tables, charts, system tray, all built-in
- **Matplotlib integration**: FigureCanvasQTAgg works seamlessly
- **Community**: Large ecosystem of examples and Stack Overflow answers
- **PyQt6 considered**: Would require enum syntax changes across 50+ files with no functional benefit

## Consequences
- Locked to Qt5 widget behavior
- Will reassess PyQt6 migration for v3.0