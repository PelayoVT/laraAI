import torch

print("Torch version:", torch.__version__)
print("CUDA disponible:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("Nombre de GPU:", torch.cuda.get_device_name(0))
    print("Número de GPUs disponibles:", torch.cuda.device_count())
    print("Memoria total:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2), "GB")
else:
    print("No se detectó una GPU CUDA.")