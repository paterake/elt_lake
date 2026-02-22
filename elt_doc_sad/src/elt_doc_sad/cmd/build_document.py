"""Build SAD document from command line."""

from __future__ import annotations

from ..sad_generator import generate_sad_document


def main() -> None:
    """CLI entry point for building SAD documents."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build SAD document")
    parser.add_argument(
        "--output",
        required=True,
        help="Output path (directory or full file path)",
    )
    parser.add_argument(
        "--integration-id",
        required=True,
        help="Integration ID (e.g., INT001)",
    )
    parser.add_argument(
        "--vendor-name",
        required=True,
        help="Vendor name",
    )
    parser.add_argument(
        "--title",
        help="Custom document title (optional)",
    )
    
    args = parser.parse_args()
    
    output_path = generate_sad_document(
        output_path=args.output,
        integration_id=args.integration_id,
        vendor_name=args.vendor_name,
        title=args.title,
    )
    
    print(f"SAD document generated: {output_path}")


if __name__ == "__main__":
    main()
