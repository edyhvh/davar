"""Core processing logic for image transcription."""

import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .api import ClaudeClient
from .books import (
    get_book_info, get_chapter_context, fix_chapter_assignment,
    validate_chapter_number, infer_chapter_from_sequence,
    get_sequence_context_for_prompt, diagnose_checkpoint
)
from .checkpoint import CheckpointManager
from .prompt import load_yaml, build_prompt, get_yaml_version, calculate_yaml_hash
from .validate import parse_json_response, validate_chapter_object, validate_verse_object
from .consolidate import consolidate_book
from .config import SPECIAL_BOOKS, CLAUDE_PRICING, MAX_DRY_RUN_IMAGES, PARALLEL_DELAY_SECONDS

logger = logging.getLogger(__name__)


def get_image_list(book_name: str, images_dir: Path) -> List[Path]:
    """Get list of images to process for a book."""
    book_dir = images_dir / book_name

    if not book_dir.exists():
        logger.warning(f"Image directory not found: {book_dir}")
        return []

    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        image_files.extend(book_dir.glob(ext))
    image_files = sorted(list(set(image_files)))

    # Special case: colossians
    if book_name.lower() == 'colossians':
        exclude = SPECIAL_BOOKS.get('colossians', {}).get('exclude_pages', [])
        image_files = [img for img in image_files if img.name not in exclude]

    # Special case: john1
    if book_name.lower() == 'john1':
        config = SPECIAL_BOOKS.get('john1', {})
        skip_pages = config.get('skip_pages', [])
        odd_from = config.get('odd_from', 9)

        filtered = []
        for img in image_files:
            try:
                num = int(img.stem)
                if num in skip_pages:
                    continue
                if num >= odd_from:
                    if num % 2 == 0:
                        continue
                elif num % 2 == 1:
                    continue
                filtered.append(img)
            except ValueError:
                continue
        return filtered

    # Default: skip odd-numbered images
    return [img for img in image_files if int(img.stem) % 2 == 0]


def calculate_cost(usage: dict) -> float:
    """Calculate actual cost based on token usage."""
    if not usage:
        return 0.01

    input_tokens = usage.get('prompt_tokens', 0)
    output_tokens = usage.get('completion_tokens', 0)

    cost = (input_tokens / 1_000_000 * CLAUDE_PRICING['input']) + \
           (output_tokens / 1_000_000 * CLAUDE_PRICING['output'])
    return max(cost, 0.00001)


def build_context_from_checkpoint(
    checkpoint: CheckpointManager,
    upcoming_images: List[Path],
    book_name: str
) -> Dict[str, Any]:
    """Build sequential context from checkpoint for resuming."""
    if not upcoming_images:
        return {'last_chapter': 0, 'last_verse': 0}

    images_state = checkpoint.state.get('images', {})

    try:
        first_num = int(upcoming_images[0].stem)
    except ValueError:
        return {'last_chapter': 0, 'last_verse': 0}

    prev_num = first_num - 2
    while prev_num > 0:
        candidate = f"{prev_num:06d}.png"
        if candidate in images_state:
            img_data = images_state[candidate]
            if img_data.get('status') == 'completed' and img_data.get('verses'):
                max_ch, max_v = 0, 0
                for verse_data in img_data['verses'].values():
                    ch, v = verse_data.get('chapter', 0), verse_data.get('verse', 0)
                    if ch > max_ch or (ch == max_ch and v > max_v):
                        max_ch, max_v = ch, v
                if max_ch > 0:
                    logger.info(f"Context from {candidate}: {max_ch}:{max_v}")
                return {'last_chapter': max_ch, 'last_verse': max_v}
        prev_num -= 2

    return {'last_chapter': 0, 'last_verse': 0}


def process_image(
    image_path: Path,
    client: ClaudeClient,
    prompt_template: str,
    checkpoint: CheckpointManager,
    book_name: str,
    dry_run: bool = False,
    sequential_context: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Process a single image."""
    image_name = image_path.name
    context = sequential_context or {'last_chapter': 0, 'last_verse': 0}

    # Skip if already processed
    if checkpoint.is_image_processed(image_name):
        logger.debug(f"Skipping {image_name} (already processed)")
        img_data = checkpoint.state.get('images', {}).get(image_name, {})
        if img_data.get('verses'):
            max_ch, max_v = 0, 0
            for v in img_data['verses'].values():
                ch, vn = v.get('chapter', 0), v.get('verse', 0)
                if ch > max_ch or (ch == max_ch and vn > max_v):
                    max_ch, max_v = ch, vn
            return True, {'last_chapter': max_ch, 'last_verse': max_v}
        return True, context

    if dry_run:
        logger.info(f"[DRY RUN] Would process {image_name}")
        return True, context

    try:
        checkpoint.update_image_status(image_name, 'processing')

        # Build enhanced prompt with context
        sequence_hint = get_sequence_context_for_prompt(book_name, context)
        enhanced_prompt = prompt_template + ("\n" + sequence_hint if sequence_hint else "")

        logger.info(f"Processing {image_name}...")
        response = client.transcribe_image(image_path, enhanced_prompt)
        cost = calculate_cost(response.get('usage', {}))

        # Parse response
        parsed_json, error = parse_json_response(response['text'])
        if error:
            logger.error(f"JSON parse error for {image_name}: {error}")
            checkpoint.update_image_status(image_name, 'failed', cost_usd=cost, error=error)
            checkpoint.save()
            return False, context

        if 'chapters' not in parsed_json:
            error = "Missing 'chapters' in response"
            logger.error(f"Invalid response for {image_name}: {error}")
            checkpoint.update_image_status(image_name, 'failed', cost_usd=cost, error=error)
            checkpoint.save()
            return False, context

        # Apply sequential inference and structure validation
        inferred_chapters, updated_context = infer_chapter_from_sequence(
            book_name, context, parsed_json['chapters'], image_name
        )
        fixed_chapters = fix_chapter_assignment(book_name, inferred_chapters)

        # Extract and validate verses
        verses_dict = {}
        for chapter_data in fixed_chapters:
            is_valid, error = validate_chapter_object(chapter_data)
            if not is_valid:
                logger.error(f"Invalid chapter in {image_name}: {error}")
                continue

            chapter_num = chapter_data['number']
            if not validate_chapter_number(book_name, chapter_num):
                logger.warning(f"Invalid chapter {chapter_num} for {book_name}")
                continue

            for verse_data in chapter_data['verses']:
                is_valid, error = validate_verse_object(verse_data)
                if not is_valid:
                    logger.warning(f"Invalid verse in {image_name}: {error}")
                    continue

                verse_num = verse_data['number']
                verse_key = f"{chapter_num}_{verse_num}"
                verses_dict[verse_key] = {
                    'status': 'completed',
                    'chapter': chapter_num,
                    'verse': verse_num,
                    'text_nikud': verse_data['text_nikud'],
                    'source_files': [image_name],
                    'visual_uncertainty': verse_data.get('visual_uncertainty', [])
                }

        if not verses_dict:
            checkpoint.update_image_status(image_name, 'failed', cost_usd=cost, error="No valid verses")
            checkpoint.save()
            return False, context

        checkpoint.update_image_status(image_name, 'completed', cost_usd=cost, verses=verses_dict)
        checkpoint.save()

        logger.info(f"✓ {image_name}: {len(verses_dict)} verses, ${cost:.5f}")
        return True, updated_context

    except Exception as e:
        logger.error(f"Error processing {image_name}: {e}")
        checkpoint.update_image_status(image_name, 'failed', cost_usd=0.0, error=str(e))
        checkpoint.save()
        return False, context


def process_book(
    book_name: str,
    images_dir: Path,
    output_dir: Path,
    checkpoint_dir: Path,
    client: ClaudeClient,
    prompt_template: str,
    yaml_version: str,
    yaml_hash: str,
    dry_run: bool = False,
    resume: bool = False,
    reprocess_failed: bool = False,
    reprocess_images: Optional[List[str]] = None,
    parallel: int = 1
) -> bool:
    """Process a single book."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing book: {book_name}")
    logger.info(f"{'='*60}")

    # Add book context to prompt
    book_context = get_chapter_context(book_name)
    book_prompt = prompt_template + ("\n" + book_context if book_context else "")

    book_info = get_book_info(book_name)
    if book_info:
        logger.info(f"Structure: {book_info['total_chapters']} chapters, {book_info['total_verses']} verses")

    # Initialize checkpoint
    checkpoint_path = checkpoint_dir / f"{book_name}_state.json"
    checkpoint = CheckpointManager(checkpoint_path)

    if resume or reprocess_failed or reprocess_images:
        checkpoint.load()
        if checkpoint.state.get('yaml_hash') != yaml_hash:
            logger.warning("YAML configuration changed since last run")
            checkpoint.state['yaml_hash'] = yaml_hash
            checkpoint.state['yaml_version'] = yaml_version
    else:
        image_list = get_image_list(book_name, images_dir)
        checkpoint.initialize(book_name, len(image_list), yaml_version, yaml_hash)
        checkpoint.save()

    # Get image list
    image_list = get_image_list(book_name, images_dir)
    if not image_list:
        logger.warning(f"No images found for {book_name}")
        return False

    # Filter images
    if reprocess_images:
        image_list = [img for img in image_list if img.name in reprocess_images]
        for img in image_list:
            if img.name in checkpoint.state.get('images', {}):
                checkpoint.state['images'][img.name]['status'] = 'pending'
    elif reprocess_failed:
        failed = checkpoint.get_failed_images()
        image_list = [img for img in image_list if img.name in failed]
        for img in image_list:
            if img.name in checkpoint.state.get('images', {}):
                checkpoint.state['images'][img.name]['status'] = 'pending'
    elif dry_run:
        unprocessed = [img for img in image_list if not checkpoint.is_image_processed(img.name)]
        image_list = unprocessed[:MAX_DRY_RUN_IMAGES]
        logger.info(f"DRY RUN: Processing {len(image_list)} images")
    else:
        image_list = [img for img in image_list if not checkpoint.is_image_processed(img.name)]

    if not image_list:
        logger.info(f"No images to process for {book_name}")
        if checkpoint.state.get('processed_images', 0) > 0:
            consolidate_book(checkpoint.state, book_name, output_dir)
        return True

    successful, failed_count = 0, 0
    context = build_context_from_checkpoint(checkpoint, image_list, book_name)

    if parallel > 1 and not dry_run:
        logger.warning("Parallel mode: sequential inference limited")
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(process_image, img, client, book_prompt, checkpoint, book_name, False, None): img
                for img in image_list
            }
            with tqdm(total=len(image_list), desc=book_name, ncols=80) as pbar:
                for future in as_completed(futures):
                    try:
                        if future.result()[0]:
                            successful += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.error(f"Thread failed: {e}")
                        failed_count += 1
                    pbar.update(1)
                    time.sleep(PARALLEL_DELAY_SECONDS)
    else:
        with tqdm(total=len(image_list), desc=book_name, ncols=80) as pbar:
            for image_path in image_list:
                success, context = process_image(
                    image_path, client, book_prompt, checkpoint, book_name, dry_run, context
                )
                if success:
                    successful += 1
                else:
                    failed_count += 1
                pbar.update(1)

    logger.info(f"\nCompleted {book_name}: {successful} successful, {failed_count} failed")

    # Consolidate if not dry run
    if not dry_run and (successful > 0 or checkpoint.state.get('processed_images', 0) > 0):
        checkpoint.load()
        consolidate_book(checkpoint.state, book_name, output_dir)

        diagnosis = diagnose_checkpoint(book_name, checkpoint.state)
        if diagnosis.get('health') == 'ISSUES_DETECTED':
            logger.warning(f"\n⚠️ Issues detected in {book_name}")
            for problem in diagnosis.get('problems', []):
                logger.warning(f"  - [{problem['type']}] {problem['message']}")

    return failed_count == 0


def process_books(
    book_names: List[str],
    images_dir: Path,
    output_dir: Path,
    yaml_path: Path,
    checkpoint_dir: Path,
    dry_run: bool = False,
    resume: bool = False,
    reprocess_failed: bool = False,
    reprocess_images: Optional[List[str]] = None,
    parallel: int = 1,
    model_name: Optional[str] = None
) -> bool:
    """Process multiple books."""
    logger.info("Loading YAML configuration...")
    yaml_data = load_yaml(yaml_path)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()

    yaml_version = get_yaml_version(yaml_data)
    yaml_hash = calculate_yaml_hash(yaml_content)

    logger.info(f"YAML version: {yaml_version}")
    logger.info(f"YAML hash: {yaml_hash[:16]}...")

    prompt_template = build_prompt(yaml_data)
    logger.info("Prompt template built")

    try:
        client = ClaudeClient(model_name=model_name)
        logger.info(f"Claude client: {client.model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Claude client: {e}")
        return False

    success_count = 0
    for book_name in book_names:
        if process_book(
            book_name, images_dir, output_dir, checkpoint_dir, client,
            prompt_template, yaml_version, yaml_hash, dry_run, resume,
            reprocess_failed, reprocess_images, parallel
        ):
            success_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Completed: {success_count}/{len(book_names)} books")
    logger.info(f"{'='*60}")

    return success_count == len(book_names)

