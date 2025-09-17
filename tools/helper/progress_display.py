"""
Progress Display Module
Handles progress bar and status display for tools
"""

import sys
import time
from typing import Optional


class ProgressDisplay:
    """Handles progress display with a progress bar"""

    def __init__(self, total_items: int):
        self.total_items = total_items
        self.current_item = 0
        self.current_pkg = ""
        self.start_time = time.time()
        self.last_update_time = 0
        self.update_interval = 0.1  # Update display every 100ms

    def update_current_pkg(self, pkg_name: str):
        """Update the current PKG being processed"""
        self.current_pkg = pkg_name

    def update(self, item_name: str):
        """Update progress for a processed item"""
        self.current_item += 1

        # Only update display if enough time has passed
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval or self.current_item == self.total_items:
            self.last_update_time = current_time
            self._display_progress(item_name)

    def _display_progress(self, current_file: str):
        """Display the progress bar and current status"""
        # Calculate progress
        if self.total_items == 0:
            percentage = 100
        else:
            percentage = (self.current_item / self.total_items) * 100

        # Calculate elapsed time and estimated time
        elapsed_time = time.time() - self.start_time
        if self.current_item > 0:
            avg_time_per_item = elapsed_time / self.current_item
            remaining_items = self.total_items - self.current_item
            estimated_remaining = avg_time_per_item * remaining_items
        else:
            estimated_remaining = 0

        # Create progress bar (use ASCII for Windows compatibility)
        bar_width = 40
        filled = int(bar_width * percentage / 100)
        bar = '#' * filled + '-' * (bar_width - filled)

        # Format times
        elapsed_str = self._format_time(elapsed_time)
        remaining_str = self._format_time(estimated_remaining)

        # Truncate file name if too long
        max_filename_len = 50
        if len(current_file) > max_filename_len:
            current_file = "..." + current_file[-(max_filename_len - 3):]

        # Build status line
        status_line = (
            f"[{bar}] {percentage:5.1f}% "
            f"({self.current_item}/{self.total_items}) "
        )

        # Add PKG info if available
        if self.current_pkg:
            status_line += f"| PKG: {self.current_pkg} "

        status_line += (
            f"| Elapsed: {elapsed_str} "
            f"| ETA: {remaining_str} "
            f"| File: {current_file}"
        )

        # Get terminal width for proper clearing
        try:
            import shutil
            terminal_width = shutil.get_terminal_size().columns
        except:
            terminal_width = 200

        # Pad with spaces to clear the entire line
        status_line = status_line[:terminal_width-1].ljust(terminal_width-1)

        # Write status with carriage return
        sys.stdout.write('\r' + status_line)
        sys.stdout.flush()

    def _format_time(self, seconds: float) -> str:
        """Format time in seconds to a readable string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def finish(self):
        """Finish the progress display"""
        if self.current_item > 0:
            self._display_progress("Complete")
        print()  # New line after progress bar


class SimpleProgress:
    """Simple progress display without a progress bar (for debugging/verbose mode)"""

    def __init__(self, total_items: int):
        self.total_items = total_items
        self.current_item = 0
        self.current_pkg = ""

    def update_current_pkg(self, pkg_name: str):
        """Update the current PKG being processed"""
        self.current_pkg = pkg_name
        print(f"\nProcessing: {pkg_name}")

    def update(self, item_name: str):
        """Update progress for a processed item"""
        self.current_item += 1
        print(f"  [{self.current_item}/{self.total_items}] Extracted: {item_name}")

    def finish(self):
        """Finish the progress display"""
        print(f"\nCompleted: {self.current_item}/{self.total_items} files")