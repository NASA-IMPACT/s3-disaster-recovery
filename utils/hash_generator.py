def generate_bucket_hash(source: str, destination: str) -> str:
    """Generate consistent hash from S3 bucket names"""
    import hashlib
    combined = f"{source}-{destination}".encode()
    return hashlib.sha256(combined).hexdigest()[:8]
