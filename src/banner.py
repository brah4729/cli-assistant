"""Custom banner/image display module for CodeBuddy."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def find_banner_image() -> Optional[Path]:
    """Find a custom banner image to display."""
    # Check environment variable first
    banner_path = os.environ.get("CODEBUDDY_BANNER")
    if banner_path:
        p = Path(banner_path).expanduser()
        if p.exists():
            return p

    # Check common locations
    search_paths = [
        Path.home() / ".config" / "codebuddy" / "banner.png",
        Path.home() / ".config" / "codebuddy" / "banner.jpg",
        Path.home() / ".local" / "share" / "codebuddy" / "banner.png",
        Path.home() / ".local" / "share" / "codebuddy" / "banner.jpg",
        Path("./banner.png").resolve(),
        Path("./banner.jpg").resolve(),
        Path("./data/banner.png").resolve(),
        Path("./data/banner.jpg").resolve(),
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


def display_image_banner(image_path: Optional[str] = None) -> bool:
    """Display a custom banner image.

    Args:
        image_path: Path to custom image. If None, searches for banner.

    Returns:
        True if image was displayed, False otherwise.
    """
    if image_path:
        banner = Path(image_path).expanduser()
        if not banner.exists():
            console.print(f"[red]Banner not found: {image_path}[/red]")
            return False
    else:
        banner = find_banner_image()
        if not banner:
            return False

    term = os.environ.get("TERM", "").lower()

    # Try different display methods based on terminal
    if "kitty" in term:
        if _try_kitty_icat(banner):
            return True
        if _try_kitty_graphics(banner):
            return True

    if _has_sixel_support():
        if _try_sixel(banner):
            return True

    if _has_chafa():
        if _try_chafa(banner):
            return True

    # Fallback to ASCII block art
    return _try_ascii_blocks(banner)


def _try_kitty_icat(image_path: Path) -> bool:
    """Try displaying with kitty's icat kitten."""
    try:
        subprocess.run(
            ["kitty", "+kitten", "icat", "--align=center", str(image_path)],
            check=True,
            capture_output=True,
        )
        print()
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _try_kitty_graphics(image_path: Path) -> bool:
    """Try kitty graphics protocol directly."""
    try:
        from PIL import Image
        import base64

        img = Image.open(image_path)

        # Resize to reasonable width
        term_width = shutil.get_terminal_size().columns
        max_width = min(term_width - 4, 80)

        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Convert to PNG bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_data = img_bytes.getvalue()

        # Kitty protocol: ESC_Ga=T,f=100,t=d,w=W,h=H;DATAESC\
        b64_data = base64.b64encode(img_data).decode()
        width = img.width
        height = img.height

        sys.stdout.write(f"\033_Ga=T,f=100,t=d,w={width},h={height};{b64_data}\033\\")
        sys.stdout.write("\n")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def _has_sixel_support() -> bool:
    """Check if terminal supports sixel."""
    term = os.environ.get("TERM", "")
    return any(t in term for t in ["foot", "xterm", "mlterm", "wezterm"])


def _try_sixel(image_path: Path) -> bool:
    """Try displaying with sixel (ImageMagick)."""
    try:
        subprocess.run(
            ["convert", str(image_path), "-resize", "80x", "sixel:-"],
            check=True,
            stdout=sys.stdout,
        )
        print()
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _has_chafa() -> bool:
    """Check if chafa is available."""
    try:
        result = subprocess.run(["which", "chafa"], capture_output=True)
        return result.returncode == 0
    except Exception:
        return False


def _try_chafa(image_path: Path) -> bool:
    """Try displaying with chafa (colored unicode blocks)."""
    try:
        subprocess.run(
            ["chafa", "--symbols=block+braille", "--size=80", "--fill=scale", str(image_path)],
            check=True,
            stdout=sys.stdout,
        )
        print()
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _try_ascii_blocks(image_path: Path) -> bool:
    """Fallback: Convert image to ASCII using block characters."""
    try:
        from PIL import Image

        img = Image.open(image_path)

        # Convert to grayscale and resize
        term_width = shutil.get_terminal_size().columns
        width = min(60, term_width - 4)
        aspect = img.height / img.width
        height = int(width * aspect * 0.5)  # *0.5 because chars are taller than wide

        img = img.convert('L').resize((width, height), Image.Resampling.LANCZOS)

        # Block characters for different shades
        blocks = [' ', '░', '▒', '▓', '█']

        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                pixel = img.getpixel((x, y))
                # Map 0-255 to block index
                idx = int(pixel / 255 * (len(blocks) - 1))
                line += blocks[idx]
            lines.append(line)

        # Draw border
        border = "╔" + "═" * width + "╗"
        bottom = "╚" + "═" * width + "╝"

        console.print(f"[cyan]{border}[/cyan]")
        for line in lines:
            console.print(f"[cyan]║[/cyan]{line}[cyan]║[/cyan]")
        console.print(f"[cyan]{bottom}[/cyan]")

        return True
    except Exception:
        return False


def set_banner(image_path: str) -> bool:
    """Set a custom banner image.

    Args:
        image_path: Path to PNG/JPG image.

    Returns:
        True if successful, False otherwise.
    """
    src = Path(image_path).expanduser()
    if not src.exists():
        console.print(f"[red]Image not found: {image_path}[/red]")
        return False

    # Copy to data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    ext = src.suffix.lower()
    if ext not in ['.png', '.jpg', '.jpeg']:
        console.print(f"[red]Unsupported format: {ext}. Use PNG or JPG.[/red]")
        return False

    dst = data_dir / "banner.png"
    try:
        from PIL import Image
        img = Image.open(src)
        # Convert to PNG for consistency
        img.save(dst, "PNG")
        console.print(f"[green]Banner set: {dst}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error setting banner: {e}[/red]")
        return False


def show_ascii_banner():
    """Show fallback ASCII text banner."""
    console.print("""
    ╔════════════════════════════════════════════════════╗
    ║                                                    ║
    ║    ██████╗ ██████╗ ██████╗ ███████╗██████╗ ██╗   ██╗██████╗ ██████╗ ██╗   ██╗
    ║   ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██║   ██║██╔══██╗██╔══██╗╚██╗ ██╔╝
    ║   ██║     ██║   ██║██║  ██║█████╗  ██████╔╝██║   ██║██║  ██║██║  ██║ ╚████╔╝
    ║   ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗██║   ██║██║  ██║██║  ██║  ╚██╔╝
    ║   ╚██████╗╚██████╔╝██████╔╝███████╗██████╔╝╚██████╔╝██████╔╝██████╔╝   ██║
    ║    ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝
    ║                                                    ║
    ╚════════════════════════════════════════════════════╝
    """, style="bold cyan")


# Import io here to avoid issues
import io
