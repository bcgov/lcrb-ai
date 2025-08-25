import { Link } from "react-router-dom";
import styles from "./Layout.module.css";
import logo from "../../assets/BCID_V_RGB_pos.png";
import {
  CopyRegular,
  ShareRegular,
  ShieldLockRegular,
  BroomRegular

} from "@fluentui/react-icons";
import { Dialog, Stack, TextField, Dropdown, IDropdownOption } from "@fluentui/react";
import { ReactNode, useEffect, useRef, useState } from "react";
import { HistoryButton } from "../../components/HistoryButton/HistoryButton";
import { getUserInfo, checkAuthEnforced } from "../../api";
import SpinnerComponent from '../../components/Spinner/Spinner';
import { IndexSelector } from "../../components/IndexSelector/IndexSelector";


export type LayoutProps = {
  children: ReactNode;
  toggleSpinner: boolean;
  onSetShowHistoryPanel: () => void;
  showHistoryBtn: boolean;
  showHistoryPanel: boolean;
  newChat: () => void;
  selectedIndex: string;
  indexes: { name: string; value: string}[];
  onIndexChange: (index: string) => void;
  disableNewChat: boolean;
  isGenerating: boolean;
};
const Layout = ({ children,toggleSpinner, newChat, disableNewChat, isGenerating, selectedIndex, indexes, onIndexChange, ...props }: LayoutProps) => {
  const { showHistoryPanel, showHistoryBtn, onSetShowHistoryPanel } = props;
  const [isSharePanelOpen, setIsSharePanelOpen] = useState<boolean>(false);
  const [copyClicked, setCopyClicked] = useState<boolean>(false);
  const [copyText, setCopyText] = useState<string>("Copy URL");

  const handleShareClick = () => {
    setIsSharePanelOpen(true);
  };

  const handleSharePanelDismiss = () => {
    setIsSharePanelOpen(false);
    setCopyClicked(false);
    setCopyText("Copy URL");
  };

  const handleCopyClick = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopyClicked(true);
  };

  useEffect(() => {
    if (copyClicked) {
      setCopyText("Copied URL");
    }
  }, [copyClicked]);

  const [showAuthMessage, setShowAuthMessage] = useState<boolean | undefined>();
  const firstRender = useRef(true);

  const getUserInfoList = async () => {
    const isAuthEnforced = await checkAuthEnforced(); // Check if auth is enforced
    if(!isAuthEnforced) {
      setShowAuthMessage(false);
      return;
    }

    const userInfoList = await getUserInfo();
    if (
      userInfoList.length === 0 &&
      window.location.hostname !== "localhost" &&
      window.location.hostname !== "127.0.0.1"
    ) {
      setShowAuthMessage(true);
    } else {
      setShowAuthMessage(false);
    }
  };

  useEffect(() => {
    getUserInfoList();
  }, []);

return (
  <div className={styles.layout}>
    <SpinnerComponent
      loading={toggleSpinner}
      label="Please wait.....!"
    />

    <header className={styles.header} role="banner">
      <div className={styles.headerContainer}>
        <Stack horizontal verticalAlign="center" style={{ width: "100%" }}>
          <img
            src={logo}
            className={styles.headerIcon}
            aria-hidden="true"
            alt="LCRB Chat"
          />

          <div className={styles.centerGroup}>
            <Link to="/" className={styles.headerTitleContainer}>
              <h3 className={styles.headerTitle}>LCRB AI Chat</h3>
            </Link>
            <Dropdown
              selectedKey={selectedIndex}
              options={indexes.map(({ name, value }) => ({
                key: value,
                text: name,
              } as IDropdownOption))}
              onChange={(_, opt) => {onIndexChange(opt!.key as string)}}
              styles={{
                root: {},
                title: {
                  background: "transparent",
                  border: "none",
                  marginTop: "4px",
                  selectors: {
                    '@media screen and (min-width: 768px)': {fontSize: '14px'},
                    '@media screen and (max-width: 767px)': {fontSize: '0px'},
                  }
                },
                dropdown: { border: "none", boxShadow: "none" , selectors: {
                  ":focus:after": {
                    borderColor: "transparent"
                  }
                }},
                caretDownWrapper: { margin: 0 },
              }}
              dropdownWidth="auto"
            />
          </div>

          <Stack horizontal className={styles.layoutRightButtons}>
            {!showAuthMessage && showHistoryBtn && (
              <HistoryButton
                onClick={onSetShowHistoryPanel}
                text={`${showHistoryPanel ? "Hide" : "Show"} Chat History`}
              />
            )}
            <div
              className={styles.shareButtonContainer}
              role="button"
              tabIndex={disableNewChat || isGenerating ? -1 : 0}
              aria-disabled={disableNewChat || isGenerating}
              aria-label="New Chat"
              onClick={disableNewChat || isGenerating ? undefined: newChat}
              onKeyDown={(e) =>
                !disableNewChat && !isGenerating && (e.key === "Enter" || e.key === " ")
                ? newChat()
                : null
              }
              style={{
                color: disableNewChat || isGenerating ? "transparent" : "#003366",
                cursor: disableNewChat || isGenerating ? "default" : "pointer",
              }}
            >
              <BroomRegular className={styles.newChatIcon} />
            </div>
          </Stack>
        </Stack>
      </div>
    </header>

    {showAuthMessage ? (
      <Stack className={styles.chatEmptyState}>
        <ShieldLockRegular
          className={styles.chatIcon}
          style={{ color: "darkorange", height: "200px", width: "200px" }}
        />
        <h1 className={styles.chatEmptyStateTitle}>
          Authentication Not Configured
        </h1>
        <h2 className={styles.chatEmptyStateSubtitle}>
          This app does not have authentication configured. Please add an
          identity provider…
        </h2>
      </Stack>
    ) : (
      <>{children}</>
    )}

    <Dialog
      onDismiss={handleSharePanelDismiss}
      hidden={!isSharePanelOpen}
      styles={{
        main: [
          {
            selectors: {
              "@media (min-width: 480px)": {
                maxWidth: "600px",
                background: "#FFFFFF",
                boxShadow:
                  "0px 14px 28.8px rgba(0, 0, 0, 0.24), 0px 0px 8px rgba(0, 0, 0, 0.2)",
                borderRadius: "8px",
                maxHeight: "200px",
                minHeight: "100px",
              },
            },
          },
        ],
      }}
      dialogContentProps={{
        title: "Share the web app",
        showCloseButton: true,
      }}
    >
      <Stack horizontal verticalAlign="center" tokens={{ childrenGap: 8 }}>
        <TextField
          className={styles.urlTextBox}
          defaultValue={window.location.href}
          readOnly
        />
        <div
          className={styles.copyButtonContainer}
          role="button"
          tabIndex={0}
          aria-label="Copy"
          onClick={handleCopyClick}
          onKeyDown={(e) =>
            e.key === "Enter" || e.key === " " ? handleCopyClick() : null
          }
        >
          <CopyRegular className={styles.copyButton} />
          <span className={styles.copyButtonText}>{copyText}</span>
        </div>
      </Stack>
    </Dialog>
  </div>
);

};

export default Layout;
