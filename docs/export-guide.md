# Export Guide

RBGraph keeps SVG as the source format for browser exports.

## SVG

Exports the vector diagram directly and keeps it resolution-independent.

## PNG, JPEG, and WebP

The browser rasterizes the SVG at 1×, 2×, or 4×. Higher scale produces larger output dimensions while preserving the same diagram geometry.

## PNG clipboard

The application creates a 4× PNG and writes it through the browser Clipboard API when image clipboard support is available.

## Standalone HTML

The HTML export contains the SVG and viewer styles in one file. It does not require a running RBGraph server.
