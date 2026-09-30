import os
import sys
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


class DynamicGestureLSTM(nn.Module):
    """
    Bidirectional LSTM neural network for dynamic ISL sequence recognition.
    Processes temporal sequences of 206-dimensional dual-hand feature vectors.
    """
    def __init__(self, input_dim=206, hidden_dim=64, num_classes=13, num_layers=2):
        super(DynamicGestureLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(64, num_classes)
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_dim)
        lstm_out, _ = self.lstm(x)
        last_out = lstm_out[:, -1, :]
        out = self.fc1(last_out)
        out = self.relu(out)
        out = self.dropout(out)
        logits = self.fc2(out)
        return logits


def load_real_sequences():
    """
    Loads real ISL sequence dataset from processed numpy files.
    Returns (X, y, class_names) or (None, None, None) if no real data available.
    """
    processed_dir = os.path.join(PROJECT_ROOT, "dataset", "processed")
    x_path = os.path.join(processed_dir, "X_sequences.npy")
    y_path = os.path.join(processed_dir, "y_sequences.npy")
    classes_path = os.path.join(processed_dir, "class_names.json")

    if not os.path.exists(x_path) or not os.path.exists(y_path):
        return None, None, None

    X = np.load(x_path)
    y = np.load(y_path)

    if len(X) == 0:
        return None, None, None

    # Load class names
    class_names = []
    if os.path.exists(classes_path):
        with open(classes_path, "r") as f:
            class_names = json.load(f)
    else:
        # Infer from unique labels
        class_names = [f"CLASS_{i}" for i in range(max(y) + 1)]

    # Add UNKNOWN_GESTURE class if not present
    if "UNKNOWN_GESTURE" not in class_names:
        class_names.append("UNKNOWN_GESTURE")

    print(f"Loaded real sequence dataset: {X.shape} ({len(class_names)} classes)")
    return X, y, class_names


DYNAMIC_ISL_CLASSES = [
    "HELLO",       # 0 (1-hand lateral wave)
    "THANK YOU",   # 1 (1-hand chin to forward descent)
    "YES",         # 2 (1-hand vertical nod)
    "NO",          # 3 (1-hand finger snap / lateral wag)
    "HELP",        # 4 (2-hand base lift upward)
    "BOOK",        # 5 (2-hand open outward)
    "TIME",        # 6 (2-hand wrist tapping)
    "STOP",        # 7 (2-hand descending chop on palm)
    "WORK",        # 8 (2-hand wrist tapping)
    "SORRY",       # 9 (1-hand chest circle)
    "PLEASE",      # 10 (1-hand chest circle)
    "WATER",       # 11 (1-hand tilt drink)
    "UNKNOWN_GESTURE" # 12 (unstructured / negative)
]


def generate_synthetic_sequences(num_samples_per_class=90, seq_len=20, input_dim=206):
    """
    Generates synthetic temporal motion trajectories as FALLBACK only.
    Prints a warning that real data should be used instead.
    """
    print("\n" + "!" * 60)
    print("  WARNING: No real ISL sequence data found!")
    print("  Training on SYNTHETIC sequences (low accuracy).")
    print("  For real ISL recognition, collect data first:")
    print("    python ml/datasets/collect_data.py")
    print("    python ml/datasets/process_data.py")
    print("!" * 60 + "\n")

    X = []
    y = []
    time_steps = np.linspace(0, 1, seq_len)
    
    for c_idx, sign in enumerate(DYNAMIC_ISL_CLASSES):
        for _ in range(num_samples_per_class):
            sequence = np.zeros((seq_len, input_dim), dtype=np.float32)
            noise = np.random.uniform(0.01, 0.03)
            
            for t_idx, t in enumerate(time_steps):
                base_vec = np.random.normal(0, noise, size=input_dim).astype(np.float32)
                
                # Setup presence flags in base_vec (indices 186..188)
                if sign in ["HELP", "BOOK", "TIME", "STOP", "WORK"]:
                    base_vec[186] = 1.0
                    base_vec[187] = 1.0
                    base_vec[188] = 2.0
                elif sign != "UNKNOWN_GESTURE":
                    base_vec[187] = 1.0
                    base_vec[188] = 1.0
                
                # Add motion dynamics
                if sign == "HELLO":
                    base_vec[93:114] += np.sin(t * 3 * np.pi) * 0.25
                elif sign == "THANK YOU":
                    base_vec[114:135] += (1.0 - t) * 0.22
                elif sign == "YES":
                    base_vec[114:135] += np.sin(t * 4 * np.pi) * 0.18
                elif sign == "NO":
                    base_vec[156:171] += t * 0.35
                elif sign == "HELP":
                    base_vec[21:42] -= t * 0.25
                    base_vec[114:135] -= t * 0.25
                    base_vec[192] = 0.15
                elif sign == "BOOK":
                    base_vec[0:21] -= t * 0.20
                    base_vec[93:114] += t * 0.20
                    base_vec[200] = np.cos(t * np.pi)
                elif sign == "TIME":
                    base_vec[198] = np.abs(np.sin(t * 6 * np.pi)) * 0.08
                elif sign == "STOP":
                    base_vec[114:135] += t * 0.30
                    base_vec[200] = 0.0
                elif sign == "WORK":
                    base_vec[192] = np.abs(np.sin(t * 4 * np.pi)) * 0.1
                elif sign == "SORRY":
                    base_vec[93:114] += np.cos(t * 3 * np.pi) * 0.12
                    base_vec[114:135] += np.sin(t * 3 * np.pi) * 0.12
                elif sign == "PLEASE":
                    base_vec[93:114] += np.cos(t * 2 * np.pi) * 0.14
                    base_vec[114:135] += np.sin(t * 2 * np.pi) * 0.14
                elif sign == "WATER":
                    base_vec[114:135] -= t * 0.18
                    base_vec[156:171] += 0.2
                elif sign == "UNKNOWN_GESTURE":
                    base_vec += np.random.normal(0, 0.08, size=input_dim).astype(np.float32)
                    
                sequence[t_idx] = base_vec
                
            X.append(sequence)
            y.append(c_idx)
            
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64), DYNAMIC_ISL_CLASSES


def train_lstm_model():
    # 1. Try to load real sequence data first
    print("Attempting to load real ISL sequence dataset...")
    X, y, class_names = load_real_sequences()

    # 2. Fall back to synthetic if no real data
    if X is None or len(X) == 0:
        X, y, class_names = generate_synthetic_sequences(num_samples_per_class=90, seq_len=20, input_dim=206)
        data_source = "synthetic"
    else:
        print(f"\n[OK] Using REAL ISL dataset for LSTM training!")
        data_source = "real"

    print(f"Dataset: {len(X)} sequences of shape {X.shape[1:]} for {len(class_names)} classes.")
    
    indices = np.random.permutation(len(X))
    split = int(0.85 * len(X))
    train_idx, val_idx = indices[:split], indices[split:]
    
    X_train, y_train = torch.tensor(X[train_idx]), torch.tensor(y[train_idx])
    X_val, y_val = torch.tensor(X[val_idx]), torch.tensor(y[val_idx])
    
    model = DynamicGestureLSTM(input_dim=206, hidden_dim=64, num_classes=len(class_names), num_layers=2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-4)
    
    print("Training PyTorch Bidirectional LSTM model for dynamic ISL...")
    epochs = 40
    batch_size = 32
    
    for epoch in range(epochs):
        model.train()
        permutation = torch.randperm(len(X_train))
        epoch_loss = 0.0
        
        for i in range(0, len(X_train), batch_size):
            indices_b = permutation[i:i + batch_size]
            batch_x, batch_y = X_train[indices_b], y_train[indices_b]
            
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(batch_x)
            
        epoch_loss /= len(X_train)
        
        if (epoch + 1) % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                val_outputs = model(X_val)
                val_preds = torch.argmax(val_outputs, dim=1)
                val_acc = (val_preds == y_val).float().mean().item()
            print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss:.4f} - Val Acc: {val_acc * 100:.2f}%")
            
    # Save checkpoint
    target_dirs = [
        os.path.join(PROJECT_ROOT, "models"),
        os.path.join(PROJECT_ROOT, "backend", "models")
    ]
    
    checkpoint_data = {
        "model_state_dict": model.state_dict(),
        "classes": class_names,
        "input_dim": 206,
        "hidden_dim": 64,
        "num_layers": 2,
        "data_source": data_source
    }
    
    for t_dir in target_dirs:
        os.makedirs(t_dir, exist_ok=True)
        ckpt_path = os.path.join(t_dir, "dynamic_gesture_lstm.pt")
        torch.save(checkpoint_data, ckpt_path)
        print(f"Saved PyTorch LSTM checkpoint to: {ckpt_path}")

    # Save training metadata
    meta = {
        "trained_at": __import__("datetime").datetime.now().isoformat(),
        "total_sequences": len(X),
        "val_accuracy": round(val_acc, 4),
        "num_classes": len(class_names),
        "class_names": class_names,
        "data_source": data_source,
        "model_type": "BiLSTM",
        "hidden_dim": 64,
        "num_layers": 2,
        "epochs": epochs
    }
    meta_path = os.path.join(PROJECT_ROOT, "models", "lstm_model_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Training metadata saved to: {meta_path}")


if __name__ == "__main__":
    train_lstm_model()
