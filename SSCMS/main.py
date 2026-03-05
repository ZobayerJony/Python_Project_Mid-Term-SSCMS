from sscms.ui.app import SSCMSApp


def main() -> None:
    """
    Entry point for SSCMS.
    Run: python main.py
    """
    app = SSCMSApp()
    app.run()


if __name__ == "__main__":
    main()