#!/usr/bin/env python3
"""
DSS Commentary Enhancement CLI.

Batch processing tool to enhance Dead Sea Scrolls variant commentaries
with Strong's numbers and trilingual meditative explanations using Claude.

Usage:
    python -m scripts.dss.commentary.main              # Process all differences
    python -m scripts.dss.commentary.main --sample 5   # Test with 5 samples
    python -m scripts.dss.commentary.main --dry-run    # Preview without writing
    python -m scripts.dss.commentary.main --book isaiah  # Process a single book
"""

import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import List, Dict

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not available
    tqdm = lambda x, **kwargs: x

from .config import (
    MAX_BATCH_SIZE,
    CLAUDE_MODEL,
    validate_anthropic_api_key,
)
from .loader import load_all_differences, load_sample_differences, load_differences_for_book
from .rewriter import DSSCommentaryRewriter
from .writer import write_enhanced_differences, update_metadata, write_sample_output

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
_shutdown_requested = False


def _signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    global _shutdown_requested
    if _shutdown_requested:
        logger.warning("Force exit requested. Exiting immediately...")
        sys.exit(1)
    _shutdown_requested = True
    logger.warning("\nShutdown requested. Finishing current batch then saving progress...")
    logger.warning("Press Ctrl+C again to force exit (may lose progress).")


def split_into_batches(items: List, batch_size: int) -> List[List]:
    """Split list into batches."""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def estimate_cost(total_differences: int, batch_size: int) -> Dict[str, float]:
    """
    Estimate token usage and cost.
    
    Rough estimates:
    - Input: ~300 tokens per difference (Hebrew words + commentary)
    - Output: ~200 tokens per difference (Strong's + 3 commentaries)
    
    Pricing (claude-haiku-4-5):
    - Input: $1.00 per 1M tokens
    - Output: $5.00 per 1M tokens
    """
    input_per_diff = 300
    output_per_diff = 200
    
    total_input = total_differences * input_per_diff
    total_output = total_differences * output_per_diff
    
    input_cost = (total_input / 1_000_000) * 1.00
    output_cost = (total_output / 1_000_000) * 5.00
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': total_input,
        'output_tokens': total_output,
        'total_tokens': total_input + total_output,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'batch_count': (total_differences + batch_size - 1) // batch_size,
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Enhance DSS commentaries with Claude',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        '--sample',
        type=int,
        metavar='N',
        help='Process only N sample differences for testing (default: process all)'
    )

    parser.add_argument(
        '--book',
        type=str,
        metavar='BOOK',
        help='Process a single book by file stem or name (e.g., isaiah)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=MAX_BATCH_SIZE,
        help=f'Batch size for processing (default: {MAX_BATCH_SIZE})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing files'
    )
    
    parser.add_argument(
        '--output-sample',
        type=str,
        metavar='FILE',
        help='Write sample output to specified JSON file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose debug logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate API key
    logger.info("Checking Anthropic API key...")
    if not validate_anthropic_api_key():
        logger.error(
            "ANTHROPIC_API_KEY not found in environment variables.\n"
            "Please add to .env file:\n"
            "ANTHROPIC_API_KEY=your_api_key_here\n"
        )
        return 1
    
    logger.info(f"Using model: {CLAUDE_MODEL}")
    
    # Load differences
    logger.info("Loading DSSI differences...")
    if args.book:
        differences = load_differences_for_book(args.book)
        if args.sample:
            differences = differences[:args.sample]
            logger.info(f"Loaded {len(differences)} sample differences from {args.book}")
        else:
            logger.info(f"Loaded {len(differences)} differences from {args.book}")
    elif args.sample:
        differences = load_sample_differences(args.sample)
        logger.info(f"Loaded {len(differences)} sample differences")
    else:
        differences = load_all_differences()
        logger.info(f"Loaded {len(differences)} total differences")
    
    if not differences:
        logger.error("No differences loaded. Exiting.")
        return 1
    
    # Show cost estimate
    estimate = estimate_cost(len(differences), args.batch_size)
    logger.info("=" * 60)
    logger.info("COST ESTIMATE")
    logger.info("=" * 60)
    logger.info(f"Total differences: {len(differences)}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Number of batches: {estimate['batch_count']}")
    logger.info(f"Estimated tokens: ~{estimate['total_tokens']:,} ({estimate['input_tokens']:,} in, {estimate['output_tokens']:,} out)")
    logger.info(f"Estimated cost: ~${estimate['total_cost']:.2f} (${estimate['input_cost']:.4f} in, ${estimate['output_cost']:.4f} out)")
    logger.info("=" * 60)
    
    if not args.dry_run and not args.sample:
        response = input("\nProceed with processing? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            logger.info("Cancelled by user.")
            return 0
    
    # Setup graceful shutdown handler
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    
    # Initialize rewriter
    logger.info(f"Initializing Claude {CLAUDE_MODEL} rewriter...")
    rewriter = DSSCommentaryRewriter()
    
    # Process in batches
    batches = split_into_batches(differences, args.batch_size)
    logger.info(f"Processing {len(batches)} batch(es)...")
    
    enhanced_differences = []
    
    for i, batch in enumerate(batches, 1):
        # Check for graceful shutdown
        if _shutdown_requested:
            logger.info(f"Shutdown requested. Stopping after batch {i-1}.")
            break
        
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH {i}/{len(batches)} ({len(batch)} differences)")
        logger.info(f"{'='*60}")
        
        try:
            enhanced_batch = rewriter.rewrite_batch(batch, batch_index=i)
            enhanced_differences.extend(enhanced_batch)
            logger.info(f"✓ Batch {i} completed successfully")
        except KeyboardInterrupt:
            logger.warning(f"Batch {i} interrupted. Saving progress...")
            break
        except Exception as e:
            logger.error(f"✗ Batch {i} failed: {e}")
            if not args.sample:
                # For production run, ask if user wants to continue
                try:
                    response = input("\nContinue with next batch? [y/N]: ")
                    if response.lower() not in ['y', 'yes']:
                        break
                except (EOFError, KeyboardInterrupt):
                    logger.info("Stopping due to interrupt.")
                    break
    
    # Show statistics
    stats = rewriter.get_stats()
    logger.info("\n" + "=" * 60)
    logger.info("PROCESSING STATISTICS")
    logger.info("=" * 60)
    logger.info(f"Total batches: {stats['total_batches']}")
    logger.info(f"Total differences: {stats['total_differences']}")
    logger.info(f"Successful: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    if stats['total_differences'] > 0:
        logger.info(f"Success rate: {stats['successful'] / stats['total_differences'] * 100:.1f}%")
    logger.info("=" * 60)
    
    # Write sample output if requested
    if args.output_sample and enhanced_differences:
        output_path = Path(args.output_sample)
        write_sample_output(enhanced_differences, output_path, count=min(10, len(enhanced_differences)))
    
    # Write enhanced differences back to files
    if enhanced_differences:
        logger.info("\nWriting enhanced differences to DSSI files...")
        write_stats = write_enhanced_differences(enhanced_differences, dry_run=args.dry_run)
        logger.info(f"Updated {write_stats['books_updated']} books")
        logger.info(f"Updated {write_stats['differences_updated']} differences")
        
        # Update metadata
        logger.info("\nUpdating metadata...")
        update_metadata(
            total_processed=len(enhanced_differences),
            model_used=CLAUDE_MODEL,
            token_stats=estimate,
            dry_run=args.dry_run
        )
    
    if args.dry_run:
        logger.info("\n✓ DRY RUN completed - no files were modified")
    elif _shutdown_requested:
        logger.info(f"\n⚠ Processing stopped early. Saved {len(enhanced_differences)} differences.")
    else:
        logger.info("\n✓ Processing completed successfully!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
