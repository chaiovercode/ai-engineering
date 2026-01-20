// Smart auto-title generation from content

const MAX_TITLE_LENGTH = 50;

export function generateTitle(linkedInContent: string | null, reportText: string): string {
  // Try to extract from LinkedIn content first line
  if (linkedInContent) {
    const firstLine = linkedInContent.split("\n")[0].trim();
    if (firstLine.length > 0) {
      // Remove emojis and clean up
      const cleaned = firstLine
        .replace(/[^\w\s.,!?-]/g, "")
        .trim();

      if (cleaned.length > MAX_TITLE_LENGTH) {
        return cleaned.substring(0, MAX_TITLE_LENGTH - 3) + "...";
      }
      return cleaned || "Untitled Report";
    }
  }

  // Fallback to report text first line
  if (reportText) {
    const firstLine = reportText.split("\n")[0].trim();
    if (firstLine.length > 0) {
      if (firstLine.length > MAX_TITLE_LENGTH) {
        return firstLine.substring(0, MAX_TITLE_LENGTH - 3) + "...";
      }
      return firstLine;
    }
  }

  return "Untitled Report";
}

export function truncateTitle(title: string, maxLength: number = MAX_TITLE_LENGTH): string {
  if (title.length <= maxLength) return title;
  return title.substring(0, maxLength - 3) + "...";
}
