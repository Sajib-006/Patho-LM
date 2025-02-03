import pandas as pd
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

def stratified_sampling(df, sample_size=5000):
    label_counts = df['label'].value_counts()
    min_count = label_counts.min()
    sample_size = min(sample_size, min_count)
    sampled_df = df.groupby('label').apply(lambda x: x.sample(n=sample_size, random_state=42)).reset_index(drop=True)
    return sampled_df

def fasta_to_df(fasta_file):
    unique_ids = []
    species = []
    sequence_lengths = []
    labels = []
    fragment_ids = []
    sequences = []

    for record in SeqIO.parse(fasta_file, "fasta"):
        unique_ids.append(record.description.split(' ')[0]) 
        
        desc_parts = record.description.split(' ', 1)[1] if ' ' in record.description else ''
        try:
            desc_parts_dict = {part.split(':')[0].strip(): part.split(':')[1].strip() for part in desc_parts.split('|')}
        except Exception as e:
            print(f"Error parsing description for record {record.id}: {e}")
            continue 

        species.append(desc_parts_dict.get('species'))
        sequence_lengths.append(int(desc_parts_dict.get('sequence_length', 0))) 
        labels.append(desc_parts_dict.get('label'))
        sequences.append(str(record.seq))
    
   
    df = pd.DataFrame({
        'unique_id': unique_ids,
        'species': species,
        'sequence_length': sequence_lengths,
        'label': labels,
        'sequence': sequences
    })
    
    return df