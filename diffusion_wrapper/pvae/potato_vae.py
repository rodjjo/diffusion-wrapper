import torch.nn as nn
import torch.nn.functional as F


class PotatoVae(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super(PotatoVae, self).__init__()


def new_qvae_model():
    return PotatoVae(
        num_hiddens=240, 
        num_residual_hiddens=384, 
        embedding_dim=256,
        n_codebooks=1, 
        codes_per_book=1024,
        commitment_cost=0.25, 
        decay=0.99,
        attn_n_heads=2, 
        use_attn=True,
        num_residual_layers=4,
        downsample=(4, 4, 4)
    )


##### 

