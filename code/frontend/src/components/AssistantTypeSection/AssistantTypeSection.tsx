import React from "react";
import { Stack } from "@fluentui/react";
import Logo from "../../assets/logo.png";
import Cards from "../../pages/chat/Cards_contract/Cards";
import styles from "./AssistantTypeSection.module.css";

type AssistantTypeSectionProps = {
  assistantType: string;
  isAssistantAPILoading: boolean;
  topics : { label: string; indexKey: string}[];
  selectedTopic: string;
  onTopicSelect: (indexKey: string) => void;
  userFirstName?: string;
};

enum assistantTypes {
  default = "default",
  contractAssistant = "contract assistant",
}

export const AssistantTypeSection: React.FC<AssistantTypeSectionProps> = ({
  assistantType,
  isAssistantAPILoading,
  topics,
  selectedTopic,
  onTopicSelect,
  userFirstName
}) => {

  // Custom descriptions per indexKey
  const indexDescriptions: Record<string, string> = {
    'dd-index-2':             'I can help you prepare a due diligence defence when facing enforcement actions.',
    'licence-mgmt-index':     'I can guide you through licence updates, renewals, terminations, and portal management.',
    'law-regs-index':         'I can answer legal and regulatory questions on the Liquor/Cannabis Control and Licensing Acts.',
    'dynamics-index':         'I can provide Microsoft Dynamics guidance, using the best‑fitting Job Aid.',
    'portal-index':           'I can support you with navigating and using the online portal features.',
    'ce-index':               'I can explain compliance and enforcement procedures based on the internal C&E Procedures Manual.',
    'project-planning-index': 'I can provide information on projects that are in progress or being considered, based on the Planning & Priorities tracker'
  };

  const selectedDescription = indexDescriptions[selectedTopic] || '';


  

  return (
    <Stack className={styles.chatEmptyState}>
      {/* <img
        src={Logo}
        className={styles.chatIcon}
        aria-hidden="true"
        alt="LCRB AI Chat"
      /> */}
      {assistantType === assistantTypes.contractAssistant ? (
        <>
          <h1 className={styles.chatEmptyStateTitle}>Contract Summarizer</h1>
          <h2 className={styles.chatEmptyStateSubtitle}>
            AI-Powered assistant for simplified summarization
          </h2>
          <Cards />
        </>
      ) : assistantType === assistantTypes.default ? (
        <>
          <h1 className={styles.chatEmptyStateTitle}>
            How can I help
            {userFirstName ? (
              <>
                , <span className={styles.dataText}>{userFirstName}</span>?
              </>
            ) : (
              "?"
            )}
          </h1>
          <h2 className={styles.chatEmptyStateSubtitle}>
            {selectedTopic
            ? selectedDescription
            : "Select a topic below to get started"}
          </h2>

          {!selectedTopic && (
          <Stack horizontal className={styles.topicPills}>
            {topics.map((t) => (
              <button
                key = {t.indexKey}
                className={`${styles.pill} ${
                  selectedTopic === t.indexKey ? styles.selectedPill : ""
                }`}
                onClick={() => onTopicSelect(t.indexKey)}
                aria-pressed={selectedTopic === t.indexKey}
              >
                {t.label}
              </button>
            ))}
          </Stack>
          )}
        </>
      ) : null}
      {isAssistantAPILoading && (
        <div className={styles.loadingContainer}>
          <div className={styles.loadingIcon}></div>
          <p>Loading...</p>
        </div>
      )}
    </Stack>
  );
};
