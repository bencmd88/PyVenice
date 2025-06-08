# CI/CD Implementation Plan for Multi-Platform Distribution

## Phase 1: Multi-Architecture Wheel Building

### Step 1: Setup GitHub Actions Workflow
```bash
mkdir -p .github/workflows
```

Create `.github/workflows/build-wheels.yml`:
```yaml
name: Build and Publish Wheels

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build wheels
      uses: pypa/cibuildwheel@v2.16.2
      env:
        CIBW_ARCHS_LINUX: "x86_64 aarch64"
        CIBW_ARCHS_MACOS: "x86_64 arm64"
        CIBW_ARCHS_WINDOWS: "AMD64 ARM64"
        CIBW_BUILD: "cp3{9,10,11,12}-*"
        CIBW_SKIP: "pp* *-musllinux*"
        CIBW_TEST_COMMAND: "python -c 'import pyvenice; print(\"OK\")'"
    
    - uses: actions/upload-artifact@v4
      with:
        name: cibw-wheels-${{ matrix.os }}-${{ strategy.job-index }}
        path: ./wheelhouse/*.whl

  build_sdist:
    name: Build source distribution
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build sdist
      run: pipx run build --sdist
    - uses: actions/upload-artifact@v4
      with:
        name: cibw-sdist
        path: dist/*.tar.gz

  upload_pypi:
    needs: [build_wheels, build_sdist]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    steps:
    - uses: actions/download-artifact@v4
      with:
        pattern: cibw-*
        path: dist
        merge-multiple: true
    
    - uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### Step 2: Configure pyproject.toml
Add to `pyproject.toml`:
```toml
[tool.cibuildwheel]
test-requires = "pytest"
test-command = "pytest {project}/tests -x"
build-verbosity = 1

[tool.cibuildwheel.linux]
before-all = "yum install -y openssl-devel libffi-devel || apt-get update && apt-get install -y libssl-dev libffi-dev"

[tool.cibuildwheel.macos]
environment = { MACOSX_DEPLOYMENT_TARGET = "11.0" }

[tool.cibuildwheel.windows]
before-build = "pip install delvewheel"
repair-wheel-command = "delvewheel repair -w {dest_dir} {wheel}"
```

### Step 3: Setup Secrets
```bash
# In GitHub repository settings > Secrets:
# PYPI_API_TOKEN - PyPI trusted publisher token
```

## Phase 2: Conda-forge Release

### Step 1: Install Dependencies
```bash
pip install grayskull
```

### Step 2: Generate Recipe
```bash
# Generate initial conda recipe
grayskull pypi pyvenice

# Review and edit meta.yaml:
# - Update maintainers section
# - Add test dependencies
# - Verify license
```

### Step 3: Submit to Conda-forge
```bash
# Fork conda-forge/staged-recipes
git clone https://github.com/YOUR_USERNAME/staged-recipes.git
cd staged-recipes

# Create recipe directory
mkdir recipes/pyvenice
cp ../pyvenice/meta.yaml recipes/pyvenice/

# Create PR to conda-forge/staged-recipes
git add recipes/pyvenice/
git commit -m "Add pyvenice package"
git push origin main
# Create PR via GitHub UI
```

### Step 4: Post-Acceptance Maintenance
```bash
# After acceptance, conda-forge creates feedstock repo
# Fork conda-forge/pyvenice-feedstock for future updates
# Updates are automatic via bot when PyPI releases
```

## Phase 3: Docker Release

### Step 1: Create Multi-Stage Dockerfile
```dockerfile
# Dockerfile
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Install PyVenice
RUN pip install --no-cache-dir pyvenice

# Production stage
FROM python:3.12-alpine

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN adduser -D -s /bin/sh pyvenice
USER pyvenice

# Verify installation
RUN python -c "import pyvenice; print('PyVenice installed successfully')"

CMD ["python"]
```

### Step 2: Create Docker Workflow
```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ghcr.io/${{ github.repository_owner }}/pyvenice
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

## Phase 4: Homebrew Release (Skip - Library Not CLI)

**Decision**: Skip Homebrew implementation. Homebrew is designed for CLI applications, not Python libraries. Users should use `pip install pyvenice` or `brew install python && pip install pyvenice`.

**Rationale**: 
- Homebrew Python formulas are complex to maintain
- Library dependencies conflict with system Python
- No significant user benefit over pip installation

## Phase 5: Snap Packages (Skip - Minimal Benefit)

**Decision**: Skip Snap implementation for Python library.

**Rationale**:
- Snap is designed for desktop applications
- Python libraries don't benefit from Snap's sandboxing
- Limited user base compared to pip/conda
- Additional maintenance overhead

## Implementation Timeline

### Week 1: Foundation
- [ ] Implement multi-arch wheel building
- [ ] Test on ARM64 devices
- [ ] Setup PyPI trusted publishing

### Week 2: Container Strategy
- [ ] Create optimized Dockerfile
- [ ] Setup GitHub Container Registry
- [ ] Test multi-platform builds

### Week 3: Conda Integration
- [ ] Generate conda recipe with grayskull
- [ ] Submit to conda-forge/staged-recipes
- [ ] Address reviewer feedback

### Week 4: Documentation & Testing
- [ ] Update installation docs
- [ ] Create distribution testing matrix
- [ ] Document maintenance procedures

## Maintenance Procedures

### Regular Tasks
1. **Monitor wheel builds** - Check CI for new Python releases
2. **Update conda recipe** - Usually automatic via conda-forge bot
3. **Security updates** - Monitor dependency CVEs
4. **Performance testing** - Verify multi-arch performance parity

### Emergency Procedures
1. **Failed builds** - Check cibuildwheel logs, update build dependencies
2. **Security incidents** - Emergency release process documented
3. **Platform deprecation** - Remove unsupported architectures gracefully

## Success Metrics

- **Coverage**: Wheels available for 95% of Python environments
- **Adoption**: Conda-forge downloads tracking
- **Performance**: Multi-arch build time < 30 minutes
- **Reliability**: < 1% build failure rate
- **Security**: Zero critical vulnerabilities in dependencies