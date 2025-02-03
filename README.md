# PathoLM

## Setup

### Install Dependencies

```
pip install -r requirements.txt
```

## Input File Format

The input file should be in FASTA format. Each sequence entry should contain a header line starting with** **`<span>></span>` followed by metadata, and a sequence line containing the DNA sequence.

### Example:

```
>unique_id species:SpeciesName|sequence_length:XXXXX|label:pathogen
ATGCTAGCTAGCTGATCGATCGATCGATCGTACGTAGCTAGCTGATCG
```

Each header should contain:

* `<span>unique_id</span>`: A unique identifier for the sequence
* `<span>species</span>`: The species name
* `<span>sequence_length</span>`: The length of the DNA sequence
* `<span>label</span>`: The classification label (e.g.,** **`<span>pathogen</span>` or** **`<span>non-pathogen</span>`)

Ensure that each sequence entry follows this format to be correctly parsed by the model.

## Model Weights Download

The model weights are not included in this repository due to their large size. Please download the model weights from Zenodo:

[Download Model Weights](https://zenodo.org/records/14791889)

### Steps to Use:

1. Download the model weights from the above Zenodo link.
2. Create a directory named** **`<span>ckpt</span>` in the repository:
   ```
   mkdir ckpt
   ```
3. Move the downloaded model weight files into the** **`<span>ckpt</span>` directory.
4. Run the evaluation script as described in the usage section.

## Usage

### Evaluate on Test Dataset

```
python eval_model.py --model_path ckpt/patholm_binary_2k_mmseq40 --test_file test.fasta
```

### Evaluate Single Sequence

```
python eval_model.py --model_path ckpt/patholm_binary_2k_mmseq40 --sequence "AGCTGATCG..."
```
