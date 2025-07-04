def calculate_metrics(data):
    """Calculate statistical metrics from a dataset."""
    return sum(data) / len(data)

def read_file(path):
    """Read contents of a file."""
    with open(path, "r") as f:
        return f.read() 