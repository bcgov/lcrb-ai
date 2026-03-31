import React, { useState } from "react";
import { Dismiss20Regular } from "@fluentui/react-icons";
import styles from "./FeedbackModal.module.css";

const REASON_OPTIONS = [
  "Incorrect or incomplete",
  "Not what I asked for",
  "Style or tone",
  "Safety or legal concern",
  "Other",
];

interface Props {
  onSubmit: (tags: string[], details: string) => void;
  onDismiss: () => void;
}

export const FeedbackModal = ({ onSubmit, onDismiss }: Props) => {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [details, setDetails] = useState("");

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  return (
    <div className={styles.overlay} onClick={onDismiss}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <span className={styles.title}>Share feedback</span>
          <button className={styles.closeButton} onClick={onDismiss} aria-label="Close">
            <Dismiss20Regular />
          </button>
        </div>
        <div className={styles.tags}>
          {REASON_OPTIONS.map((opt) => (
            <button
              key={opt}
              className={`${styles.tag} ${selectedTags.includes(opt) ? styles.tagSelected : ""}`}
              onClick={() => toggleTag(opt)}
            >
              {opt}
            </button>
          ))}
        </div>
        <textarea
          className={styles.textarea}
          placeholder="Share details (optional)"
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          rows={3}
        />
        <div className={styles.footer}>
          <button className={styles.submitButton} onClick={() => onSubmit(selectedTags, details)}>
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};
