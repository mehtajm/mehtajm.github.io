# Jai Mehta
# 03/29/2025
# Nyl12 Parser
from Bio import AlignIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import re
import tempfile
import os
from Bio import SeqIO
def parse_ranges(input_str):
    elements = input_str.split(',')
    result = []
    prev_value = None
    
    for elem in elements:
        if re.match(r'^[A-Za-z]', elem):
            prev_value = int(elem.split('-')[1])
        else:
            range_values = list(map(int, elem.split('-')))
            size = max(range_values) + 1  # Use the higher value of the two
            result.append((prev_value, size))
            prev_value = None  # Reset prev_value after using it
    
    return result
  
def split_by_repeating_substring(input_str):
    if len(input_str) < 25:
        return [(0, len(input_str), input_str)]  # Handle small strings

    pattern = input_str[:25]  # First 25 characters
    segments = []
    start_idx = 0
    search_idx = 25  # Start searching after the first 25 characters

    while True:
        next_idx = input_str.find(pattern, search_idx)  # Find next occurrence
        if next_idx == -1:
            break  # No more occurrences

        segments.append((start_idx, next_idx - start_idx, input_str[start_idx:next_idx]))
        start_idx = next_idx
        search_idx = next_idx + 25  # Move forward

    # Add final segment
    segments.append((start_idx, len(input_str) - start_idx, input_str[start_idx:]))

    return segments

def run_msa(input_sequences):
    # You should add current working directory here
    with open("temp_sequences.fasta", "w") as f:
        for i, (_, _, seq) in enumerate(input_sequences):
            f.write(f">chain_{chr(i + 97)}\n{seq}\n")
    print(f"")
    # Run MAFFT alignment (adjust paths if necessary)
    os.system(f"mafft temp_sequences.fasta > out.fa 2>/dev/null") # 2>/dev/null silences stderr if you want
    alignment = AlignIO.read("out.fa", "fasta")
    os.system("rm temp_sequences.fasta out.fa")
    return alignment

def correct_alignment(aligned_sequences, contigs):
    #
    seq_length = len(aligned_sequences[0].seq)
    num_sequences = len(aligned_sequences)
    
    for i in range(seq_length):
        column_chars = [seq.seq[i] for seq in aligned_sequences]
        unique_chars = set(column_chars)
        
        if len(unique_chars) > 1:  # Found a difference
            for seq_index, char in enumerate(column_chars):
                if column_chars.count(char) == 1:  # Identify differing sequence
                    adjusted_index = (seq_index * seq_length) + i
                    
                    if any(start <= adjusted_index < start + length for start, length in contigs):
                        for seq in aligned_sequences:
                            seq.seq = Seq(seq.seq[:i] + char + seq.seq[i+1:])  # Correct others
    
    return aligned_sequences
def remove_gaps(aligned_sequences):
    for seq in aligned_sequences:
        seq.seq = Seq(str(seq.seq).replace("-", ""))
    return aligned_sequences

def extract_beta_strings(final_sequences):
    marker = "TTLTIVIT"
#    marker = "TTIG"
    new_sequences = []

    for name, record in enumerate(final_sequences):
        seq_str = str(record.seq)

        if marker in seq_str:
            alpha_part, beta_part = seq_str.split(marker, 1)  # Split at first occurrence of marker
            beta_part = marker + beta_part
            # Create new sequence records with modified names
            alpha_record = SeqRecord(Seq(alpha_part), id=f"{record.id}_alpha", description="")
            beta_record = SeqRecord(Seq(beta_part), id=f"{record.id}_beta", description="")

            new_sequences.extend([alpha_record, beta_record])
        else:
            # If the marker isn't found, keep the sequence with a modified name
            unchanged_record = SeqRecord(Seq(seq_str), id=f"{record.id}_unchanged", description="")
            new_sequences.append(unchanged_record)

    return new_sequences

contigs = "A1-152, 9-9,A162-221,10-10,A232-1037,12-12,A1050-1079,4-12,A1092-1311"
sequence = "MAASSTDNILHFDFPEVQIGTAINPEGPTGITLFYFPKGVQASVDIQGGSVGTFFTQEKMQQGEAYLDGVAFTGGGILGLEAVAGAVSSLFADQTKNEVQFRRMPLISGAVIFDYTPRQNMIYPDKALGQKAFAALSAGQFVQGRHGAGVSAZZZZZZZZZFQLAGQGGAFAQIGKTKIAVFTVVNAVGVILDEKGEVIYGLPKGATKQTLNQQVTELLQQZZZZZZZZZZNTTLTIVITNEKLAPRHLKQLGRQVHHALSQVIHPYATILDGDVLYTVSTRSIESDLYAPGADIESDLNAKFIYLGMVAGELAKQAVWSAVGYSHRPMAASSTDNILHFDFPEVQIGTAINPEGPTGITLFYFPKGVQASVDIQGGSVGTFFTQEKMQQGEAYLDGVAFTGGGILGLEAVAGAVSSLFADQTKNEVQFRRMPLISGAVIFDYTPRQNMIYPDKALGQKAFAALSAGQFVQGRHGAGVSASVGKLLRDGFQLAGQGGAFAQIGKTKIAVFTVVNAVGVILDEKGEVIYGLPKGATKQTLNQQVTELLQQPKKPFWPEPKNTTLTIVITNEKLAPRHLKQLGRQVHHALSQVIHPYATILDGDVLYTVSTRSIESDLYAPGADIESDLNAKFIYLGMVAGELAKQAVWSAVGYSHRPMAASSTDNILHFDFPEVQIGTAINPEGPTGITLFYFPKGVQASVDIQGGSVGTFFTQEKMQQGEAYLDGVAFTGGGILGLEAVAGAVSSLFADQTKNEVQFRRMPLISGAVIFDYTPRQNMIYPDKALGQKAFAALSAGQFVQGRHGAGVSASVGKLLRDGFQLAGQGGAFAQIGKTKIAVFTVVNAVGVILDEKGEVIYGLPKGATKQTLNQQVTELLQQPKKPFWPEPKNTTLTIVITNEKLAPRHLKQLGRQVHHALSQVIHPYATILDGDVLYTVSTRSIESDLYAPGADIESDLNAKFIYLGMVAGELAKQAVWSAVGYSHRPMAASSTDNILHFDFPEVQIGTAINPEGPTGITLFYFPKGVQASVDIQGGSVGTZZZZZZZZZZZZYLDGVAFTGGGILGLEAVAGAVSSLFADQTZZZZZZSGAVIFDYTPRQNMIYPDKALGQKAFAALSAGQFVQGRHGAGVSASVGKLLRDGFQLAGQGGAFAQIGKTKIAVFTVVNAVGVILDEKGEVIYGLPKGATKQTLNQQVTELLQQPKKPFWPEPKNTTLTIVITNEKLAPRHLKQLGRQVHHALSQVIHPYATILDGDVLYTVSTRSIESDLYAPGADIESDLNAKFIYLGMVAGELAKQAVWSAVGYSHRP"
segments = split_by_repeating_substring(sequence)
aligned_sequences = run_msa(segments)
corrected_sequences = correct_alignment(aligned_sequences, parse_ranges(contigs))
final_sequences = remove_gaps(corrected_sequences)
split_sequences = extract_beta_strings(final_sequences)
for record in split_sequences:
    print(record.id, record.seq)
