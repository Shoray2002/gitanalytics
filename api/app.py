import json
from flask import Flask, Response, request, jsonify
import re
import requests
import os
import tempfile
from git import Repo
from nbconvert.exporters import PythonExporter
import openai
import nbformat
import tiktoken
from itertools import islice
import numpy as np


EMBEDDING_CTX_LENGTH = 2048
EMBEDDING_ENCODING = "cl100k_base"


non_code_extensions = (
    ".md",  # Markdown files
    ".txt",  # Text files
    ".csv",  # Comma-separated values
    ".json",  # JSON files
    ".yml",  # YAML files
    ".yaml",  # YAML files
    ".xml",  # XML files
    ".ini",  # Configuration files
    ".cfg",  # Configuration files
    ".conf",  # Configuration files
    ".properties",  # Java properties files
    ".log",  # Log files
    ".gitignore",  # Git ignore rules
    ".editorconfig",  # Editor configuration files
    ".dockerignore",  # Docker ignore rules
    ".prettierignore",  # Prettier ignore rules
    ".prettierrc",  # Prettier configuration files
    ".eslintrc",  # ESLint configuration files
    ".eslintignore",  # ESLint ignore rules
    ".stylelintrc",  # Stylelint configuration files
    ".stylelintignore",  # Stylelint ignore rules
    ".npmignore",  # NPM ignore rules
    ".npmrc",  # NPM configuration files
    ".lock",  # Dependency lock files
    ".LICENSE",  # License files
    ".license",  # License files
    ".LICENSE-MIT",  # MIT License files
    ".LICENSE-APACHE",  # Apache License files
    ".gitmodules",  # Git submodule configuration files
    ".gitattributes",  # Git attribute files
    ".gitconfig",  # Git configuration files
    ".rst",  # reStructuredText files
    ".pdf",  # Portable Document Format files
    ".ppt",  # PowerPoint presentation files
    ".pptx",  # PowerPoint presentation files (XML-based)
    ".doc",  # Word document files
    ".docx",  # Word document files (XML-based)
    ".xls",  # Excel spreadsheet files
    ".xlsx",  # Excel spreadsheet files (XML-based)
    ".rtf",  # Rich Text Format files
    ".jpg",  # JPEG image files
    ".jpeg",  # JPEG image files
    ".png",  # PNG image files
    ".gif",  # GIF image files
    ".bmp",  # Bitmap image files
    ".ico",  # Icon files
    ".svg",  # Scalable Vector Graphics files
    ".psd",  # Adobe Photoshop files
    ".ai",  # Adobe Illustrator files
    ".eps",  # Encapsulated PostScript files
    ".tif",  # TIFF image files
    ".tiff",  # TIFF image files
    ".zip",  # ZIP archive files
    ".tar",  # TAR archive files
    ".gz",  # GZIP archive files
    ".bz2",  # BZIP2 archive files
    ".7z",  # 7-Zip archive files
    ".rar",  # RAR archive files
    ".iso",  # ISO image files
    ".img",  # Disk image files
    ".bin",  # Binary files
    ".dat",  # Data files
    ".bak",  # Backup files
    ".tmp",  # Temporary files
    ".swp",  # Swap files
    ".swo",  # Swap files
    ".readme",  # Readme files
    ".changelog",  # Changelog files
    ".changes",  # Changelog files
    ".news",  # Changelog files
    ".asciidoc",  # AsciiDoc files
    ".adoc",  # AsciiDoc files
    ".dtd",  # Document Type Definition files
    ".xsd",  # XML Schema Definition files
    ".plist",  # Property List files
    ".toml",  # TOML files
    ".tsv",  # Tab-separated values files
    ".ods",  # OpenDocument Spreadsheet files
    ".odt",  # OpenDocument Text files
    ".ott",  # OpenDocument Text Template files
    ".odp",  # OpenDocument Presentation files
    ".otp",  # OpenDocument Presentation Template files
    ".odg",  # OpenDocument Graphics files
    ".otg",  # OpenDocument Graphics Template files
    ".notebook",  # Jupyter Notebook files
    ".mdx",  # Markdown Extra files
    ".tex",  # LaTeX files
    ".bib",  # BibTeX files
    ".cls",  # LaTeX class files
    ".sty",  # LaTeX style files
    ".vtt",  # WebVTT files
    ".srt",  # SubRip subtitle files
    ".sbv",  # YouTube caption files
    ".ass",  # Advanced SubStation Alpha subtitle files
    ".ssa",  # SubStation Alpha subtitle files
    ".ics",  # iCalendar files
    ".ifb",  # iCalendar free/busy time files
    ".ical",  # iCalendar files
    ".icalendar",  # iCalendar files
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".svg",
    ".ipynb",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".eot",
    ".pfa",
    ".pfb",
    ".afm",
    ".pfm",
    ".fon",
    ".fnt",
    ".svg",
    ".sfd",
    ".3ds",  # 3D Studio Max files
    ".obj",  # Wavefront Object files
    ".fbx",  # Autodesk FBX files
    ".dae",  # COLLADA files
    ".stl",  # Stereolithography files
    ".ply",  # Polygon File Format (Stanford Triangle Format)
    ".blend",  # Blender files
    ".max",  # 3D Studio Max files
    ".ma",  # Maya ASCII files
    ".mb",  # Maya Binary files
    ".c4d",  # Cinema 4D files
    ".lwo",  # LightWave Object files
    ".lw",  # LightWave files
    ".lws",  # LightWave Scene files
    ".ase",  # ASCII Scene Export files
    ".x",  # DirectX files
    ".gltf",  # GL Transmission Format files
    ".glb",  # Binary GL Transmission Format files
    ".vox",  # MagicaVoxel files
    ".step",  # STEP files
    ".stp",  # STEP files
    ".iges",  # IGES files
    ".igs",  # IGES files
    ".vrml",  # VRML files
    ".wrl",  # VRML files
    ".x3d",  # X3D files
    ".x3db",  # X3D Binary files
    ".x3dv",  # X3D Classic VRML files
)

app = Flask(__name__)


def batched(iterable, n):
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def chunked_tokens(text, encoding_name, chunk_length):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = batched(tokens, chunk_length)
    yield from chunks_iterator


def len_safe_get_embedding(
    text,
    max_tokens=EMBEDDING_CTX_LENGTH,
    encoding_name=EMBEDDING_ENCODING,
):
    chunks = []
    for chunk in chunked_tokens(
        text, encoding_name=encoding_name, chunk_length=max_tokens
    ):
        chunks.append(chunk)
    return chunks


# routes
@app.route("/analyze", methods=["GET"])
def analyze():
    print("analyze")
    github_url = request.args.get("username")
    # results_generator = analyze_repositories(github_url)
    return analyze_repositories(github_url), {"Content-Type": "application/x-ndjson"}


def generate_json():
    data = [{"id": i, "value": f"Item {i + 1}"} for i in range(10)]
    for item in data:
        item = json.dumps(item)
        item = "".join([item, "\n"])
        yield item


def fetch_repositories(github_url):
    username = github_url.split("/")[-1]
    api_url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Failed to fetch repositories for user {username}: {response.text}"
        )


def preprocess_code(repo_url):
    repo_name = repo_url.split("/")[-1].split(".")[0]
    temp_dir = tempfile.mkdtemp()
    local_path = os.path.join(temp_dir, repo_name)

    # Clone the repository
    Repo.clone_from(repo_url, local_path)
    print(f"Cloned repository {repo_url} to {local_path}")

    # Convert Jupyter notebooks to Python scripts
    exporter = PythonExporter()
    for root, dirs, files in os.walk(local_path):
        # Ignore node_modules and directories starting with .
        dirs[:] = [
            d
            for d in dirs
            if not (
                d.startswith(".")
                or d == "node_modules"
                or d == "venv"
                or d == "env"
                or d == "virtualenv"
                or d == "assets"
                or d == "static"
                or d == "build"
                or d == "dist"
                or d == "target"
            )
        ]

        for file in files:
            if file.endswith(".ipynb"):
                file_path = os.path.join(root, file)
                with open(file_path) as f:
                    nb_node = nbformat.read(f, as_version=4)
                script, _ = exporter.from_notebook_node(nb_node)
                with open(file_path.replace(".ipynb", ".py"), "w") as f:
                    f.write(script)

    # Read all code files and concatenate their content
    code = ""
    for root, dirs, files in os.walk(local_path):
        # Ignore node_modules and directories starting with .
        dirs[:] = [
            d
            for d in dirs
            if not (
                d.startswith(".")
                or d == "node_modules"
                or d == "venv"
                or d == "env"
                or d == "virtualenv"
                or d == "assets"
                or d == "static"
                or d == "build"
                or d == "dist"
                or d == "target"
            )
        ]

        for file in files:
            file_path = os.path.join(root, file)
            # Ignore asset files like images and SVGs
            if (
                not file.lower().endswith(non_code_extensions)
                and not file.startswith(".")
                and file
                not in [
                    "LICENSE",
                    "license",
                ]
                and not is_binary(file_path)
            ):
                print("Reading file:", file_path)
                with open(file_path) as f:
                    code += f"File: {file}\n"
                    code += f.read().strip() + "\n"
    chunks = divide_into_chunks(code)
    return chunks


def divide_into_chunks(code):
    chunks = len_safe_get_embedding(text=code)
    print("Divided code into", len(chunks), "chunks")
    return chunks


def analyze_code_with_gpt(code_chunks):
    openai.api_key = "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"
    total_complexity = 0
    analyzed_chunks = 0
    # Analyze each code chunk
    for i, code_chunk in enumerate(code_chunks):
        print("Analyzing code chunk: ", i + 1, " out of ", len(code_chunks))
        print("Size of code chunk: ", len(code_chunk))
        enc = tiktoken.get_encoding(EMBEDDING_ENCODING)
        chunk_text = enc.decode(code_chunk)
        prompt = f"{chunk_text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Your job is to rate the technical complexity of the code given by the user on a scale of 1 to 10 and only respond with a number and no extra text whatsoever. Never ever return a statement like 'I don't know' or 'I can't rate this' becaause of error or any other reason. In case of error, just return the number 0.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        try:
            print(response.choices[0].message["content"])
            nums = [
                int(num)
                for num in re.findall(r"\d+", response.choices[0].message["content"])
            ]
            rating = float(nums[0])
            total_complexity += rating
            analyzed_chunks += 1
        except ValueError:
            pass
    if analyzed_chunks > 0:
        return total_complexity / analyzed_chunks
    else:
        return None


def analyze_repositories(github_url):
    repos = fetch_repositories(github_url)
    max_complexity = -1
    most_complex_repo = None
    gpt_analysis = ""

    for repo in repos:
        print("Analyzing repository: ", repo["name"])
        repo_url = repo["html_url"]
        code_chunks = preprocess_code(repo_url)
        print(len(code_chunks), " code chunks found")
        complexity = analyze_code_with_gpt(code_chunks)
        print("Complexity score of ", repo["name"], ": ", complexity)

        if complexity is not None and complexity > max_complexity:
            max_complexity = complexity
            most_complex_repo = repo
            gpt_analysis = str(round(complexity, 2))

        yield json.dumps({"repository": repo["html_url"], "complexity": complexity})

    yield json.dumps(
        {
            "most_complex_repository": most_complex_repo["html_url"],
            "gpt_analysis": gpt_analysis,
        }
    )


def is_binary(file_path):
    with open(file_path, "rb") as f:
        for _ in range(1024):
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
    return False


if __name__ == "__main__":
    app.run(debug=True)
