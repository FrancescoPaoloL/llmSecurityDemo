## Build Strategy

This project uses **single-stage** build with precompiled binaries.

**Pros:**
- Fast builds (~1min rebuild vs 5min from source)
- Simple Docker setup
- Layer caching optimization

**Cons:**
- Platform-specific binaries (requires compatible CPU architecture)
- Manual rebuild required for code changes

For reproducible builds, consider multi-stage in the future.

## Build Environment

Binaries compiled on:
- **OS**: Debian 12 (Bookworm)
- **CPU**: Intel i5-12400 (Alder Lake)
- **Compiler**: GCC 12.2.0
- **Build script**: `llama.cpp/build-owasp.sh`

### Compiler Flags
```bash
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-O3" \
  -DCMAKE_CXX_FLAGS="-O3" \
  -DGGML_AVX2=ON \
  -DGGML_FMA=ON \
  -DGGML_OPENMP=ON \
  -DBUILD_SHARED_LIBS=ON
```

**Note**: Generic x86_64 optimization (no `-march=native`) for Azure cross-platform compatibility. Supports Intel/AMD CPUs with AVX2 instruction set.

### Platform Compatibility

**Issue discovered**: Initial build with `-march=native` crashed on Azure Container Instances (AMD EPYC) when compiled on Intel i5-12400.

**Solution**: Generic optimization flags ensure binaries work on both Intel and AMD x86_64 processors.

**Trade-off**: ~5-10% performance loss vs build-machine-specific optimization, but deployment reliability gained.

