import numpy as np
from TConv2D import TConv2D
from Dense import Dense

class Generator:
    def __init__(self, batch_size):
        self.layers = [
            Dense(batch_size=batch_size, input_shape=(1, 1, 100), num_neurons=8 * 8 * 256, activation="lrelu", batch_norm=True),
            TConv2D(batch_size=batch_size, input_shape=(8, 8, 256), num_filters=128, kernel_size=4, stride=2, padding=1, activation="lrelu", batch_norm=True),
            TConv2D(batch_size=batch_size, input_shape=(16, 16, 128), num_filters=64, kernel_size=4, stride=2, padding=1, activation="lrelu", batch_norm=True),
            TConv2D(batch_size=batch_size, input_shape=(32, 32, 64), num_filters=3, kernel_size=4, stride=2, padding=1, activation="tanh")
        ]
        
        self.W_deltas = [np.zeros_like(layer.W) if hasattr(layer, 'W') else None for layer in self.layers]
        self.B_deltas = [np.zeros_like(layer.B) if hasattr(layer, 'B') else None for layer in self.layers]

    def applyDeltas(self, learning_rate):
        for layer_index in range(len(self.layers)):
            if hasattr(self.layers[layer_index], 'W'):
                self.layers[layer_index].W -= learning_rate * self.W_deltas[layer_index]
                self.layers[layer_index].B -= learning_rate * self.B_deltas[layer_index]
    def resetDeltas(self):
        for layer_index in range(len(self.layers)):
            if hasattr(self.layers[layer_index], 'W'):
                self.W_deltas[layer_index].fill(0)
                self.B_deltas[layer_index].fill(0)
    def forward(self, x):
        for layer in self.layers:
            x = layer.forward(x)
        return x
    def backward(self, gradient):
        current_gradient = gradient
        for layer_index in range(len(self.layers) -1, -1, -1):
            current_gradient = self.layers[layer_index].backward(current_gradient, self.W_deltas[layer_index], self.B_deltas[layer_index])
        return current_gradient

    def state_dict(self):
        state = {}
        for i, layer in enumerate(self.layers):
            if hasattr(self.layers[i], 'W'):
                state[f"layer_{i}_W"] = layer.W
                state[f"layer_{i}_B"] = layer.B
            if hasattr(self.layers[i], 'scale'):
                state[f"layer_{i}_scale"] = layer.scale
                state[f"layer_{i}_shift"] = layer.shift
                state[f"layer_{i}_running_mean"] = layer.running_mean
                state[f"layer_{i}_running_var"] = layer.running_var
        return state

    def load_state_dict(self, state):
        for i, layer in enumerate(self.layers):
            if hasattr(self.layers[i], 'W'):
                layer.W = state[f"layer_{i}_W"]
                layer.B = state[f"layer_{i}_B"]
            if hasattr(self.layers[i], 'scale'):
                layer.scale = state[f"layer_{i}_scale"]
                layer.shift = state[f"layer_{i}_shift"]
                layer.running_mean = state[f"layer_{i}_running_mean"]
                layer.running_var = state[f"layer_{i}_running_var"]
