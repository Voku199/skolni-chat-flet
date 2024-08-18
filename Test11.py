import tensorflow as tf

# Zkontrolujte, zda TensorFlow detekuje GPU
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Pokud máte GPU, TensorFlow by mělo automaticky použít GPU pro trénování
