import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import os

class TileEncoderNet(nn.Module):

    def __init__(self, num_ids, embedding_dim, output_dim, rows, cols, **kwargs):
        super().__init__()
        self.embedding = nn.Embedding(num_ids, embedding_dim)
        self.pos_embedding = nn.Parameter(torch.randn(1, embedding_dim, rows, cols))
        
        self.spatial_conv = nn.Sequential(
            nn.Conv2d(embedding_dim, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, output_dim, kernel_size=3, padding=1),
            nn.ReLU()
        )
        
        self.reconstruction_head = nn.Conv2d(output_dim, num_ids, kernel_size=1)

    def forward(self, x, return_features=False):
        is_batch = x.ndim == 3
        if not is_batch:
            x = x.unsqueeze(0)
        x = self.embedding(x).permute(0, 3, 1, 2)
        x = x + self.pos_embedding
        features = self.spatial_conv(x)

        if return_features:
            return features.squeeze(0) if not is_batch else features
            
        logits = self.reconstruction_head(features)
        return logits.squeeze(0) if not is_batch else logits


class TileEncoder:

    def __init__(self, num_ids=65536, embedding_dim=8, output_dim=16, rows=14, cols=16, learning_rate=1e-3, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.params = {
            'num_ids': num_ids,
            'embedding_dim': embedding_dim,
            'output_dim': output_dim,
            'rows': rows,
            'cols': cols,
            'learning_rate': learning_rate}
        
        self.model = TileEncoderNet(**self.params).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.CrossEntropyLoss()

    def embed(self, observation):
        self.model.eval()
        with torch.no_grad():
            obs_tensor = self._ensure_tensor(observation).to(self.device)
            return self.model(obs_tensor, return_features=True).permute(1, 2, 0)

    def train(self, observations, epochs=5, batch_size=32, mask_prob=0.15):
        if not observations: return
        
        loader = DataLoader(self._prepare_dataset(observations), batch_size=batch_size, shuffle=True)
        self.model.train()

        for epoch in range(epochs):
            self._run_epoch(loader, mask_prob)

    def save(self, path):
        checkpoint = {
            'model_state': self.model.state_dict(),
            'params': self.params
        }
        torch.save(checkpoint, path)

    @staticmethod
    def load(path, device=None):
        device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        checkpoint = torch.load(path, map_location=device)
        
        instance = TileEncoder(**checkpoint['params'], device=device)
        instance.model.load_state_dict(checkpoint['model_state'])
        return instance

    def _run_epoch(self, loader, mask_prob):
        for batch in loader:
            batch = batch.to(self.device)
            masked_input = self._apply_mask(batch, mask_prob)
            
            self.optimizer.zero_grad()
            output = self.model(masked_input)
            
            loss = self.criterion(output, batch)
            loss.backward()
            self.optimizer.step()

    def _apply_mask(self, batch, mask_prob):
        mask = (torch.rand(batch.shape, device=self.device) < mask_prob)
        masked_batch = batch.clone()
        masked_batch[mask] = 0
        return masked_batch

    def _ensure_tensor(self, data):
        return data if isinstance(data, torch.Tensor) else torch.LongTensor(data)

    def _prepare_dataset(self, observations):
        class SimpleDataset(Dataset):
            def __init__(self, data): self.data = [torch.LongTensor(o) for o in data]
            def __len__(self): return len(self.data)
            def __getitem__(self, i): return self.data[i]
        return SimpleDataset(observations)