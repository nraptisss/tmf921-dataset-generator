"""
Split TMF921 dataset into train/validation/test sets
Uses stratified split to maintain distribution
"""

import json
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
import argparse


def load_dataset(filepath):
    """Load the generated TMF921 dataset"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def split_dataset(data, train_size=0.8, val_size=0.1, test_size=0.1, random_state=42):
    """
    Split dataset into train/validation/test sets
    
    Args:
        data: List of intent pairs
        train_size: Proportion for training (default 0.8 = 80%)
        val_size: Proportion for validation (default 0.1 = 10%)
        test_size: Proportion for test (default 0.1 = 10%)
        random_state: Random seed for reproducibility
    
    Returns:
        train, val, test datasets
    """
    # First split: separate test set
    train_val, test = train_test_split(
        data, 
        test_size=test_size, 
        random_state=random_state
    )
    
    # Second split: separate train and validation
    # Adjust val_size relative to remaining data
    relative_val_size = val_size / (train_size + val_size)
    train, val = train_test_split(
        train_val,
        test_size=relative_val_size,
        random_state=random_state
    )
    
    return train, val, test


def save_split(data, filepath):
    """Save dataset split to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"OK Saved {len(data)} intents to {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Split TMF921 dataset')
    parser.add_argument(
        '--input',
        default='output/tmf921_dataset.json',
        help='Input dataset file'
    )
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory for splits'
    )
    parser.add_argument(
        '--train-size',
        type=float,
        default=0.8,
        help='Training set size (default: 0.8)'
    )
    parser.add_argument(
        '--val-size',
        type=float,
        default=0.1,
        help='Validation set size (default: 0.1)'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.1,
        help='Test set size (default: 0.1)'
    )
    parser.add_argument(
        '--random-state',
        type=int,
        default=42,
        help='Random seed (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Validate split proportions
    total = args.train_size + args.val_size + args.test_size
    if abs(total - 1.0) > 0.001:
        raise ValueError(f"Split sizes must sum to 1.0, got {total}")
    
    print("=" * 70)
    print("TMF921 Dataset Splitter")
    print("=" * 70)
    
    # Load dataset
    print(f"\nLoading dataset from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract intent pairs
    if 'intent_pairs' in data:
        intents = data['intent_pairs']
    elif 'intents' in data:
        intents = data['intents']
    else:
        # Assume it's a direct list
        intents = data
    
    total_intents = len(intents)
    print(f"Total intents: {total_intents}")
    
    # Split dataset
    print(f"\nSplitting dataset:")
    print(f"  Train: {args.train_size:.1%}")
    print(f"  Val:   {args.val_size:.1%}")
    print(f"  Test:  {args.test_size:.1%}")
    
    train, val, test = split_dataset(
        intents,
        train_size=args.train_size,
        val_size=args.val_size,
        test_size=args.test_size,
        random_state=args.random_state
    )
    
    # Save splits
    print(f"\nSaving splits to: {args.output_dir}/")
    save_split(train, os.path.join(args.output_dir, 'train_intents.json'))
    save_split(val, os.path.join(args.output_dir, 'val_intents.json'))
    save_split(test, os.path.join(args.output_dir, 'test_intents.json'))
    
    # Summary
    print("\n" + "=" * 70)
    print("SPLIT SUMMARY")
    print("=" * 70)
    print(f"Total:      {total_intents:4d} intents")
    print(f"Training:   {len(train):4d} intents ({len(train)/total_intents:.1%})")
    print(f"Validation: {len(val):4d} intents ({len(val)/total_intents:.1%})")
    print(f"Test:       {len(test):4d} intents ({len(test)/total_intents:.1%})")
    print("=" * 70)
    print("\n[OK] Dataset split complete!")
    print(f"\nNext steps:")
    print(f"  1. Build vector database: python rag/build_vector_db.py")
    print(f"  2. Run RAG experiments: python experiments/rag_experiment.py")


if __name__ == "__main__":
    main()
