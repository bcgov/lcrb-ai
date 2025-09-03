export const formatCitationText = (text: string): string => {
  const cleaned = text
    .replace(/\s+/g, " ")                  // collapse whitespace
    .replace(/\[.*?\]\(.*?\)/g, "")        // strip Markdown links
    .replace(/\/[A-Za-z0-9_\-./]+(\.pdf|\.docx|\.txt)?/g, "")
    .replace(/(?:Page \d+ of \d+|Page \d+)/gi, "")
    .replace(/-{2,}|_{2,}/g, "")
    .replace(/\n/g, " ")                   // remove hard breaks
    .trim();                               // trim ends

  const filtered = cleaned
    .split(". ")
    .filter(sentence => /^[A-Z]/.test(sentence.trim()))
    .join(". ");

  return filtered;
};
