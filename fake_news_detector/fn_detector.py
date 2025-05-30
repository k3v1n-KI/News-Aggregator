import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertTokenizerFast
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from utilities import get_content

# Define the same model architecture to load trained weights
torch_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class RNNClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=100, hidden_dim=128, output_dim=2,
                 num_layers=2, bidirectional=True, dropout=0.5, pad_idx=0):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.rnn = nn.LSTM(embed_dim,
                           hidden_dim,
                           num_layers=num_layers,
                           batch_first=True,
                           bidirectional=bidirectional,
                           dropout=dropout if num_layers > 1 else 0)
        factor = 2 if bidirectional else 1
        self.fc = nn.Linear(hidden_dim * factor, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, text, lengths):
        embedded = self.dropout(self.embedding(text))
        packed = nn.utils.rnn.pack_padded_sequence(embedded,
                                                   lengths.cpu(),
                                                   batch_first=True,
                                                   enforce_sorted=False)
        _, (hidden, _) = self.rnn(packed)
        if self.rnn.bidirectional:
            hidden = torch.cat((hidden[-2], hidden[-1]), dim=1)
        else:
            hidden = hidden[-1]
        return self.fc(self.dropout(hidden))

class FakeNewsDetector:
    def __init__(self,
                 model_path: str = 'models/fake_news_rnn_model.pth',
                 tokenizer_dir: str = 'models/tokenizer',
                 device: torch.device = None):
        # Device setup
        self.device = device or torch_device
        # Load tokenizer and stop words
        self.tokenizer = BertTokenizerFast.from_pretrained(tokenizer_dir)
        self.stop_words = set(ENGLISH_STOP_WORDS)
        # Initialize and load model
        pad_idx = self.tokenizer.pad_token_id
        self.model = RNNClassifier(
            vocab_size=self.tokenizer.vocab_size,
            pad_idx=pad_idx
        )
        state = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

    def preprocess(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def encode(self, text: str) -> (torch.Tensor, torch.Tensor):
        # Clean and tokenize
        cleaned = self.preprocess(text)
        tokens = self.tokenizer.tokenize(cleaned)
        # Remove stop words
        tokens = [tok for tok in tokens if tok not in self.stop_words]
        
        # Truncate if too long (to prevent OOM or timeout)
        MAX_LEN = 512
        if len(tokens) > MAX_LEN:
            tokens = tokens[:MAX_LEN]

        # Convert to IDs, ensure at least one token
        ids = self.tokenizer.convert_tokens_to_ids(tokens)
        if len(ids) == 0:
            ids = [self.tokenizer.unk_token_id]
        tensor = torch.tensor(ids, dtype=torch.long, device=self.device).unsqueeze(0)
        lengths = torch.tensor([tensor.size(1)], dtype=torch.long, device=self.device)
        return tensor, lengths


    def predict(self, text: str, is_content=True) -> dict:
        if not is_content:
            text = get_content(text)
        if not text or len(text.strip()) == 0:
            return {'prediction': -1, 'confidence': 0.0}

        tensor, lengths = self.encode(text)
        if tensor is None or lengths[0].item() == 0:
            return {'prediction': -1, 'confidence': 0.0}

        with torch.no_grad():
            logits = self.model(tensor, lengths)
            probs = F.softmax(logits, dim=1).cpu().numpy()[0]
            pred = int(probs.argmax())
            confidence = round(float(probs[pred]), 2)

        return {'prediction': pred, 'confidence': confidence * 100}


