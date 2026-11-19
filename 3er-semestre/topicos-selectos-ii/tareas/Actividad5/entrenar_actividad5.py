# -*- coding: utf-8 -*-
"""
Actividad 5 - CNN para clasificación de Pokémon (Tópicos Selectos de GBD II).
Trains the professor's TinyVGG (IvTole/Pokemon_Classification, src/) and the EfficientNet-B0
transfer-learning model from his notebook, and saves every number and prediction the report uses.

Experiments (fixed seeds):
  E1  professor's setup as is: test = 15 images per class COPIED from train (get_data.py),
      same augmented transform for train and test, 10 epochs (molab notebook)
  E2  same TinyVGG, clean split: the 15 test images per class are REMOVED from train,
      test without augmentation, 30 epochs
  E3  E2 without data augmentation
  E4  EfficientNet-B0 pretrained on ImageNet, frozen features, new 151-class head, clean split,
      5 epochs (professor's notebook)
The engine (train_step / test_step / train) and TinyVGG are the professor's code, unchanged.
Images are decoded once and cached as uint8 tensors (64x64 and 224x224); the transforms that
follow the resize are the same ones the professor uses.
"""
import json
import os
import random
import time

import numpy as np
import torch
import torchvision
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import functional as TF
from tqdm.auto import tqdm
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "datos", "pokemon", "PokemonData")
CACHE = os.path.join(HERE, "..", "..", "datos", "pokemon", "cache")
RES = os.path.join(HERE, "resultados")
MODELOS = os.path.join(HERE, "models")
SEED = 42
N_TEST = 15
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EXT = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")


# ============================ professor's code (src/model_builder.py) ====================
class TinyVGG(nn.Module):
    def __init__(self, input_shape: int, hidden_units: int, output_shape: int) -> None:
        super().__init__()
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=input_shape, out_channels=hidden_units, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(hidden_units, hidden_units, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.Conv2d(hidden_units, hidden_units, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units * 13 * 13, out_features=output_shape))

    def forward(self, x: torch.Tensor):
        return self.classifier(self.conv_block_2(self.conv_block_1(x)))


# ============================ professor's code (src/engine.py) ===========================
def train_step(model, dataloader, loss_fn, optimizer, device) -> Tuple[float, float]:
    model.train()
    train_loss, train_acc = 0, 0
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        y_pred = model(X)
        loss = loss_fn(y_pred, y)
        train_loss += loss.item()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        y_pred_class = torch.argmax(torch.softmax(y_pred, dim=1), dim=1)
        train_acc += (y_pred_class == y).sum().item() / len(y_pred)
    return train_loss / len(dataloader), train_acc / len(dataloader)


def test_step(model, dataloader, loss_fn, device) -> Tuple[float, float]:
    model.eval()
    test_loss, test_acc = 0, 0
    with torch.inference_mode():
        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)
            test_pred_logits = model(X)
            loss = loss_fn(test_pred_logits, y)
            test_loss += loss.item()
            test_pred_labels = test_pred_logits.argmax(dim=1)
            test_acc += ((test_pred_labels == y).sum().item() / len(test_pred_labels))
    return test_loss / len(dataloader), test_acc / len(dataloader)


def train(model, train_dataloader, test_dataloader, optimizer, loss_fn, epochs, device) -> Dict[str, List]:
    results = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": []}
    for epoch in tqdm(range(epochs)):
        train_loss, train_acc = train_step(model, train_dataloader, loss_fn, optimizer, device)
        test_loss, test_acc = test_step(model, test_dataloader, loss_fn, device)
        print(f"Epoch: {epoch+1} | train_loss: {train_loss:.4f} | train_acc: {train_acc:.4f} | "
              f"test_loss: {test_loss:.4f} | test_acc: {test_acc:.4f}")
        results["train_loss"].append(train_loss)
        results["train_acc"].append(train_acc)
        results["test_loss"].append(test_loss)
        results["test_acc"].append(test_acc)
    return results


# ============================ data =======================================================
def cargar_cache():
    """Decodes every image once: 64x64 (Resize((64,64)), as in train.py) and 224x224
    (EfficientNet_B0_Weights.DEFAULT.transforms(): resize 256 bicubic + center crop 224)."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, "imagenes.pt")
    if os.path.exists(f):
        return torch.load(f)
    clases = sorted(d for d in os.listdir(DATA) if os.path.isdir(os.path.join(DATA, d)))
    r64 = transforms.Resize((64, 64))
    r224 = transforms.Compose([transforms.Resize(256, interpolation=transforms.InterpolationMode.BICUBIC),
                               transforms.CenterCrop(224)])
    x64, x224, y, rutas, malas = [], [], [], [], []
    for ci, c in enumerate(tqdm(clases)):
        for fn in sorted(os.listdir(os.path.join(DATA, c))):
            if not fn.lower().endswith(EXT):
                continue
            p = os.path.join(DATA, c, fn)
            try:
                im = Image.open(p).convert("RGB")
            except Exception:
                malas.append(p); continue
            x64.append(TF.pil_to_tensor(r64(im)))
            x224.append(TF.pil_to_tensor(r224(im)))
            y.append(ci); rutas.append(f"{c}/{fn}")
    d = {"x64": torch.stack(x64), "x224": torch.stack(x224), "y": torch.tensor(y),
         "clases": clases, "rutas": rutas, "malas": malas}
    torch.save(d, f)
    return d


class Imagenes(Dataset):
    """uint8 tensors -> the professor's transforms after the resize."""
    def __init__(self, x, y, idx, tf):
        self.x, self.y, self.idx, self.tf = x, y, idx, tf

    def __len__(self):
        return len(self.idx)

    def __getitem__(self, i):
        j = self.idx[i]
        return self.tf(self.x[j]), int(self.y[j])


def tf_tinyvgg(aumento):
    pasos = [transforms.RandomHorizontalFlip(), transforms.RandomRotation(25)] if aumento else []
    return transforms.Compose(pasos + [transforms.ConvertImageDtype(torch.float32),
                                       transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


TF_EFF = transforms.Compose([transforms.ConvertImageDtype(torch.float32),
                             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


def semillas():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed(SEED)


def loader(ds, shuffle):
    g = torch.Generator(); g.manual_seed(SEED)
    return DataLoader(ds, batch_size=32, shuffle=shuffle, num_workers=0, generator=g)


def predecir(model, dl):
    """Predicted class, whether the true class is in the top 5, and the top-5 softmax probabilities."""
    model.eval(); ys, ps, top5, t5i, t5p = [], [], [], [], []
    with torch.inference_mode():
        for X, y in dl:
            out = model(X.to(DEVICE))
            prob = torch.softmax(out, dim=1).topk(5, 1)
            ps.append(out.argmax(1).cpu()); ys.append(y)
            top5.append((prob.indices.cpu() == y[:, None]).any(1))
            t5i.append(prob.indices.cpu()); t5p.append(prob.values.cpu())
    return (torch.cat(ys).numpy(), torch.cat(ps).numpy(), torch.cat(top5).numpy(),
            torch.cat(t5i).numpy(), torch.cat(t5p).numpy())


def correr(nombre, model, ds_tr, ds_te, epochs, ds_eval=None):
    semillas()
    loss_fn = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    t0 = time.time()
    res = train(model, loader(ds_tr, True), loader(ds_te, False), opt, loss_fn, epochs, DEVICE)
    res["segundos"] = time.time() - t0
    y, p, t5, t5i, t5p = predecir(model, loader(ds_eval or ds_te, False))
    res["acc_final"] = float((y == p).mean()); res["top5"] = float(t5.mean())
    np.savez(os.path.join(RES, f"pred_{nombre}.npz"), y=y, p=p, top5_idx=t5i, top5_prob=t5p)
    # save the trained weights, as train.py does with utils.save_model (models/ is gitignored)
    os.makedirs(MODELOS, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(MODELOS, f"pokemon_{nombre}.pth"))
    res["params_total"] = sum(q.numel() for q in model.parameters())
    res["params_entrenables"] = sum(q.numel() for q in model.parameters() if q.requires_grad)
    print(nombre, "acc", res["acc_final"], "top5", res["top5"], "seg", round(res["segundos"]))
    return res


def main():
    os.makedirs(RES, exist_ok=True)
    print("device", DEVICE, torch.cuda.get_device_name(0) if DEVICE == "cuda" else "")
    d = cargar_cache()
    y, clases = d["y"], d["clases"]
    n_cls = len(clases)
    conteo = np.bincount(y.numpy(), minlength=n_cls)

    # get_data.py: random.sample(15) images per class become the test set
    random.seed(SEED)
    test_idx = []
    for c in range(n_cls):
        idx = np.where(y.numpy() == c)[0].tolist()
        test_idx += random.sample(idx, N_TEST)
    test_set = set(test_idx)
    todos = list(range(len(y)))
    train_limpio = [i for i in todos if i not in test_set]

    info = {"n_imagenes": len(y), "n_clases": n_cls, "malas": d["malas"],
            "conteo_min": int(conteo.min()), "conteo_max": int(conteo.max()),
            "conteo_mediana": float(np.median(conteo)), "conteo": conteo.tolist(), "clases": clases,
            "n_test": len(test_idx), "n_train_prof": len(todos), "n_train_limpio": len(train_limpio),
            "device": torch.cuda.get_device_name(0) if DEVICE == "cuda" else "cpu",
            "torch": torch.__version__, "torchvision": torchvision.__version__}
    json.dump({"test_idx": test_idx}, open(os.path.join(RES, "split.json"), "w"))

    R = {}
    x64 = d["x64"]
    # E1: professor's setup (train contains the test images; augmented transform on both)
    R["E1"] = correr("E1", TinyVGG(3, 64, n_cls).to(DEVICE),
                     Imagenes(x64, y, todos, tf_tinyvgg(True)), Imagenes(x64, y, test_idx, tf_tinyvgg(True)), 10,
                     ds_eval=Imagenes(x64, y, test_idx, tf_tinyvgg(False)))
    # E2: clean split, augmentation only on train
    R["E2"] = correr("E2", TinyVGG(3, 64, n_cls).to(DEVICE),
                     Imagenes(x64, y, train_limpio, tf_tinyvgg(True)), Imagenes(x64, y, test_idx, tf_tinyvgg(False)), 30)
    # E3: clean split, no augmentation
    R["E3"] = correr("E3", TinyVGG(3, 64, n_cls).to(DEVICE),
                     Imagenes(x64, y, train_limpio, tf_tinyvgg(False)), Imagenes(x64, y, test_idx, tf_tinyvgg(False)), 30)
    # E4: transfer learning, professor's notebook
    semillas()
    w = torchvision.models.EfficientNet_B0_Weights.DEFAULT
    m = torchvision.models.efficientnet_b0(weights=w).to(DEVICE)
    for q in m.features.parameters():
        q.requires_grad = False
    torch.manual_seed(SEED); torch.cuda.manual_seed(SEED)
    m.classifier = nn.Sequential(nn.Dropout(p=0.2, inplace=True),
                                 nn.Linear(in_features=1280, out_features=n_cls, bias=True)).to(DEVICE)
    R["E4"] = correr("E4", m, Imagenes(d["x224"], y, train_limpio, TF_EFF),
                     Imagenes(d["x224"], y, test_idx, TF_EFF), 5)

    json.dump({"info": info, "R": R}, open(os.path.join(RES, "resultados.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("listo")


if __name__ == "__main__":
    main()
