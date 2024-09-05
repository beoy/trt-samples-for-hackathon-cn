import time
import tripy as tp

class MLP(tp.Module):

    def __init__(self, embedding_size, dtype=tp.float32):
        super().__init__()
        self.c_fc = tp.Linear(embedding_size, 4 * embedding_size, bias=True, dtype=dtype)
        self.c_proj = tp.Linear(4 * embedding_size, embedding_size, bias=True, dtype=dtype)

    def __call__(self, x):
        x = self.c_fc(x)
        x = tp.gelu(x)
        x = self.c_proj(x)
        return x

mlp = MLP(embedding_size=2)

inp = tp.iota(shape=(1, 2), dim=1, dtype=tp.float32)

out = mlp(inp)

compiler = tp.Compiler(mlp)

# When we compile, we need to indicate which parameters to the function should be runtime inputs.

# In this case, MLP takes a single input tensor for which we can specify our desired shape and datatype.

fast_mlp = compiler.compile(tp.InputInfo(shape=(1, 2), dtype=tp.float32))

ITERS = 10

start = time.time()
for _ in range(ITERS):
    out = mlp(inp)
    out.eval()  # Recall that we need to evaluate in order to actually materialize `out`

end = time.time()

eager_time = (end - start) / ITERS
print(f"Eager mode average time: {eager_time:.4f} seconds")

start = time.time()
for _ in range(ITERS):
    out = fast_mlp(inp)
    out.eval()

end = time.time()

compiled_time = (end - start) / ITERS
print(f"Compiled mode average time: {(end - start) / ITERS:.4f} seconds")
