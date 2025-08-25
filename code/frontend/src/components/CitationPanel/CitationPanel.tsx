import React from "react";
import { Stack, Text } from "@fluentui/react";
import { DismissRegular } from "@fluentui/react-icons";
import styles from "./CitationPanel.module.css";
import { formatCitationText } from "../../util/formatCitation";
import { Citation } from "../../api";

export type CitationPanelProps = {
  citations: Citation[];
  setIsCitationPanelOpen: (flag: boolean) => void;
  activeCitation?: any;
};

export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  setIsCitationPanelOpen,
}) => {
  // Helper to create a two-sentence snippet with ellipsis
  const getSnippet = (content: string): string => {
    const fullText = formatCitationText(content);
    const sentences = fullText.split('. ').map(s => s.trim()).filter(s => s.length);
    if (sentences.length <= 2) {
      return fullText;
    }
    return sentences.slice(0, 2).join('. ') + '...';
  };

  // Group citations by title (or filepath if title is empty)
  const groups = citations.reduce<Record<string, Citation[]>>((acc, c) => {
    const key = c.title ?? c.filepath ?? "Untitled Source";
    if (!acc[key]) acc[key] = [];
    acc[key].push(c);
    return acc;
  }, {});

  return (
    <div className={`${styles.citationPanel} ${styles.mobileStyles}`}>      
      {/* Header */}
      <Stack
        horizontal
        className={styles.citationPanelHeaderContainer}
        horizontalAlign="space-between"
        verticalAlign="center"
      >
        <Text className={styles.citationPanelHeader}>Sources</Text>
        <DismissRegular
          role="button"
          tabIndex={0}
          className={styles.citationPanelDismiss}
          onClick={() => setIsCitationPanelOpen(false)}
          onKeyDown={(e) =>
            (e.key === " " || e.key === "Enter") &&
            setIsCitationPanelOpen(false)
          }
        />
      </Stack>
      <Text className={`${styles.citationPanelDisclaimer} ${styles.mobileCitationPanelDisclaimer}`}>
        Tables, images, and other special formatting not shown in this preview.
      </Text>

      {/* Citation groups */}
      {Object.entries(groups).map(([heading, docs]) => (
        <div key={heading}>
          <Text className={`${styles.citationPanelTitle} ${styles.mobileCitationPanelTitle}`}>
            {heading}
          </Text>
          {docs.map((c) => (
            <div key={c.reindex_id} className={styles.citationSnippet}>
              <strong>{c.reindex_id}.</strong> {getSnippet(c.content)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
