# APX Command-Line Utilities

This directory contains standalone Python utility scripts for inspecting, formatting, transforming, and analyzing APX (AUTOSAR Port eXchange) specification files (`.apx`).

All modern utilities support UNIX pipes (`stdin` and `stdout`), allowing them to be chained together seamlessly with standard command-line tools.

---

## Utility Overview

| Utility | Description | Stdin / Stdout |
| :--- | :--- | :--- |
| [`apx_compact.py`](apx_compact.py) | Compacts APX files using index-based type references (`T[0]`, `T[1]`) | Yes (default) |
| [`apx_normalize.py`](apx_normalize.py) | Normalizes APX files with sorted elements and named type references (`T["TypeName"]`) | Yes (default) |
| [`apx_size.py`](apx_size.py) | Computes serialized binary buffer sizes (in bytes) for require (`in`) and provide (`out`) ports | Yes (default) |
| [`apx_mirror.py`](apx_mirror.py) | Inverts provide and require ports to create client/stub nodes | Yes (`-p` flag) |
| [`apx_join.py`](apx_join.py) | Merges multiple APX node definition files into a single unified APX node | File-based |

---

## Script Descriptions & Usage

### 1. `apx_compact.py`

Converts type references in an APX specification from name-based references (e.g. `T["VehicleSpeed_T"]`) to 0-based index references (e.g. `T[0]`). This reduces textual representation size and network transfer overhead.

**Syntax:**
```bash
python util/apx_compact.py [input_file] [-o OUTPUT_FILE]
```

**Options:**
- `input_file`: Path to input `.apx` file, or `-` for `stdin` (default: `-`).
- `-o`, `--output`: Path to output file. Defaults to `stdout` when reading from `stdin`, or overwrites the input file in-place if an input file is provided.

**Examples:**
```bash
# Compact a file in-place
python util/apx_compact.py node.apx

# Compact a file and save to a new file
python util/apx_compact.py node.apx -o node_compact.apx

# Read from stdin, write to stdout
cat node.apx | python util/apx_compact.py > node_compact.apx
```

---

### 2. `apx_normalize.py`

Normalizes an APX specification into a canonical, human-readable format. Elements (data types, provide ports, require ports) are sorted alphabetically by name, and all type references are converted to explicit name-based references (e.g. `T["EngineSpeed_T"]`).

**Syntax:**
```bash
python util/apx_normalize.py [input_file] [-o OUTPUT_FILE]
```

**Options:**
- `input_file`: Path to input `.apx` file, or `-` for `stdin` (default: `-`).
- `-o`, `--output`: Path to output file. Defaults to `stdout` when reading from `stdin`, or overwrites the input file in-place if an input file is provided.

**Examples:**
```bash
# Normalize a file in-place
python util/apx_normalize.py node.apx

# Normalize a compact APX stream from stdin
python util/apx_normalize.py < node_compact.apx > node_normalized.apx
```

---

### 3. `apx_size.py`

Parses an APX specification and compiles its port data elements via the APX Virtual Machine compiler to calculate the exact serialized binary buffer memory sizes needed for runtime communication:
- `in`: Total byte size of require ports (unpacked from network/RTE buffers).
- `out`: Total byte size of provide ports (packed into network/RTE buffers).

**Syntax:**
```bash
python util/apx_size.py [input_file]
```

**Output format:**
```text
in:	<bytes>	out:	<bytes>
```

**Examples:**
```bash
# Calculate buffer size of a file
python util/apx_size.py node.apx

# Calculate buffer size from standard input
cat node.apx | python util/apx_size.py
```

---

### 4. `apx_mirror.py`

Generates a complementary "mirror" node where all provide ports become require ports and all require ports become provide ports. This is useful for creating virtual test harnesses, simulation nodes, or client-side counterparts.

**Syntax:**
```bash
python util/apx_mirror.py [input_file] [-o OUTPUT_FILE] [-n NAME] [-m] [-p]
```

**Options:**
- `input_file`: Input APX file path.
- `-o OUTPUT_FILE`: Output file path (default: overwrite input file).
- `-n`, `--name`: New name for the mirrored APX node.
- `-m`, `--normalize`: Output in normalized format.
- `-p`, `--pipe`: Read from `stdin` and output to `stdout`.

**Examples:**
```bash
# Mirror a node file and rename it
python util/apx_mirror.py server.apx -o client.apx -n "ClientNode"

# Stream mirrored output through pipe
cat server.apx | python util/apx_mirror.py -p -n "TestClient" > client.apx
```

---

### 5. `apx_join.py`

Merges multiple APX specification files into a single consolidated APX node definition.

**Syntax:**
```bash
python util/apx_join.py input_files... -n NAME [--sort] [--normalize]
```

**Options:**
- `input_files`: One or more APX file paths to merge.
- `-n`, `--name`: Name of the new merged APX node (required).
- `--sort`: Sort types and ports in the merged node.
- `--normalize`: Generate normalized APX output.

**Examples:**
```bash
python util/apx_join.py -n "CompositeECU" engine.apx transmission.apx brakes.apx --sort --normalize
```

---

## UNIX Pipeline Examples

Because the utilities support reading from `stdin` and writing to `stdout`, they can be combined with each other and standard UNIX utilities in various workflows:

### 1. Inspection and Buffer Size Calculation on the Fly

Stream an APX file or network response through the size analyzer without creating temporary files:

```bash
cat component.apx | python util/apx_size.py
```

Or from a remote URL:

```bash
curl -s https://example.com/specs/Node.apx | python util/apx_size.py
```

### 2. Format Chaining (Compact &rarr; Normalize &rarr; View)

Transform a compact representation back to canonical normalized form and view it with `less` or `head`:

```bash
cat compact_node.apx | python util/apx_normalize.py | less
```

### 3. Mirroring and Compacting in a Single Pipeline

Generate a client node from a server specification, compact it, and write to a destination file in one line:

```bash
python util/apx_mirror.py server.apx -p -n "ClientNode" | python util/apx_compact.py > client_compact.apx
```

### 4. Mirroring and Calculating Client I/O Footprint

Quickly verify that a mirrored node's input size matches the original node's output size:

```bash
echo "=== Server Buffer Sizes ==="
python util/apx_size.py server.apx

echo "=== Client (Mirrored) Buffer Sizes ==="
cat server.apx | python util/apx_mirror.py -p | python util/apx_size.py
```

### 5. Canonical Comparison with `diff` and Git

Normalize two APX files on the fly before diffing to ignore type order and reference formatting differences:

```bash
diff -u <(python util/apx_normalize.py node_v1.apx -o -) \
        <(python util/apx_normalize.py node_v2.apx -o -)
```

Or diff a Git revision against your working copy:

```bash
git show HEAD:src/node.apx | python util/apx_normalize.py | diff -u - <(python util/apx_normalize.py src/node.apx -o -)
```

### 6. Batch Processing and Formatting with Shell Loops

Calculate buffer sizes for all `.apx` files in a project:

```bash
for file in specs/*.apx; do
    echo -n "$file -> "
    python util/apx_size.py "$file"
done
```

Normalize all APX files across a directory tree:

```bash
find . -name "*.apx" -exec python util/apx_normalize.py {} +
```
