# tracking/website_blocker.py
"""
Cross-platform website blocker using the system hosts file.
"""

from utils.logger import setup_logger
from utils.platform_utils import get_hosts_path

logger = setup_logger("tracking.website_blocker")

REDIRECT_IP = "127.0.0.1"
BLOCK_MARKER_START = "# === ProductivityAnalyzer Block Start ==="
BLOCK_MARKER_END = "# === ProductivityAnalyzer Block End ==="


class WebsiteBlocker:
    """Blocks websites by adding entries to the system hosts file."""

    def __init__(self):
        self.hosts_path = get_hosts_path()

    def block(self, websites: list[str]) -> bool:
        """
        Block a list of websites by adding them to the hosts file.
        Returns True on success, False on failure.
        """
        websites = [w.strip() for w in websites if w.strip()]
        if not websites:
            return True

        try:
            # Read current content
            with open(self.hosts_path) as f:
                content = f.read()

            # Remove any existing blocks from us
            content = self._remove_our_blocks(content)

            # Add new blocks
            block_lines = [BLOCK_MARKER_START]
            for website in websites:
                block_lines.append(f"{REDIRECT_IP} {website}")
                # Also block www subdomain
                if not website.startswith("www."):
                    block_lines.append(f"{REDIRECT_IP} www.{website}")
            block_lines.append(BLOCK_MARKER_END)

            content += "\n" + "\n".join(block_lines) + "\n"

            with open(self.hosts_path, "w") as f:
                f.write(content)

            logger.info(f"Blocked {len(websites)} websites")
            return True

        except PermissionError:
            logger.error("Permission denied: Need administrator/root privileges to modify hosts file")
            return False
        except FileNotFoundError:
            logger.error(f"Hosts file not found at: {self.hosts_path}")
            return False
        except Exception as e:
            logger.error(f"Error blocking websites: {e}")
            return False

    def unblock(self, websites: list[str]) -> bool:
        """
        Unblock websites by removing our entries from the hosts file.
        Returns True on success.
        """
        try:
            with open(self.hosts_path) as f:
                content = f.read()

            content = self._remove_our_blocks(content)

            with open(self.hosts_path, "w") as f:
                f.write(content)

            logger.info("Unblocked websites")
            return True

        except PermissionError:
            logger.error("Permission denied: Need admin privileges to modify hosts file")
            return False
        except Exception as e:
            logger.error(f"Error unblocking websites: {e}")
            return False

    def _remove_our_blocks(self, content: str) -> str:
        """Remove our block markers and everything between them."""
        lines = content.split("\n")
        result = []
        inside_block = False

        for line in lines:
            if BLOCK_MARKER_START in line:
                inside_block = True
                continue
            elif BLOCK_MARKER_END in line:
                inside_block = False
                continue

            if not inside_block:
                result.append(line)

        return "\n".join(result)

    def is_blocked(self, website: str) -> bool:
        """Check if a website is currently blocked."""
        try:
            with open(self.hosts_path) as f:
                content = f.read()
            return website.strip() in content
        except Exception:
            return False
