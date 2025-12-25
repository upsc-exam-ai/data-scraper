"""
Main entry point for the syncer service.
"""
import logging
import sys
import argparse
from .sync import SyncOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='UPSC AI News Syncer')
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test connectivity to sources and databases'
    )
    
    args = parser.parse_args()
    
    orchestrator = SyncOrchestrator()
    
    if args.test:
        logger.info("Running connectivity tests...")
        orchestrator.test_databases()
        orchestrator.test_sources()
    else:
        try:
            orchestrator.sync(days_back=args.days)
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

