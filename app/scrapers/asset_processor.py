"""
Asset Processor
Gorsel optimizasyonu, WebP donusumu, thumbnail olusturma
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from PIL import Image
import io

logger = logging.getLogger(__name__)


class AssetProcessor:
    """
    Gorsel isleme sinifi

    Ozellikler:
    - WebP donusumu (boyut optimizasyonu)
    - Resize (boyutlandirma)
    - Thumbnail olusturma
    - Metadata okuma
    """

    # Varsayilan boyutlar
    THUMBNAIL_SIZE = (300, 200)
    BANNER_SIZE = (1920, 300)
    HERO_SIZE = (1920, 620)
    ICON_SIZE = (256, 256)
    GRID_SIZE = (600, 900)

    # WebP kalitesi
    WEBP_QUALITY = 85
    THUMBNAIL_QUALITY = 75

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path('/var/www/agtrmerkezi/static/assets')

    def convert_to_webp(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        quality: int = WEBP_QUALITY,
        resize: Optional[Tuple[int, int]] = None
    ) -> Optional[Path]:
        """
        Gorseli WebP formatina donustur

        Args:
            input_path: Kaynak gorsel yolu
            output_path: Hedef yol (None ise ayni dizinde .webp uzantili)
            quality: WebP kalitesi (0-100)
            resize: Yeni boyut (width, height) - None ise boyut degismez

        Returns:
            Olusturulan dosya yolu
        """
        try:
            with Image.open(input_path) as img:
                # RGBA'yi RGB'ye donustur (WebP icin)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Seffaf arka plan icin beyaz kullan
                    background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Boyutlandir
                if resize:
                    img = self._resize_image(img, resize)

                # Cikti yolunu belirle
                if output_path is None:
                    output_path = input_path.with_suffix('.webp')

                # Dizini olustur
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # WebP olarak kaydet
                img.save(output_path, 'WEBP', quality=quality, optimize=True)
                logger.info(f"Converted to WebP: {input_path} -> {output_path}")

                return output_path

        except Exception as e:
            logger.exception(f"Failed to convert {input_path}: {e}")
            return None

    def create_thumbnail(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        size: Tuple[int, int] = THUMBNAIL_SIZE,
        quality: int = THUMBNAIL_QUALITY
    ) -> Optional[Path]:
        """
        Thumbnail olustur

        Args:
            input_path: Kaynak gorsel
            output_path: Hedef yol
            size: Thumbnail boyutu
            quality: Kalite

        Returns:
            Thumbnail dosya yolu
        """
        try:
            with Image.open(input_path) as img:
                # RGBA kontrolu
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Thumbnail olustur (aspect ratio koruyarak)
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # Cikti yolunu belirle
                if output_path is None:
                    stem = input_path.stem
                    output_path = input_path.parent / f"{stem}_thumb.webp"

                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(output_path, 'WEBP', quality=quality, optimize=True)

                logger.info(f"Created thumbnail: {output_path}")
                return output_path

        except Exception as e:
            logger.exception(f"Failed to create thumbnail for {input_path}: {e}")
            return None

    def _resize_image(
        self,
        img: Image.Image,
        size: Tuple[int, int],
        maintain_aspect: bool = True
    ) -> Image.Image:
        """
        Gorseli boyutlandir

        Args:
            img: PIL Image
            size: Hedef boyut (width, height)
            maintain_aspect: Aspect ratio'yu koru

        Returns:
            Boyutlandirilmis Image
        """
        if maintain_aspect:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img
        else:
            return img.resize(size, Image.Resampling.LANCZOS)

    def resize_for_banner(
        self,
        input_path: Path,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Banner boyutuna getir (1920x300)"""
        return self.convert_to_webp(
            input_path,
            output_path,
            resize=self.BANNER_SIZE
        )

    def resize_for_hero(
        self,
        input_path: Path,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Hero boyutuna getir (1920x620)"""
        return self.convert_to_webp(
            input_path,
            output_path,
            resize=self.HERO_SIZE
        )

    def get_image_info(self, path: Path) -> Optional[Dict]:
        """
        Gorsel bilgilerini al

        Returns:
            {width, height, format, mode, size_bytes}
        """
        try:
            with Image.open(path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode,
                    'size_bytes': path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Failed to get info for {path}: {e}")
            return None

    def process_game_assets(
        self,
        game_dir: Path,
        create_thumbnails: bool = True,
        convert_webp: bool = True
    ) -> Dict[str, List[Path]]:
        """
        Bir oyunun tum asset'lerini isle

        Args:
            game_dir: Oyun asset dizini
            create_thumbnails: Thumbnail olustur
            convert_webp: WebP'ye donustur

        Returns:
            Islenen dosyalarin listesi
        """
        result = {
            'converted': [],
            'thumbnails': [],
            'errors': []
        }

        # Desteklenen formatlar
        extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

        for asset_file in game_dir.rglob('*'):
            if asset_file.suffix.lower() not in extensions:
                continue

            try:
                # WebP'ye donustur
                if convert_webp and asset_file.suffix.lower() != '.webp':
                    webp_path = self.convert_to_webp(asset_file)
                    if webp_path:
                        result['converted'].append(webp_path)

                # Thumbnail olustur
                if create_thumbnails:
                    thumb_path = self.create_thumbnail(asset_file)
                    if thumb_path:
                        result['thumbnails'].append(thumb_path)

            except Exception as e:
                logger.error(f"Error processing {asset_file}: {e}")
                result['errors'].append(str(asset_file))

        return result

    def optimize_directory(
        self,
        directory: Path,
        recursive: bool = True,
        delete_originals: bool = False
    ) -> Dict[str, int]:
        """
        Dizindeki tum gorselleri optimize et

        Args:
            directory: Hedef dizin
            recursive: Alt dizinleri de tara
            delete_originals: Orijinalleri sil

        Returns:
            Istatistikler
        """
        stats = {
            'processed': 0,
            'converted': 0,
            'saved_bytes': 0,
            'errors': 0
        }

        extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
        pattern = '**/*' if recursive else '*'

        for img_path in directory.glob(pattern):
            if img_path.suffix.lower() not in extensions:
                continue

            stats['processed'] += 1
            original_size = img_path.stat().st_size

            try:
                webp_path = self.convert_to_webp(img_path)
                if webp_path and webp_path.exists():
                    new_size = webp_path.stat().st_size
                    stats['saved_bytes'] += original_size - new_size
                    stats['converted'] += 1

                    if delete_originals and webp_path != img_path:
                        img_path.unlink()

            except Exception as e:
                logger.error(f"Error optimizing {img_path}: {e}")
                stats['errors'] += 1

        logger.info(
            f"Optimization complete: {stats['converted']}/{stats['processed']} converted, "
            f"{stats['saved_bytes'] / 1024 / 1024:.2f} MB saved"
        )

        return stats


# Convenience functions
def convert_image(input_path: str, output_path: str = None) -> Optional[str]:
    """Tek gorsel donustur"""
    processor = AssetProcessor()
    result = processor.convert_to_webp(Path(input_path), Path(output_path) if output_path else None)
    return str(result) if result else None


def create_thumbnail(input_path: str, output_path: str = None) -> Optional[str]:
    """Tek thumbnail olustur"""
    processor = AssetProcessor()
    result = processor.create_thumbnail(Path(input_path), Path(output_path) if output_path else None)
    return str(result) if result else None
