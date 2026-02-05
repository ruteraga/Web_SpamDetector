"""
Script to convert/re-save the Keras model for TensorFlow 2.12.0 compatibility.

The error "Unrecognized keyword arguments: ['batch_shape']" occurs because
the model was saved with a newer TensorFlow version that uses different
serialization format for InputLayer.

Solutions:
1. Upgrade TensorFlow (recommended but may have other implications)
2. Re-save the model with TF 2.12.0
3. Reconstruct the model architecture manually
"""

import tensorflow as tf
import numpy as np

# Option 1: Try loading with compatibility mode
try:
    print("Attempting to load model with legacy format...")
    model = tf.keras.models.load_model(
        'data/text_model.keras',
        custom_objects=None,
        compile=False  # Don't compile, just load architecture
    )
    print("✓ Model loaded successfully!")
    
    # Re-save in compatible format
    print("Re-saving model in TF 2.12.0 compatible format...")
    model.save('data/text_model_compatible.keras')
    print("✓ Model saved as 'text_model_compatible.keras'")
    
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    print("\nOption 2: You need to either:")
    print("  1. Upgrade TensorFlow to match the version used to create the model")
    print("  2. Re-train the model with TensorFlow 2.12.0")
    print("  3. Export the model architecture from the original environment")