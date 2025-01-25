# Phonemizer and Drug Similarity Analysis with Modified ALINE Algorithm

This repository contains tools for processing, phonemizing, and analyzing drug names, specifically targeting phonetic confusability. The project includes:

1. **Phonemization Pipeline**:
   - Cleans and preprocesses drug trade names using custom regex patterns.
   - Phonemizes names using `phonemizer` with `festival` or `espeak` backends for phonetic representation.
   - Outputs processed data in structured formats for analysis.

2. **Similarity Scoring**:
   - Implements a modified version of the **ALINE algorithm** for phonetic similarity analysis.
   - The algorithm was adapted from the original `abydos` library to resolve mismatches in phoneme representation and improve accuracy.

3. **Dockerized Environment**:
   - A lightweight `Dockerfile` to encapsulate dependencies, including Python libraries (`phonemizer`, `pandas`) and system tools (`festival`, `espeak`).

4. **Features**:
   - Batch processing for large datasets with multiprocessing support.
   - Gender and age categorization for drug-specific attributes.
   - Detailed similarity matrices for pairwise drug name comparisons.

### Use Cases
- LASA (Look-Alike, Sound-Alike) error reduction in drug labeling.
- Phonetic analysis and clustering of drug names for regulatory compliance.
- Data preprocessing and validation for pharmaceutical datasets.

### Getting Started
1. Build the Docker image:
   ```bash
   docker build -t phonemizer .
   ```
2. Run the container:
   ```bash
   docker run -it --rm phonemizer
   ```

### Notes
- The `aline_abydos.py` module modifies the original `abydos` implementation to resolve phoneme mismatches and ensure compatibility with the phonemized output.
