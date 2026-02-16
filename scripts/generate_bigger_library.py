"""
Uses the examle yeast_1000.mfg file to create a bigger example for run time analysis.
"""

#!/usr/bin/env python

import re
from typing import List, Dict, Tuple
import random

def read_msp(filename: str) -> List[Dict]:
    """
    Parse an .msp file into a list of spectra dictionaries.
    
    Each spectrum dict contains:
      - 'name': str
      - 'mw': float (precursor m/z)
      - 'comment': str
      - 'num_peaks': int
      - 'peaks': List[Tuple[float, float, str]]  # (mz, intensity, annotation)
    """
    spectra = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Initialize spectrum dict
        spectrum = {
            'name': '',
            'mw': None,
            'comment': '',
            'num_peaks': 0,
            'peaks': []
        }

        # Parse header lines
        while i < len(lines) and lines[i].strip() and ':' in lines[i]:
            key, value = lines[i].split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'name':
                spectrum['name'] = value
            elif key == 'mw' or key == 'precursor_mz':
                spectrum['mw'] = float(value)
            elif key == 'comment':
                spectrum['comment'] = value
            elif key == 'num peaks':
                spectrum['num_peaks'] = int(value)
            i += 1

        # Parse peaks
        peak_count = 0
        while i < len(lines) and peak_count < spectrum['num_peaks']:
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            # Split by whitespace (handles tabs/spaces)
            parts = line.split()
            if len(parts) < 2:
                i += 1
                continue
            mz = float(parts[0])
            intensity = float(parts[1])
            annotation = ''
            if len(parts) >= 3:
                # Annotation may be quoted; remove quotes
                anno_raw = ' '.join(parts[2:])
                annotation = re.sub(r'^["\']|["\']$', '', anno_raw)
            spectrum['peaks'].append((mz, intensity, annotation))
            peak_count += 1
            i += 1

        # Only append if we actually read a spectrum
        if spectrum['name']:
            spectra.append(spectrum)

    return spectra

import random
from typing import List, Dict

def add_new_spectra(spectra: List[Dict], goal: int, mw_noise_std: float = 10) -> List[Dict]:
    """
    Generate new spectra by shuffling intensities and adding noise to precursor m/z.
    
    Parameters:
        spectra: original list of spectra
        goal: total number of spectra desired
        mw_noise_std: standard deviation of Gaussian noise added to MW (in Th)
    """
    if len(spectra) == 0:
        return spectra

    # Start with deep copies of originals
    result = [spec.copy() for spec in spectra]
    for spec in result:
        spec['peaks'] = list(spec['peaks'])  # ensure peaks are mutable

    while len(result) < goal:
        base_idx = (len(result) - len(spectra)) % len(spectra)
        base_spec = result[base_idx]

        # Shuffle intensities
        mz_vals, inten_vals, annos = zip(*base_spec['peaks'])
        inten_list = list(inten_vals)
        random.shuffle(inten_list)
        new_peaks = [(mz, inten, anno) for mz, inten, anno in zip(mz_vals, inten_list, annos)]

        # Add Gaussian noise to precursor m/z (MW)
        noisy_mw = base_spec['mw'] + random.gauss(0, mw_noise_std)

        # Ensure MW stays positive (safety)
        noisy_mw = max(noisy_mw, 0.1)

        # Build new spectrum
        new_spec = {
            'name': base_spec['name'],
            'mw': noisy_mw,
            'comment': base_spec['comment'],  # note: Comment still has old Parent=... value
            'num_peaks': len(new_peaks),
            'peaks': new_peaks
        }

        result.append(new_spec)

    return result

def write_msp(filename: str, spectra: List[Dict]):
    with open(filename, 'w') as f:
        for spec in spectra:
            f.write(f"Name: {spec['name']}\n")
            f.write(f"MW: {spec['mw']:.6f}\n")
            f.write(f"Comment: {spec['comment']}\n")
            f.write(f"Num peaks: {len(spec['peaks'])}\n")
            for mz, intensity, annotation in spec['peaks']:
                if annotation:
                    f.write(f"{mz:.6f}\t{intensity:.6f}\t\"{annotation}\"\n")
                else:
                    f.write(f"{mz:.6f}\t{intensity:.6f}\n")
            f.write("\n")  # blank line between spectra

spectra = read_msp('/home/malekk/Mistle/example/yeast_1000.msp')
goal = 5000000
spectra = add_new_spectra(spectra, goal)
write_msp('/home/malekk/Mistle/example/yeast_bigger.msp', spectra)