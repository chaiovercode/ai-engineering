// Image export utilities using html-to-image
import { toPng, toBlob } from "html-to-image";

export interface ExportOptions {
  quality?: number;
  pixelRatio?: number;
  backgroundColor?: string;
}

const defaultOptions: ExportOptions = {
  quality: 0.95,
  pixelRatio: 2,
  backgroundColor: "#ffffff",
};

export async function exportToPng(
  element: HTMLElement,
  filename: string,
  options: ExportOptions = {}
): Promise<void> {
  const opts = { ...defaultOptions, ...options };

  try {
    const dataUrl = await toPng(element, {
      quality: opts.quality,
      pixelRatio: opts.pixelRatio,
      backgroundColor: opts.backgroundColor,
    });

    // Create download link
    const link = document.createElement("a");
    link.download = filename;
    link.href = dataUrl;
    link.click();
  } catch (error) {
    console.error("Failed to export image:", error);
    throw error;
  }
}

export async function copyToClipboard(
  element: HTMLElement,
  options: ExportOptions = {}
): Promise<void> {
  const opts = { ...defaultOptions, ...options };

  try {
    const blob = await toBlob(element, {
      quality: opts.quality,
      pixelRatio: opts.pixelRatio,
      backgroundColor: opts.backgroundColor,
    });

    if (!blob) throw new Error("Failed to create blob");

    await navigator.clipboard.write([
      new ClipboardItem({ "image/png": blob }),
    ]);
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
    throw error;
  }
}

export async function getImageBlob(
  element: HTMLElement,
  options: ExportOptions = {}
): Promise<Blob> {
  const opts = { ...defaultOptions, ...options };

  const blob = await toBlob(element, {
    quality: opts.quality,
    pixelRatio: opts.pixelRatio,
    backgroundColor: opts.backgroundColor,
  });

  if (!blob) throw new Error("Failed to create blob");
  return blob;
}
