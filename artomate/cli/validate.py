"""CLI command for configuration validation."""

import sys
import click
from loguru import logger

from artomate.core.config import get_config


@click.command()
@click.option(
    "--strict",
    is_flag=True,
    help="Exit with error code if any required configs are missing",
)
def validate_config(strict: bool):
    """Validate configuration and check for missing API keys.

    This command checks your .env file and environment variables to ensure
    all required configuration is set for running workflows.

    Examples:
        # Check configuration status
        python -m artomate.cli.validate

        # Check and exit with error if configs missing (useful in CI/CD)
        python -m artomate.cli.validate --strict
    """
    config = get_config()

    # Print validation status
    config.print_validation_status()

    # In strict mode, exit with error if validation fails
    if strict:
        try:
            config.validate_complete_workflow()
            logger.info("✅ All required configurations are set!")
            sys.exit(0)
        except ValueError as e:
            logger.error(f"❌ Configuration validation failed:\n{e}")
            sys.exit(1)


if __name__ == "__main__":
    validate_config()
