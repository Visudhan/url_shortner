"""
Short code generator for URL shortening.

Generates random Base62 strings (a-z, A-Z, 0-9) and checks the database
to ensure uniqueness before returning.

Base62 math:
  - 6 characters → 62^6 = 56,800,235,584 possible codes (~56 billion)
  - At 1 million URLs/day, it would take ~155 YEARS to exhaust the space
  - Collision probability stays extremely low until ~1% of the space is used

Why random instead of sequential?
  - Sequential (1, 2, 3...) leaks information: competitors can guess your URL count
  - Random codes are unpredictable — can't enumerate or scrape URLs
"""

import string
import secrets
from shortener.models import URL


# The 62 characters used in short codes
# a-z (26) + A-Z (26) + 0-9 (10) = 62 characters
# Using string constants to avoid typos
BASE62_ALPHABET = string.ascii_letters + string.digits  # 'abcdefg...XYZ0123456789'

# Default length of generated short codes
SHORT_CODE_LENGTH = 6

# Maximum retry attempts before giving up (safety valve)
MAX_RETRIES = 10


def generate_short_code(length=SHORT_CODE_LENGTH):
    """
    Generate a unique random Base62 short code.

    How it works:
      1. Generate a random string of `length` characters from Base62 alphabet
      2. Check if it already exists in the database
      3. If collision → try again (up to MAX_RETRIES times)
      4. If unique → return it

    Uses `secrets` module (not `random`) because:
      - `random` is pseudo-random — predictable if you know the seed
      - `secrets` uses the OS cryptographic random source — unpredictable
      - Important for security: nobody should be able to guess the next short code

    Args:
        length: Number of characters in the short code (default: 6)

    Returns:
        A unique short code string (e.g., 'aB3xZ9')

    Raises:
        RuntimeError: If a unique code can't be generated after MAX_RETRIES attempts
    """

    for attempt in range(MAX_RETRIES):
        # Generate random code: pick `length` random characters from alphabet
        code = "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

        # Check database for collision
        # Using .filter().exists() is optimized — it runs:
        #   SELECT 1 FROM urls WHERE short_code = 'aB3xZ9' LIMIT 1
        # This is faster than .filter().count() because it stops at the first match
        if not URL.objects.filter(short_code=code).exists():
            return code

    # If we get here, something is very wrong (extremely unlikely with 56B combinations)
    raise RuntimeError(
        f"Failed to generate a unique short code after {MAX_RETRIES} attempts. "
        f"This should be statistically impossible with {62 ** length:,} possible combinations. "
        f"Consider increasing SHORT_CODE_LENGTH."
    )
